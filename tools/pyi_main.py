"""PyInstaller 专用入口：以 ``python -m ralf_conv`` 同等方式执行 CLI。

业务源码在 ``src/`` 内仅用相对导入；本文件仅由 ``ralf-conv-cli.spec`` 引用。
"""
from __future__ import annotations

import runpy

if __name__ == "__main__":
    runpy.run_module("ralf_conv", run_name="__main__")
