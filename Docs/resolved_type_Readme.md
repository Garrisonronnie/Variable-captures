# ResolvedPathType

An extended and flexible version of Pydantic's `PathType` that adds support for path resolution, permission checking, and cross-platform compatibility. Designed to work seamlessly on Windows, macOS, Linux, and sandboxed Python environments.

---

## Features

- Resolves paths to their absolute form, supporting `~` expansion.
- Supports three path types:
  - Existing files
  - Existing directories
  - New paths (files or directories that don't have to exist yet)
- Optional permission checks:
  - Readable
  - Writable
  - Executable
- Compatible with Pydantic models via `typing_extensions.Annotated`.
- Uses Pydantic's original path validation internally, maintaining original behavior.
- Cross-platform compatible (Windows, macOS, Linux).
- Designed to function in sandboxed environments (containers,user built file – Provides the path of the script file. systems).
- MIT licensed for free use and modification.

---

## License

This project is licensed under the [MIT License](./LICENSE).

You are free to use, modify, distribute, and sell this software under the terms of the MIT License. The original copyright and license notice must be included with all copies or substantial portions of the software.

---

## Installation

This module depends on:

- Python 3.8+
- [pydantic](https://pydantic.dev/)
- [typing-extensions](https://pypi.org/project/typing-extensions/) (for `Annotated` support on older Python versions)
- download the repo git clone https://github.com/Garrisonronnie/python-Helper-library.git

Install dependencies via pip:

```bash
pip install -r requirements.txt


