# Copyright 2025-2026 hingebase

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied. See the License for the specific language governing
# permissions and limitations under the License.

__all__ = ["local_properties"]

import os
from pathlib import Path
from typing import TYPE_CHECKING

import packaging.version
import rattler.exceptions

from . import _common, _env

if TYPE_CHECKING:
    from collections.abc import Mapping


def local_properties(
    envs: Mapping[str, Mapping[str, str]],
    demangler: str,
) -> None:
    if not hasattr(rattler.exceptions, "ParseCondaLockError"):
        try:
            rattler.LockFile.from_path(Path(os.devnull))
        except Exception as e:  # ruff: ignore[blind-except]
            rattler.exceptions.ParseCondaLockError = type(e)

    versions = {
        k: packaging.version.parse(v)
        for k, v in _env.numba_versions().items()
    }
    compiler: dict[str, _common.Compiler] = {
        k: {
            "name": f"numba {versions[k]}",
            "exe": _common.which("kimnara-playground-runner", v),
        }
        for k, v in envs.items()
        if k.startswith("nb")
    }
    context: _common.Context = {
        "defaultCompiler": max(compiler, key=versions.__getitem__),
        "demangler": demangler,
        "compiler": compiler,
    }
    Path("compiler-explorer/etc/config/numba.local.properties").write_text(
        _common.env.render_template("numba.local.properties.jinja", **context),
        encoding="utf-8",
        newline="",
    )
