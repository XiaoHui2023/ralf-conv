from __future__ import annotations

import json
from pathlib import Path

from ralf_conv.__main__ import main

FIXTURE_RALF = Path(__file__).resolve().parent / "fixtures" / "demo_soc.ralf"


def test_cli_prints_flat_json_to_stdout(capsys) -> None:
    assert main(["-i", str(FIXTURE_RALF)]) == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert isinstance(data, list)
    assert any(item.get("path") == "demo_soc.CTRL" for item in data)
    assert captured.err == ""


def test_cli_writes_flat_json(tmp_path: Path) -> None:
    out = tmp_path / "out.json"
    assert main(["-i", str(FIXTURE_RALF), "-o", str(out)]) == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert any(item.get("path") == "demo_soc.CTRL" for item in data)


def test_cli_writes_hierarchical_json(tmp_path: Path) -> None:
    out = tmp_path / "tree.json"
    assert (
        main(
            [
                "--format",
                "hierarchical",
                "-i",
                str(FIXTURE_RALF),
                "-o",
                str(out),
            ]
        )
        == 0
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert len(data) == 1
    root = data[0]
    assert root.get("name") == "demo_soc"
    assert root.get("path") == "demo_soc"
    assert root.get("baseAddress") == 0
    assert root.get("addressUnitBits") == 8
    assert "addressBlocks" in root and "registers" in root
    names = {r["name"] for r in root["registers"]}
    assert names >= {"CTRL", "STAT"}
    ctrl = next(r for r in root["registers"] if r["name"] == "CTRL")
    assert ctrl["addressOffset"] == 0
    assert ctrl["size"] == 32
    assert ctrl["fields"][0]["bitOffset"] == 0
    assert ctrl["fields"][0]["bitWidth"] == 1


def test_cli_rejects_non_ralf_input(tmp_path: Path) -> None:
    inp = tmp_path / "x.json"
    inp.write_text("{}", encoding="utf-8")
    out = tmp_path / "o.json"
    assert main(["-i", str(inp), "-o", str(out)]) == 2


def test_cli_rejects_non_json_output(tmp_path: Path) -> None:
    out = tmp_path / "out.yaml"
    assert main(["-i", str(FIXTURE_RALF), "-o", str(out)]) == 2


def test_cli_base_offset_applied_to_flat_json(tmp_path: Path) -> None:
    out = tmp_path / "off.json"
    base = 0x1000
    assert (
        main(
            [
                "-i",
                str(FIXTURE_RALF),
                "-o",
                str(out),
                "-b",
                hex(base),
            ]
        )
        == 0
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    ctrl = next(item for item in data if item.get("path") == "demo_soc.CTRL")
    assert ctrl["address"] == base


def test_cli_base_offset_verilog_hex_literal(tmp_path: Path) -> None:
    out = tmp_path / "off2.json"
    assert (
        main(
            [
                "-i",
                str(FIXTURE_RALF),
                "-o",
                str(out),
                "--base-offset",
                "'h2000",
            ]
        )
        == 0
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    stat = next(item for item in data if item.get("path") == "demo_soc.STAT")
    assert stat["address"] == 0x2000 + 0x10


def test_cli_pass_include_dirs(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parent / "fixtures" / "include_merge" / "root"
    inc = Path(__file__).resolve().parent / "fixtures" / "include_merge" / "inc"
    out = tmp_path / "merged.json"
    rc = main(
        [
            "-i",
            str(root / "top.ralf"),
            "-o",
            str(out),
            "-I",
            str(inc),
        ]
    )
    assert rc == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    paths = {item["path"] for item in data}
    assert "soc.CORE_STAT" in paths
    assert "telemetry.EVT_CNT" in paths
