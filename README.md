# CE-Playground

[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/hingebase/ce-playground/update-lockfiles.yml?label=ci&logo=github)](https://github.com/hingebase/ce-playground/actions)
![Apache-2.0 License](https://img.shields.io/github/license/hingebase/ce-playground)
![Pixi](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/prefix-dev/pixi/main/assets/badge/v0.json)
![basedpyright](https://img.shields.io/badge/basedpyright-checked-42b983)
![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)

Experimental self-hosted [Compiler Explorer][1].

## Features (compared to the official site)
- No hard-coded paths
- Support the following languages and compilers:
  | Language | Compilers |
  | :-: | :-: |
  | C | gcc, clang, cl, icx |
  | C++ | g++, clang++, cl, icpx |
  | Python | numba |
- Multiple versions of numba

## Prerequisites
| OS | Arch | Installed software |
| :-: | :-: | :-: |
| Linux | x86-64 | glibc |
| macOS | x86-64 | Xcode or [Xcode Command Line Tools][2] |
| Windows 10/11 | x86-64 | Visual Studio or [Microsoft C++ Build Tools][3] |

## Usage
1. Download pre-compiled Compiler Explorer from its [GitHub Actions][4] to the
   root directory of this project
2. Install a recent version of [Pixi][5]
3. `pixi r start`

[1]: https://godbolt.org/
[2]: https://developer.apple.com/library/archive/technotes/tn2339/_index.html
[3]: https://visualstudio.microsoft.com/visual-cpp-build-tools/
[4]: https://github.com/compiler-explorer/compiler-explorer/actions/workflows/test-and-deploy.yml
[5]: https://pixi.sh/latest/installation/
