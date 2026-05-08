from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ralf_model import RalfError, load_ralf_file

from ralf_conv.flatten import document_to_register_list


def _make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ralf-conv",
        description="使用 ralf_model 解析 RALF，展开为扁平寄存器列表并输出 JSON。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例:\n"
            "  ralf-conv -i chip.ralf -o chip.json\n"
            "  ralf-conv -i top.ralf -o out.json -I ./inc -I ./lib\n"
        ),
    )
    p.add_argument(
        "-i",
        "--input",
        dest="input_path",
        type=Path,
        required=True,
        metavar="PATH",
        help="输入 .ralf 文件路径",
    )
    p.add_argument(
        "-o",
        "--output",
        dest="output_path",
        type=Path,
        required=True,
        metavar="PATH",
        help="输出 .json 文件路径",
    )
    p.add_argument(
        "-I",
        dest="include_dirs",
        type=Path,
        action="append",
        default=[],
        metavar="DIR",
        help="RALF `source` 搜索目录（可重复，对应该文件目录与显式 -I 列表）",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = _make_parser().parse_args(argv)
    if args.input_path.suffix.lower() != ".ralf":
        print("错误: 输入须为 .ralf 文件。", file=sys.stderr)
        return 2
    if args.output_path.suffix.lower() != ".json":
        print("错误: 输出须为 .json 文件。", file=sys.stderr)
        return 2
    try:
        doc = load_ralf_file(
            args.input_path,
            include_paths=tuple(args.include_dirs),
        )
        rows = document_to_register_list(doc)
        payload = [r.as_mapping() for r in rows]
        args.output_path.parent.mkdir(parents=True, exist_ok=True)
        args.output_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return 0
    except (OSError, ValueError, RalfError) as e:
        print(f"错误: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
