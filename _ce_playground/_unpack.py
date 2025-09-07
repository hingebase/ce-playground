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

__all__ = ["main"]

import re
import tarfile
import zipfile


def main() -> None:
    with zipfile.ZipFile("dist.zip") as f:
        for i in f.infolist():
            if i.filename.endswith(".static.tar.xz"):
                with f.open(i) as g, tarfile.open(mode="r|xz", fileobj=g) as h:
                    h.extractall("compiler-explorer/static", filter="data")
            elif i.filename.endswith(".tar.xz"):
                with f.open(i) as g, tarfile.open(mode="r|xz", fileobj=g) as h:
                    h.extractall("compiler-explorer", filter=_filter)  # noqa: S202


def _filter(member: tarfile.TarInfo, path: str, /) -> tarfile.TarInfo | None:
    result = tarfile.data_filter(member, path)
    return None if _properties.fullmatch(result.name) else result


_properties = re.compile(r"\./etc/config/[^/]+\.properties")

if __name__ == "__main__":
    main()
