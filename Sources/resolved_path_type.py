#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
resolved_path_type.py

An extended version of Pydantic's PathType with permission and resolution checks.

MIT License

Copyright (c) 2025 <Your Name>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import annotations

import os
import typing
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from typing_extensions import Annotated
from pydantic.types import PathType
from pydantic_core import core_schema


class PathPermissionError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class ResolvedPathType(PathType):
    path_type: Literal["file", "dir", "new"]
    must_be_readable: bool = False
    must_be_writable: bool = False
    must_be_executable: bool = False
    must_exist: bool = True

    def _resolve_and_validate(self, path: Path, info: core_schema.ValidationInfo) -> Path:
        try:
            resolved_path = path.expanduser().resolve(strict=False)
        except (OSError, RuntimeError):
            resolved_path = path.expanduser()

        if self.path_type == "file":
            validated_path = PathType.validate_file(resolved_path, info)
        elif self.path_type == "dir":
            validated_path = PathType.validate_directory(resolved_path, info)
        elif self.path_type == "new":
            validated_path = PathType.validate_new(resolved_path, info)
        else:
            raise ValueError(f"Unknown path_type: {self.path_type}")

        self._check_permissions(validated_path)
        return validated_path

    def _check_permissions(self, path: Path) -> None:
        failures = []
        if self.must_exist and not path.exists() and self.path_type != "new":
            failures.append("exist")
        if self.must_be_readable and not os.access(path, os.R_OK):
            failures.append("readable")
        if self.must_be_writable and not os.access(path, os.W_OK):
            failures.append("writable")
        if self.must_be_executable and not os.access(path, os.X_OK):
            failures.append("executable")
        if failures:
            raise PathPermissionError(f"Path '{path}' must be: {', '.join(failures)}")

    def __call__(self, path: Path, info: core_schema.ValidationInfo) -> Path:
        return self._resolve_and_validate(path, info)

    def __hash__(self) -> int:
        return hash((
            self.path_type,
            self.must_be_readable,
            self.must_be_writable,
            self.must_be_executable,
            self.must_exist,
        ))

    @classmethod
    def readable_file(cls) -> ResolvedPathType:
        return cls(path_type="file", must_be_readable=True)

    @classmethod
    def writable_file(cls) -> ResolvedPathType:
        return cls(path_type="file", must_be_writable=True)

    @classmethod
    def executable_file(cls) -> ResolvedPathType:
        return cls(path_type="file", must_be_executable=True)

    @classmethod
    def readable_directory(cls) -> ResolvedPathType:
        return cls(path_type="dir", must_be_readable=True)

    @classmethod
    def writable_directory(cls) -> ResolvedPathType:
        return cls(path_type="dir", must_be_writable=True)

    @classmethod
    def executable_directory(cls) -> ResolvedPathType:
        return cls(path_type="dir", must_be_executable=True)

    @classmethod
    def new_file(cls) -> ResolvedPathType:
        return cls(path_type="new", must_exist=False)

    @classmethod
    def new_directory(cls) -> ResolvedPathType:
        return cls(path_type="new", must_exist=False)


ResolvedFilePath = Annotated[Path, ResolvedPathType.readable_file()]
WritableFilePath = Annotated[Path, ResolvedPathType.writable_file()]
ExecutableFilePath = Annotated[Path, ResolvedPathType.executable_file()]

ResolvedDirectoryPath = Annotated[Path, ResolvedPathType.readable_directory()]
WritableDirectoryPath = Annotated[Path, ResolvedPathType.writable_directory()]
ExecutableDirectoryPath = Annotated[Path, ResolvedPathType.executable_directory()]

ResolvedNewFilePath = Annotated[Path, ResolvedPathType.new_file()]
ResolvedNewDirectoryPath = Annotated[Path, ResolvedPathType.new_directory()]

ResolvedExistingPath = typing.Union[ResolvedFilePath, ResolvedDirectoryPath]
