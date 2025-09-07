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

__all__ = ["Compiler", "Context", "env", "pixi", "which"]

import asyncio
import os
import shutil
import sys
from collections.abc import Mapping
from typing import Literal, Required, TypedDict

import minijinja

type _Boolean = Literal["true", "false"]

env = minijinja.Environment(minijinja.load_from_path("templates"))


class Compiler(TypedDict, total=False):
    name: Required[str]
    exe: Required[str]
    options: str
    intelAsm: str
    needsMulti: _Boolean
    supportsBinary: _Boolean
    supportsBinaryObject: _Boolean
    supportsExecute: _Boolean
    versionFlag: str
    versionRe: str
    compilerType: str
    interpreted: _Boolean
    emulated: _Boolean
    executionWrapper: str
    executionWrapperArgs: str
    demangler: str
    demanglerArgs: str
    demanglerType: str
    objdumper: str
    objdumperArgs: str
    objdumperType: str
    instructionSet: str
    includeFlag: str
    includePath: str
    libPath: str
    unwiseOptions: str


class Context(TypedDict, total=False):
    defaultCompiler: str
    demangler: Required[str]
    objdumper: str
    llvmDisassembler: str
    compiler: Required[dict[str, Compiler]]


async def pixi(*args: str) -> bytes:
    proc = await asyncio.create_subprocess_exec(
        "pixi", "-q", *args,
        stdin=asyncio.subprocess.DEVNULL,
        stdout=asyncio.subprocess.PIPE,
    )
    out, _ = await proc.communicate()
    if proc.returncode != 0:
        sys.exit(proc.returncode or 1)
    return out


def which(cmd: str, env: Mapping[str, str]) -> str:
    if res := shutil.which(cmd, path=env["PATH"]):
        return os.path.normpath(res)
    message = f"{cmd!r} not found"
    raise AssertionError(message)
