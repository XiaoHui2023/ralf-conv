# 打包工具

## 一键打包（PyInstaller；Linux 再 staticx）

在仓库根执行（使用根目录 `.venv`，无则创建）。每次打包会 `--force-reinstall` 重装 `pyproject.toml` 依赖与 PyInstaller，避免 `.venv` 残留旧版依赖。

### Linux / macOS / Git Bash

```bash
./tools/pack.sh
```

### Windows

```bat
tools\pack.bat
```

无法直接执行 `pack.sh` 时，也可用 Git Bash：`bash tools/pack.sh`。

产物写入 `dist/`：

| 目标 | 产物 |
| --- | --- |
| 主入口（src） | `ralf-conv` / `ralf-conv.exe` |
| 发布压缩包 | `ralf-conv-<version>-linux.tar.gz` / `ralf-conv-<version>-windows.zip` |

| 平台 | 脚本 | staticx |
| --- | --- | --- |
| Linux | `pack.sh` | 需要系统 **patchelf** |
| macOS 等 | `pack.sh` | 跳过 |
| Windows | `pack.bat` / `pack.sh` | 跳过 |
