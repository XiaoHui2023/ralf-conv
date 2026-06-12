# 打包发布

需要发布可执行文件时，在可访问 PyPI 的机器上于仓库根执行一键脚本；Linux 上会在 PyInstaller onefile 之后再做 staticx，得到更易在旧 glibc 环境运行的自解压单文件。

## 一键打包

### Linux / macOS / Git Bash

```bash
./tools/pack.sh
```

### Windows

```bat
tools\pack.bat
```

脚本会创建或复用根目录 `.venv`，每次以 `pip install --upgrade --force-reinstall -e .` 重装项目及其依赖（含 `python-library-ralf-model`），再调用 PyInstaller。详细参数见 [tools/README.md](tools/README.md)。

| 命令 | 产物（`dist/`） |
| --- | --- |
| `./tools/pack.sh` 或 `src` | `ralf-conv`、`ralf-conv-<version>-linux.tar.gz` |
| `tools\pack.bat` 或 `src` | `ralf-conv.exe`、`ralf-conv-<version>-windows.zip` |

压缩包内除可执行体外含 `example/demo_soc.ralf` 示例；清单见 `tools/bundle_release.py`。

Windows 产物为 `*.exe`，无 staticx 步骤。

## GitHub 自动构建与下载

推送 `v*` 标签（如 `v0.1.0`）时，GitHub Actions 会：

1. 在 **Ubuntu 16.04** 容器内执行 `tools/pack.sh`（PyInstaller + staticx），生成可在旧 glibc 环境运行的 Linux 单文件；
2. 在 **Windows** 上执行 `tools/pack.bat`；
3. 将 `ralf-conv-*.tar.gz` 与 `ralf-conv-*.zip` 上传到该版本的 **GitHub Release**。

未打标签时，可在仓库 **Actions → Release → Run workflow** 手动触发；产物在对应运行的 **Artifacts** 中下载。

## Linux staticx

在 Linux 上，`tools/pack.sh` 对 ELF 产物再运行 **staticx**，需要系统已安装 **patchelf**（例如 `sudo apt install patchelf`）。**macOS** 当前跳过 staticx，仅保留 PyInstaller onefile。

## Spec 文件

PyInstaller 规格放在仓库根目录：

- `ralf-conv-cli.spec` → `ralf-conv`

## 兼容边界

单文件可执行文件的系统兼容性取决于**执行打包的那台机器**。要支持较旧的 Linux 发行版，应在 glibc 基线不高于目标环境的系统上构建，并在目标机实测 staticx 产物。若运行期还依赖额外系统动态库，需单独验证。
