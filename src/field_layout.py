from __future__ import annotations

from ralf_model.nodes import FieldNode
from ralf_model.parse import _parse_int_literal  # noqa: SLF001 — 与解析器共享字面量语义


def verilog_int_token(tok: str) -> int:
    s = tok.strip()
    if not s:
        raise ValueError("empty integer")
    v, end = _parse_int_literal(s, 0)
    if end != len(s):
        raise ValueError(f"unsupported int literal: {tok!r}")
    return int(v)


def field_bits_width(f: FieldNode) -> int:
    for stmt in f.inner_statements:
        st = stmt.strip()
        if not st.lower().startswith("bits"):
            continue
        rest = st[4:].strip().rstrip(";").strip()
        compact = rest.replace(" ", "")
        return verilog_int_token(compact)
    return 1


def field_lsbs(fields: list[FieldNode]) -> list[int]:
    """计算每位字段最低位：显式 `@` 优先；否则自上一隐式结束位置连续排列。"""
    implicit_next = 0
    lsbs: list[int] = []
    for f in fields:
        w = field_bits_width(f)
        if f.offset_bits is not None:
            lsb = f.offset_bits
            implicit_next = max(implicit_next, lsb + w)
        else:
            lsb = implicit_next
            implicit_next = lsb + w
        lsbs.append(lsb)
    return lsbs
