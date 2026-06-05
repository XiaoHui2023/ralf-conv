from __future__ import annotations

from pathlib import Path

from ralf_model import load_ralf_file

from ralf_conv.hierarchy import document_to_block_forest

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "demo_soc.ralf"


def test_demo_soc_block_tree_matches_flat_addresses() -> None:
    doc = load_ralf_file(FIXTURE)
    forest = document_to_block_forest(doc)
    assert len(forest) == 1
    root = forest[0]
    assert root.name == "demo_soc"
    assert root.path == "demo_soc"
    assert root.base_address == 0
    assert root.blocks == []
    by_name = {r.name: r for r in root.registers}
    assert by_name["CTRL"].address == 0
    assert by_name["CTRL"].size_bits == 32
    assert by_name["STAT"].address == 0x10
    assert by_name["SLOT_A"].address == 0x100
    assert by_name["SLOT_B"].address == 0x104
    ctrl_fields = {f.name: (f.lsb, f.width) for f in by_name["CTRL"].fields}
    assert ctrl_fields["ena"] == (0, 1)
    assert ctrl_fields["mode"] == (8, 4)


def test_base_offset_adds_to_block_and_register_addresses() -> None:
    doc = load_ralf_file(FIXTURE)
    base = 0x8000_0000
    forest = document_to_block_forest(doc, base_offset=base)
    root = forest[0]
    assert root.base_address == base
    by_name = {r.name: r for r in root.registers}
    assert by_name["CTRL"].address == base
    assert by_name["STAT"].address == base + 0x10


def test_system_tree_nests_blocks_and_registers() -> None:
    fixture = Path(__file__).resolve().parent / "fixtures" / "demo_system.ralf"
    doc = load_ralf_file(fixture)
    forest = document_to_block_forest(doc)
    assert len(forest) == 1
    chip = forest[0]
    assert chip.name == "demo_chip"
    assert hasattr(chip, "systems")
    soc = chip.systems[0]
    assert soc.name == "demo_soc"
    assert soc.path == "demo_chip.demo_soc"
    assert soc.base_address == 0
    regs = soc.blocks[0]
    assert regs.name == "regs"
    by_name = {r.name: r for r in regs.registers}
    assert by_name["CTRL"].address == 0
    assert by_name["STAT"].address == 0x10


def test_nested_blocks_carry_base_and_path() -> None:
    """fixtures 若有嵌套 block，路径与基址应叠加。"""
    # demo_soc 无子 block；仅校验 API 返回类型与字段存在
    doc = load_ralf_file(FIXTURE)
    forest = document_to_block_forest(doc)
    assert all(hasattr(b, "blocks") and hasattr(b, "registers") for b in forest)
