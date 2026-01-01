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

import os
import shutil
import sys
from pathlib import Path
from typing import NoReturn


def _main() -> NoReturn:
    os.chdir(os.environ["PIXI_PROJECT_ROOT"])
    prefix = Path(sys.prefix)
    if arg0 := shutil.which("pixi", path=prefix / "bin"):
        cuda_home = prefix.with_name("cuda")
        if cuda_home.is_dir():
            if sys.platform == "win32":
                cuda_home /= "Library"
            os.environ["CUDA_HOME"] = str(cuda_home)
        os.execl(  # noqa: S606
            arg0,
            arg0,
            "-q",
            "r",
            "-e", prefix.name,
            "numba", "-s",
        )
    message = "Pixi not found"
    raise AssertionError(message)


if __name__ == "__main__":
    _main()
