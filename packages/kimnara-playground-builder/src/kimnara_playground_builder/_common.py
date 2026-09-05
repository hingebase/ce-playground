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

__all__ = ["Compiler", "Context", "env", "which"]

import os
import shutil
from typing import TYPE_CHECKING, Literal, Required, TypedDict

from minijinja import Environment, load_from_path

from . import __path__

if TYPE_CHECKING:
    from collections.abc import Mapping

type _Boolean = Literal["true", "false"]

env: Environment = Environment(load_from_path(__path__))


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


def which(cmd: str, env: Mapping[str, str]) -> str:
    if res := shutil.which(cmd, path=env["PATH"]):
        return os.path.normpath(res)
    message = f"{cmd!r} not found"
    raise AssertionError(message)
