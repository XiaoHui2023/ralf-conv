from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ralf_model.nodes import BlockNode, RalfDocument, RegisterNode, SystemNode

from .field_layout import field_bits_width, field_lsbs
from .flatten import FieldFlat


def _register_size_bits(reg: RegisterNode) -> int:
    """寄存器位宽：优先 `bytes N`；否则按字段覆盖的最高位向上取整字节再转位。"""
    if reg.bytes_width is not None and reg.bytes_width > 0:
        return reg.bytes_width * 8
    if not reg.fields:
        return 8
    lsbs = field_lsbs(reg.fields)
    tops = [lsbs[i] + field_bits_width(reg.fields[i]) for i in range(len(reg.fields))]
    max_bit = max(tops)
    return ((max_bit + 7) // 8) * 8


@dataclass
class RegisterHier:
    """层次模型中的寄存器；JSON 映射对齐 IP-XACT（spirit:register / spirit:field 常用项）。"""

    name: str
    offset_bytes: int | None
    address: int
    size_bits: int
    fields: list[FieldFlat] = field(default_factory=list)
    hdl_path: str | None = None

    def as_mapping(self) -> dict[str, Any]:
        off = 0 if self.offset_bytes is None else self.offset_bytes
        fields_json: list[dict[str, Any]] = []
        for ff in self.fields:
            fd: dict[str, Any] = {
                "name": ff.name,
                "bitOffset": ff.lsb,
                "bitWidth": ff.width,
            }
            if ff.hdl_path is not None:
                fd["hdlPath"] = ff.hdl_path
            fields_json.append(fd)
        m: dict[str, Any] = {
            "name": self.name,
            "addressOffset": off,
            "size": self.size_bits,
            "absoluteAddress": self.address,
            "fields": fields_json,
        }
        if self.hdl_path is not None:
            m["hdlPath"] = self.hdl_path
        return m


@dataclass
class SystemHier:
    """保留 RALF system 嵌套；体内可含子 system 与 block。"""

    name: str
    path: str
    base_address: int
    systems: list[SystemHier] = field(default_factory=list)
    blocks: list[BlockHier] = field(default_factory=list)

    def as_mapping(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "path": self.path,
            "baseAddress": self.base_address,
            "addressUnitBits": 8,
            "systems": [s.as_mapping() for s in self.systems],
            "addressBlocks": [b.as_mapping() for b in self.blocks],
        }


@dataclass
class BlockHier:
    """保留 RALF block 嵌套；JSON 键与 IP-XACT addressBlock / 寄存器树常见命名兼容。"""

    name: str
    path: str
    base_address: int
    blocks: list[BlockHier] = field(default_factory=list)
    registers: list[RegisterHier] = field(default_factory=list)

    def as_mapping(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "path": self.path,
            "baseAddress": self.base_address,
            "addressUnitBits": 8,
            "addressBlocks": [b.as_mapping() for b in self.blocks],
            "registers": [r.as_mapping() for r in self.registers],
        }


def document_to_block_forest(
    doc: RalfDocument,
    *,
    base_offset: int = 0,
) -> list[SystemHier | BlockHier]:
    """按 system / block 树输出：顶层为文档根级列表，内含嵌套与 registers（含 fields）。

    Args:
        base_offset: 加到所有基址与寄存器绝对地址上的整体偏移。
    """
    out: list[SystemHier | BlockHier] = [
        _system_subtree(s, prefix=(), ancestor_base=base_offset) for s in doc.systems
    ]
    out.extend(
        _block_subtree(b, prefix=(), ancestor_base=base_offset) for b in doc.blocks
    )
    return out


def _system_subtree(
    system: SystemNode,
    *,
    prefix: tuple[str, ...],
    ancestor_base: int,
) -> SystemHier:
    scope = prefix + (system.name,)
    path_str = ".".join(scope)
    my_base = ancestor_base + (system.base_address or 0)
    systems_out = [
        _system_subtree(sub, prefix=scope, ancestor_base=my_base)
        for sub in system.systems
    ]
    blocks_out = [
        _block_subtree(sub, prefix=scope, ancestor_base=my_base)
        for sub in system.blocks
    ]
    return SystemHier(
        name=system.name,
        path=path_str,
        base_address=my_base,
        systems=systems_out,
        blocks=blocks_out,
    )


def _block_subtree(
    block: BlockNode,
    *,
    prefix: tuple[str, ...],
    ancestor_base: int,
) -> BlockHier:
    scope = prefix + (block.name,)
    path_str = ".".join(scope)
    my_base = ancestor_base + (block.base_address or 0)

    registers_out: list[RegisterHier] = []
    for reg in block.registers:
        if reg.declaration_only:
            continue
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
        registers_out.append(
            RegisterHier(
                name=reg.name,
                offset_bytes=reg.offset_bytes,
                address=addr,
                size_bits=_register_size_bits(reg),
                fields=fields_out,
                hdl_path=reg.paren_path,
            )
        )

    blocks_out = [
        _block_subtree(sub, prefix=scope, ancestor_base=my_base) for sub in block.blocks
    ]
    return BlockHier(
        name=block.name,
        path=path_str,
        base_address=my_base,
        blocks=blocks_out,
        registers=registers_out,
    )
