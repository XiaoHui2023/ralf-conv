from __future__ import annotations

from pathlib import Path

from ralf_model import load_ralf_file

from ralf_conv.flatten import document_to_register_list

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "demo_soc.ralf"


def test_demo_soc_flatten_addresses_and_paths() -> None:
    doc = load_ralf_file(FIXTURE)
    rows = document_to_register_list(doc)
    by_path = {r.路径: r for r in rows}

    assert by_path["demo_soc.CTRL"].地址 == 0x0
    assert by_path["demo_soc.STAT"].地址 == 0x10
    assert by_path["demo_soc.SLOT_A"].地址 == 0x100
    assert by_path["demo_soc.SLOT_B"].地址 == 0x104

    ctrl = by_path["demo_soc.CTRL"]
    fields = {f.名字: (f.最低位, f.位宽) for f in ctrl.fields}
    assert fields["ena"] == (0, 1)
    assert fields["mode"] == (8, 4)
    assert fields["flags"] == (16, 8)


def test_stat_implicit_then_explicit_lsbs() -> None:
    doc = load_ralf_file(FIXTURE)
    rows = document_to_register_list(doc)
    stat = next(r for r in rows if r.路径 == "demo_soc.STAT")
    fmap = {f.名字: (f.最低位, f.位宽) for f in stat.fields}
    assert fmap["cnt"] == (0, 16)
    assert fmap["ovf"] == (31, 1)
