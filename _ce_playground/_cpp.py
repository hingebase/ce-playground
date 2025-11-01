# Copyright 2025 hingebase

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__all__ = ["local_properties"]

import sys
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, override

from . import _c, _common

if TYPE_CHECKING:
    from collections.abc import Mapping


def local_properties(
    context: _common.Context,
    envs: Mapping[str, Mapping[str, str]],
) -> None:
    context["compiler"] = {
        k: _compilers[k](v).compiler() for k, v in envs.items()
    }
    Path("compiler-explorer/etc/config/c++.local.properties").write_text(
        _common.env.render_template("c.local.properties.jinja", **context),
        encoding="utf-8",
        newline="",
    )


class _GNU(_c.GNU):
    exe_envvar: ClassVar[str] = "CXX"
    options_envvar: ClassVar[str] = "CXXFLAGS"

    @override
    def options(self) -> str:
        return "-std=c++2c"


class _Clang(_GNU, _c.Clang):
    pass


class _IntelLLVM(_Clang, _c.IntelLLVM):
    if sys.platform == "win32":
        @override
        def options(self) -> str:
            return "-EHsc -std:c++latest -utf-8"


class _MSVC(_IntelLLVM, _c.MSVC):
    pass


_compilers: dict[str, type[_GNU]] = {
    "gcc": _GNU,
    "clang": _Clang,
    "intel": _IntelLLVM,
    "msvc": _MSVC,
}
