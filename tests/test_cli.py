from __future__ import annotations

import json
from pathlib import Path

from ralf_conv.cli import main

FIXTURE_RALF = Path(__file__).resolve().parent / "fixtures" / "demo_soc.ralf"


def test_cli_writes_flat_json(tmp_path: Path) -> None:
    out = tmp_path / "out.json"
    assert main(["-i", str(FIXTURE_RALF), "-o", str(out)]) == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert any(item.get("路径") == "demo_soc.CTRL" for item in data)


def test_cli_rejects_non_ralf_input(tmp_path: Path) -> None:
    inp = tmp_path / "x.json"
    inp.write_text("{}", encoding="utf-8")
    out = tmp_path / "o.json"
    assert main(["-i", str(inp), "-o", str(out)]) == 2


def test_cli_rejects_non_json_output(tmp_path: Path) -> None:
    out = tmp_path / "out.yaml"
    assert main(["-i", str(FIXTURE_RALF), "-o", str(out)]) == 2


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
    paths = {item["路径"] for item in data}
    assert "soc.CORE_STAT" in paths
    assert "telemetry.EVT_CNT" in paths
