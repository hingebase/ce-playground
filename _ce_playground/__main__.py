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

__all__ = ["main"]

import asyncio
import json
import sys
from typing import TYPE_CHECKING

from . import _c, _common, _cpp, _numba, _unpack

if TYPE_CHECKING:
    from collections.abc import Mapping


def main() -> None:
    _unpack.main()
    info, tasks = asyncio.run(_envs())
    envs = {k: json.loads(v.result()) for k, v in tasks.items()}
    context = _c.local_properties(envs)
    _cpp.local_properties(context, envs)
    _numba.local_properties(json.loads(info), context["demangler"])


async def _envs() -> tuple[bytes, Mapping[str, asyncio.Task[bytes]]]:
    tasks: dict[str, asyncio.Task[bytes]] = {}
    async with asyncio.TaskGroup() as g:
        info = g.create_task(_common.pixi("info", "--json"))
        tasks["clang"] = g.create_task(_inspect("clang"))
        if sys.platform != "darwin":
            tasks["intel"] = g.create_task(_inspect("intel"))
            if sys.platform == "win32":
                tasks["gcc"] = g.create_task(_inspect("gcc", "_inspect2"))
                tasks["msvc"] = g.create_task(_inspect("msvc"))
            else:
                tasks["gcc"] = g.create_task(_inspect("gcc"))
    return info.result(), tasks


async def _inspect(env: str, task: str = "_inspect") -> bytes:
    out = await _common.pixi("r", "-e", env, task)
    if task == "_inspect2":
        out = out[out.index(b'{"'):]
    return out


if __name__ == "__main__":
    main()
