from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ralf_model.nodes import BlockNode, FieldNode, RalfDocument
from ralf_model.parse import _parse_int_literal  # noqa: SLF001 — 与解析器共享字面量语义


def _verilog_int_token(tok: str) -> int:
    s = tok.strip()
    if not s:
        raise ValueError("empty integer")
    v, end = _parse_int_literal(s, 0)
    if end != len(s):
        raise ValueError(f"unsupported int literal: {tok!r}")
    return int(v)


def _field_bits_width(f: FieldNode) -> int:
    for stmt in f.inner_statements:
        st = stmt.strip()
        if not st.lower().startswith("bits"):
            continue
        rest = st[4:].strip().rstrip(";").strip()
        compact = rest.replace(" ", "")
        return _verilog_int_token(compact)
    return 1


def _field_lsbs(fields: list[FieldNode]) -> list[int]:
    """计算每位字段最低位：显式 `@` 优先；否则自上一隐式结束位置连续排列。"""
    implicit_next = 0
    lsbs: list[int] = []
    for f in fields:
        w = _field_bits_width(f)
        if f.offset_bits is not None:
            lsb = f.offset_bits
            implicit_next = max(implicit_next, lsb + w)
        else:
            lsb = implicit_next
            implicit_next = lsb + w
        lsbs.append(lsb)
    return lsbs


@dataclass
class FieldFlat:
    名字: str
    最低位: int
    位宽: int


@dataclass
class RegisterFlat:
    路径: str
    地址: int
    fields: list[FieldFlat] = field(default_factory=list)

    def as_mapping(self) -> dict[str, Any]:
        return {
            "路径": self.路径,
            "地址": self.地址,
            "fields": [
                {"名字": ff.名字, "最低位": ff.最低位, "位宽": ff.位宽} for ff in self.fields
            ],
        }


def document_to_register_list(doc: RalfDocument) -> list[RegisterFlat]:
    """将 `ralf_model` 文档树展开为扁平寄存器列表（层次路径 + 绝对字节地址 + 字段）。"""
    out: list[RegisterFlat] = []
    for root in doc.blocks:
        _walk_block(root, prefix=(), ancestor_base=0, acc=out)
    return out


def _walk_block(
    block: BlockNode,
    *,
    prefix: tuple[str, ...],
    ancestor_base: int,
    acc: list[RegisterFlat],
) -> None:
    scope = prefix + (block.name,)
    my_base = ancestor_base + (block.base_address or 0)

    for reg in block.registers:
        if reg.declaration_only:
            continue
        path_str = ".".join((*scope, reg.name))
        addr = my_base + (reg.offset_bytes or 0)
        lsbs = _field_lsbs(reg.fields)
        fields_out = [
            FieldFlat(
                名字=f.name,
                最低位=lsbs[i],
                位宽=_field_bits_width(f),
            )
            for i, f in enumerate(reg.fields)
        ]
        acc.append(RegisterFlat(路径=path_str, 地址=addr, fields=fields_out))

    for sub in block.blocks:
        _walk_block(sub, prefix=scope, ancestor_base=my_base, acc=acc)
