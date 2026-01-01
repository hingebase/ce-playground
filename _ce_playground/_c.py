# Copyright 2025-2026 hingebase

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__all__ = ["GNU", "MSVC", "Clang", "IntelLLVM", "local_properties"]

import dataclasses
import os
import re
import shlex
import subprocess  # noqa: S404
import sys
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, LiteralString, override

from . import _common

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence


def local_properties(envs: Mapping[str, Mapping[str, str]]) -> _common.Context:
    context: _common.Context = {
        "demangler": _common.which("llvm-cxxfilt", envs["clang"]),
        "llvmDisassembler": _common.which("llvm-dis", envs["clang"]),
        "compiler": {
            "c" + k: _compilers[k](v).compiler() for k, v in envs.items()
        },
    }
    match sys.platform:
        case "linux":
            env = envs["gcc"]
            context.update(
                defaultCompiler="gcc",
                objdumper=_common.which(env["OBJDUMP"], env),
            )
        case "darwin":
            context.update(
                defaultCompiler="clang",
                objdumper=_common.which("objdump", os.environ),
            )
        case "win32":
            env = envs["gcc"]
            context.update(
                defaultCompiler="msvc",
                objdumper=_common.which(env["OBJDUMP"], env),
            )
            p = Path("compiler-explorer/etc/config/versionFlag.txt")
            p.write_bytes(b"-c nul\n")
        case _:
            raise NotImplementedError
    Path("compiler-explorer/etc/config/c.local.properties").write_text(
        _common.env.render_template("c.local.properties.jinja", **context),
        encoding="utf-8",
        newline="",
    )
    return context


@dataclasses.dataclass
class GNU:
    env: Mapping[str, str]

    exe_envvar: ClassVar[str] = "CC"
    options_envvar: ClassVar[str] = "CFLAGS"

    def compiler(self) -> _common.Compiler:
        exe = _common.which(self.env[self.exe_envvar], self.env)
        stdout = subprocess.check_output(  # noqa: S603
            self.version(exe),
            stderr=subprocess.STDOUT,
            encoding="ascii",
        )
        version = _version.findall(stdout)[0]
        options = [self.env.get(self.options_envvar, ""), self.options()]
        obj: _common.Compiler = {
            "name": f"{_name(Path(exe))} {version}",
            "exe": exe,
            "options": " ".join(filter(None, options)),
            "instructionSet": "amd64",
            "includeFlag": "-I",
            "unwiseOptions": "-march=native",
        }
        if sys.platform == "win32":
            obj["compilerType"] = "win32-mingw-gcc"
        return obj

    def options(self) -> str:
        del self
        return "-std=c2y"

    def version(self, exe: str) -> Sequence[str]:
        del self
        return [exe, "--version"]


class Clang(GNU):
    @override
    def compiler(self) -> _common.Compiler:
        obj = super().compiler()
        obj.update(
            # https://github.com/compiler-explorer/compiler-explorer/issues/3472
            compilerType="clang",
            intelAsm="-mllvm --x86-asm-syntax=intel",
        )
        if sys.platform == "win32":
            obj.update(
                demangler=_common.which("undname", self.env),
                demanglerType="win32",
            )
            for key in "includePath", "libPath":
                obj[key] = os.pathsep.join(
                    map(
                        os.path.normpath,
                        self.env[key[:-4].upper()].split(os.pathsep),
                    ),
                )
        return obj


class IntelLLVM(Clang):
    @override
    def compiler(self) -> _common.Compiler:
        obj = super().compiler()
        self._include(obj, "opt/compiler/include")
        if sys.platform == "win32":
            self._include(obj, "include")
            # https://github.com/compiler-explorer/compiler-explorer/issues/4940
            obj["compilerType"] = "win32-vc"
        else:
            obj["compilerType"] = "clang-intel"
            obj["intelAsm"] = "-masm=intel"
            args = obj.get("options", "").split()
            args.append(f"--sysroot={self.env['CONDA_BUILD_SYSROOT']}")
            obj["options"] = shlex.join(args)
        obj.pop("unwiseOptions", "")
        return obj

    if sys.platform == "win32":
        @override
        def options(self) -> str:
            return "-masm=intel -Qstd:c18"

    def _include(self, obj: _common.Compiler, path: LiteralString) -> None:
        include = Path(self.env["CONDA_PREFIX"], path)
        if include.is_dir():
            obj["includePath"] = os.pathsep.join(
                filter(None, [str(include), obj.get("includePath", "")]),
            )


class MSVC(IntelLLVM):
    @override
    def compiler(self) -> _common.Compiler:
        obj = super().compiler()
        obj.update(
            versionFlag="@etc/config/versionFlag.txt",
            versionRe=r"^.*Microsoft \(R\).*$",
        )
        obj.pop("intelAsm", "")
        return obj

    @override
    def options(self) -> str:
        return "-std:clatest -utf-8"

    @override
    def version(self, exe: str) -> Sequence[str]:
        return exe


if sys.platform == "win32":
    def _name(exe: Path) -> str:
        return exe.stem
else:
    def _name(exe: Path) -> str:
        return exe.name


_compilers: dict[str, type[GNU]] = {
    "gcc": GNU,
    "clang": Clang,
    "intel": IntelLLVM,
    "msvc": MSVC,
}
_version = re.compile(r"\d+\.\d+\.\d+")
