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
    by_path = {r.path: r for r in rows}

    assert by_path["soc.CORE_STAT"].address == 0
    assert by_path["soc.ALARM"].address == 0x20
    wdt = next(f for f in by_path["soc.ALARM"].fields if f.name == "WDT_EN")
    assert wdt.lsb == 5 and wdt.width == 1

    assert by_path["telemetry.EVT_CNT"].address == 0
    pin = by_path["gpio.PIN"]
    assert pin.fields[0].name == "dir" and pin.fields[0].lsb == 0
    assert pin.fields[1].name == "dat" and pin.fields[1].lsb == 16
