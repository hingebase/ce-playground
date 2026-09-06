# Kimnara Playground

[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/hingebase/kimnara-playground/update-lockfiles.yml?label=ci&logo=github)](https://github.com/hingebase/kimnara-playground/actions)
![Apache-2.0 License](https://img.shields.io/github/license/hingebase/kimnara-playground)
![Pixi](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/prefix-dev/pixi/main/assets/badge/v0.json)
![basedpyright](https://img.shields.io/endpoint?url=https://docs.basedpyright.com/latest/badge.json)
![ty](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json)
![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)

Self-hosted [Compiler Explorer][1] for trying [Kimnara][6].

## Usage
Dump the assembly of Kimnara functions decorated with one of
- `@kn.func(nopython=True, ...)`
- `@kn.cfunc(nopython=True, ...)`
- `@kn.ufunc(nopython=True, parallel=False, ...)`
- `@kn.gufunc(nopython=True, parallel=False, ...)`
by assigning their `.dispatcher` to module-level variables. Example:
``` py
import kimnara as kn

@kn.func(nopython=True)
def add(x1: int, x2: int) -> int:
    return x1 + x2

shown = add.dispatcher

@kn.func(nopython=True)
def hidden(x1: int, x2: int) -> int:
    return x1 - x2
```
Developers may compare the assembly among multiple Numba versions
and C/C++ compilers.

## Build steps
1. Check if your OS meets the minimum requirements [here][7]
2. (macOS-only) Install Xcode or [Xcode Command Line Tools][2]
3. (Windows-only) Install Visual Studio 2026 or [Microsoft C++ Build Tools][3]
4. Download pre-compiled Compiler Explorer from its [GitHub Actions][4] to the
   root directory of this project
5. Install [Pixi][5] 0.71.x on macOS, >=0.76 otherwise
6. `pixi r --locked start`  
   There will be a huge installation for the first run, please be patient.  
   Once installed, the server only takes few seconds to launch.

[1]: https://godbolt.org/
[2]: https://developer.apple.com/library/archive/technotes/tn2339/_index.html
[3]: https://visualstudio.microsoft.com/visual-cpp-build-tools/
[4]: https://github.com/compiler-explorer/compiler-explorer/actions/workflows/test-and-deploy.yml
[5]: https://pixi.sh/latest/installation/
[6]: https://github.com/hingebase/kimnara
[7]: pixi.lock#L2-L18
