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

__all__ = ["main"]

import os
import pathlib
import posixpath
import re
import sys
import tarfile
import zipfile
from typing import TYPE_CHECKING

import nodejs_wheel

from . import _c, _cpp, _env, _numba

if TYPE_CHECKING:
    from collections.abc import Mapping


def main() -> None:
    _unpack()
    _custom_compile_timeout()
    envs = _inspect()
    context = _c.local_properties(envs)
    _cpp.local_properties(context, envs)
    _numba.local_properties(envs, context["demangler"])
    _discover_compilers()


def _custom_compile_timeout() -> None:
    pathlib.Path(
        "compiler-explorer/etc/config/compiler-explorer.local.properties",
    ).write_text(
        "compileTimeoutMs=80000\n",
        encoding="ascii",
        newline="",
    )


def _discover_compilers() -> None:
    nodejs_wheel.node(
        ["app.js", "--discovery-only", "discovered-compilers.json"],
        cwd="compiler-explorer",
        env=dict(os.environ, NODE_ENV="production"),
        check=True,
    )


def _inspect() -> Mapping[str, Mapping[str, str]]:
    envs = _env.inspect()
    if sys.platform == "win32":
        pattern = re.compile(r"/([a-z])/(.*)")
        env = envs["gcc"]
        env["PATH"] = os.pathsep.join(
            os.path.normpath(rematch.expand(r"\1:/\2"))
            for item in env["PATH"].split(posixpath.pathsep)
            if (rematch := pattern.fullmatch(item))
        )
        envs["clang"].update(CC="clang", CXX="clang++")
    return envs


def _filter(member: tarfile.TarInfo, path: str, /) -> tarfile.TarInfo | None:
    result = tarfile.data_filter(member, path)
    return None if _properties.fullmatch(result.name) else result


def _unpack() -> None:
    with zipfile.ZipFile("dist.zip") as f:
        for i in f.infolist():
            if i.filename.endswith(".static.tar.xz"):
                with f.open(i) as g, tarfile.open(mode="r|xz", fileobj=g) as h:
                    h.extractall("compiler-explorer/static", filter="data")
            elif i.filename.endswith(".tar.xz"):
                with f.open(i) as g, tarfile.open(mode="r|xz", fileobj=g) as h:
                    h.extractall("compiler-explorer", filter=_filter)  # ruff: ignore[tarfile-unsafe-members]


_properties = re.compile(r"\./etc/config/[^/]+\.properties")
