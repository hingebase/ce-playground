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

import asyncio
import json
import shutil
import sys
from pathlib import Path
from typing import TYPE_CHECKING, TypedDict, cast

import packaging.version

from . import _common

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

_PATCH = b"""\
import os
import shutil
from pathlib import Path

if __name__ == "__main__" and os.getenv("PIXI_ENVIRONMENT_NAME") == "start":
    prefix = Path(sys.prefix)
    if arg0 := shutil.which("pixi", path=prefix / "bin"):
        cuda_home = prefix.with_name("cuda")
        if cuda_home.is_dir():
            if sys.platform == "win32":
                cuda_home /= "Library"
            os.environ["CUDA_HOME"] = str(cuda_home)
        os.execl(
            arg0,
            arg0,
            "-q",
            "r",
            "-e", prefix.name,
            "--manifest-path", os.environ["PIXI_PROJECT_MANIFEST"],
            sys.executable,
            "-I",
            *sys.argv,
        )
"""


def local_properties(info: _Info, demangler: str) -> None:
    with (
        Path("compiler-explorer/etc/scripts/numba_wrapper.py").open("r+b")
    ) as f:
        for line in f:
            if line.startswith(b"import sys"):
                break
        n = f.tell()
        lines = [_PATCH, f.read()]
        f.seek(n)
        f.writelines(lines)
    shutil.copy(
        "scripts/_numba_s.py",
        "compiler-explorer/etc/config/versionFlag.py",
    )
    compiler: dict[str, _common.Compiler] = {
        env["name"]: {
            "name": "",
            "exe": _common.which("python", {"PATH": _path(env["prefix"])}),
        }
        for env in info["environments_info"]
        if env["name"].startswith("nb")
    }
    for k, v in asyncio.run(_versions(compiler)).items():
        for pkg in cast("Iterable[_Package]", json.loads(v.result())):
            if pkg["name"] == "numba":
                compiler[k]["name"] = f"numba {pkg['version']}"
                break
        else:
            message = "Numba not found"
            raise AssertionError(message)
    context: _common.Context = {
        "defaultCompiler": max(
            compiler,
            key=lambda c: packaging.version.parse(compiler[c]["name"][6:]),
        ),
        "demangler": demangler,
        "compiler": compiler,
    }
    Path("compiler-explorer/etc/config/numba.local.properties").write_text(
        _common.env.render_template("numba.local.properties.jinja", **context),
        encoding="utf-8",
        newline="",
    )


class _Environment(TypedDict):
    name: str
    prefix: str


class _Info(TypedDict):
    environments_info: list[_Environment]


class _Package(TypedDict):
    name: str
    version: str


if sys.platform == "win32":
    def _path(prefix: str) -> str:
        return prefix
else:
    def _path(prefix: str) -> str:
        return str(Path(prefix, "bin"))


async def _versions(names: Iterable[str]) -> Mapping[str, asyncio.Task[bytes]]:
    versions: dict[str, asyncio.Task[bytes]] = {}
    async with asyncio.TaskGroup() as g:
        for name in names:
            versions[name] = g.create_task(
                _common.pixi("ls", "-e", name, "--json", r"^numba$"),
            )
    return versions
