from __future__ import annotations

from pathlib import Path

import pytest

from ralf_model import RalfSourceError, load_ralf_file

from ralf_conv.flatten import document_to_register_list

ROOT = Path(__file__).resolve().parent / "fixtures" / "include_merge" / "root"
TOP = ROOT / "top.ralf"
INC = Path(__file__).resolve().parent / "fixtures" / "include_merge" / "inc"


def test_include_path_required_for_sibling_dir_source() -> None:
    with pytest.raises(RalfSourceError):
        load_ralf_file(TOP, include_paths=())

    doc = load_ralf_file(TOP, include_paths=(INC,))
    names = [b.name for b in doc.blocks]
    assert "soc" in names
    assert "telemetry" in names
    assert "gpio" in names


def test_flatten_merged_sources_paths_and_syntax_variants() -> None:
    doc = load_ralf_file(TOP, include_paths=(INC,))
    rows = document_to_register_list(doc)
    by_path = {r.路径: r for r in rows}

    assert by_path["soc.CORE_STAT"].地址 == 0
    assert by_path["soc.ALARM"].地址 == 0x20
    wdt = next(f for f in by_path["soc.ALARM"].fields if f.名字 == "WDT_EN")
    assert wdt.最低位 == 5 and wdt.位宽 == 1

    assert by_path["telemetry.EVT_CNT"].地址 == 0
    pin = by_path["gpio.PIN"]
    assert pin.fields[0].名字 == "dir" and pin.fields[0].最低位 == 0
    assert pin.fields[1].名字 == "dat" and pin.fields[1].最低位 == 16
