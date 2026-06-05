from __future__ import annotations

from pathlib import Path

from ralf_model import load_ralf_file

from ralf_conv.flatten import document_to_register_list

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "demo_soc.ralf"


def test_demo_soc_flatten_addresses_and_paths() -> None:
    doc = load_ralf_file(FIXTURE)
    rows = document_to_register_list(doc)
    by_path = {r.path: r for r in rows}

    assert by_path["demo_soc.CTRL"].address == 0x0
    assert by_path["demo_soc.STAT"].address == 0x10
    assert by_path["demo_soc.SLOT_A"].address == 0x100
    assert by_path["demo_soc.SLOT_B"].address == 0x104

    ctrl = by_path["demo_soc.CTRL"]
    fields = {f.name: (f.lsb, f.width) for f in ctrl.fields}
    assert fields["ena"] == (0, 1)
    assert fields["mode"] == (8, 4)
    assert fields["flags"] == (16, 8)


def test_flatten_applies_base_offset() -> None:
    doc = load_ralf_file(FIXTURE)
    rows = document_to_register_list(doc, base_offset=0x1000)
    by_path = {r.path: r for r in rows}
    assert by_path["demo_soc.CTRL"].address == 0x1000
    assert by_path["demo_soc.STAT"].address == 0x1010
    assert by_path["demo_soc.SLOT_A"].address == 0x1100


def test_base_offset_adds_to_all_register_addresses() -> None:
    doc = load_ralf_file(FIXTURE)
    base = 0x4000_0000
    rows = document_to_register_list(doc, base_offset=base)
    by_path = {r.path: r for r in rows}
    assert by_path["demo_soc.CTRL"].address == base
    assert by_path["demo_soc.STAT"].address == base + 0x10
    assert by_path["demo_soc.SLOT_A"].address == base + 0x100


def test_system_prefix_in_flat_paths() -> None:
    fixture = Path(__file__).resolve().parent / "fixtures" / "demo_system.ralf"
    doc = load_ralf_file(fixture)
    rows = document_to_register_list(doc)
    by_path = {r.path: r for r in rows}
    assert by_path["demo_chip.demo_soc.regs.CTRL"].address == 0
    assert by_path["demo_chip.demo_soc.regs.STAT"].address == 0x10


def test_stat_implicit_then_explicit_lsbs() -> None:
    doc = load_ralf_file(FIXTURE)
    rows = document_to_register_list(doc)
    stat = next(r for r in rows if r.path == "demo_soc.STAT")
    fmap = {f.name: (f.lsb, f.width) for f in stat.fields}
    assert fmap["cnt"] == (0, 16)
    assert fmap["ovf"] == (31, 1)
