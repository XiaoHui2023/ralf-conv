from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ralf_model.nodes import BlockNode, RalfDocument, SystemNode

from .field_layout import field_bits_width, field_lsbs


@dataclass
class FieldFlat:
    name: str
    lsb: int
    width: int
    hdl_path: str | None = None

    def as_mapping(self) -> dict[str, Any]:
        m: dict[str, Any] = {"name": self.name, "lsb": self.lsb, "width": self.width}
        if self.hdl_path is not None:
            m["hdlPath"] = self.hdl_path
        return m


@dataclass
class RegisterFlat:
    path: str
    address: int
    fields: list[FieldFlat] = field(default_factory=list)
    hdl_path: str | None = None

    def as_mapping(self) -> dict[str, Any]:
        m: dict[str, Any] = {
            "path": self.path,
            "address": self.address,
            "fields": [ff.as_mapping() for ff in self.fields],
        }
        if self.hdl_path is not None:
            m["hdlPath"] = self.hdl_path
        return m


def document_to_register_list(
    doc: RalfDocument,
    *,
    base_offset: int = 0,
) -> list[RegisterFlat]:
    """将 `ralf_model` 文档树展开为扁平寄存器列表（层次路径 + 绝对字节地址 + 字段）。

    Args:
        base_offset: 加到所有绝对字节地址上的整体基址偏移。
    """
    out: list[RegisterFlat] = []
    for root in doc.systems:
        _walk_system(root, prefix=(), ancestor_base=base_offset, acc=out)
    for root in doc.blocks:
        _walk_block(root, prefix=(), ancestor_base=base_offset, acc=out)
    return out


def _walk_system(
    system: SystemNode,
    *,
    prefix: tuple[str, ...],
    ancestor_base: int,
    acc: list[RegisterFlat],
) -> None:
    scope = prefix + (system.name,)
    my_base = ancestor_base + (system.base_address or 0)
    for sub in system.systems:
        _walk_system(sub, prefix=scope, ancestor_base=my_base, acc=acc)
    for block in system.blocks:
        _walk_block(block, prefix=scope, ancestor_base=my_base, acc=acc)


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
        lsbs = field_lsbs(reg.fields)
        fields_out = [
            FieldFlat(
                name=f.name,
                lsb=lsbs[i],
                width=field_bits_width(f),
                hdl_path=f.paren_path,
            )
            for i, f in enumerate(reg.fields)
        ]
        acc.append(
            RegisterFlat(
                path=path_str,
                address=addr,
                fields=fields_out,
                hdl_path=reg.paren_path,
            )
        )

    for sub in block.blocks:
        _walk_block(sub, prefix=scope, ancestor_base=my_base, acc=acc)
