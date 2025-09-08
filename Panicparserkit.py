#!/usr/bin/env python3
"""
MIT License
Copyright (c) 2025 Ronnie Garrison
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
import json
import logging
from pathlib import Path
from typing import Dict, Optional
import click
from tqdm import tqdm
import os
# Create LICENSE.txt
license_text = __doc__  # Reuse docstring as license content
with open("LICENSE.txt", "w") as f:
    f.write(license_text)
print("MIT License written to LICENSE.txt")
# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
# Detect sandbox (iOS/macOS)
SANDBOXED = False
if 'APP_SANDBOX_CONTAINER_ID' in os.environ:
    SANDBOXED = True
    logging.info("Running in sandbox mode: file access limited to app container.")
class SymbolMapper:
    def __init__(self, symbol_file: str):
        self.symbols: Dict[str, str] = {}
        self.load_symbols(symbol_file)
    def load_symbols(self, symbol_file: str) -> None:
        path = Path(symbol_file)
        if SANDBOXED:
            documents_dir = Path.home() / "Documents"
            if not str(path).startswith(str(documents_dir)):
                raise PermissionError("Sandbox mode: access outside Documents is denied")
        if not path.exists():
            raise FileNotFoundError(f"Symbol file not found: {symbol_file}")
        with path.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(maxsplit=1)
                if len(parts) == 2:
                    addr, symbol = parts
                    self.symbols[addr] = symbol
        logging.info(f"Loaded {len(self.symbols)} symbols from {symbol_file}")
    def map_address(self, address: str) -> str:
        return self.symbols.get(address, f"<unknown:{address}>")
class PanicParser:
    def __init__(self, symbol_mapper: SymbolMapper):
        self.mapper = symbol_mapper
    def parse_file(self, panic_file: str) -> Dict:
        path = Path(panic_file)
        if SANDBOXED:
            documents_dir = Path.home() / "Documents"
            if not str(path).startswith(str(documents_dir)):
                raise PermissionError("Sandbox mode: access outside Documents is denied")
        if not path.exists():
            raise FileNotFoundError(f"Panic file not found: {panic_file}")
        with path.open() as f:
            lines = f.readlines()
        if not lines:
            raise ValueError("Panic file is empty")
        try:
            metadata = json.loads(lines[0])
        except json.JSONDecodeError:
            raise ValueError("First line must be valid JSON metadata")
        raw_log = "".join(lines[1:])
        mapped_log = self.map_addresses(raw_log)
        return {
            "metadata": metadata,
            "log": mapped_log
        }
    def map_addresses(self, raw_log: str) -> str:
        for addr in tqdm(self.mapper.symbols.keys(), desc="Mapping addresses"):
            if addr in raw_log:
                raw_log = raw_log.replace(addr, self.mapper.map_address(addr))
        return raw_log
@click.group()
@click.option('--verbose', is_flag=True, help="Enable verbose output")
def cli(verbose: bool):
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
@cli.group()
def parser():
    """Commands for parsing panic logs."""
@parser.command('parse')
@click.argument('panic_file')
@click.argument('symbol_file')
@click.option('--output', '-o', type=click.Path(), help="Optional output file to save results")
def parse_panic(panic_file: str, symbol_file: str, output: Optional[str]):
    try:
        mapper = SymbolMapper(symbol_file)
        parser_instance = PanicParser(mapper)
        result = parser_instance.parse_file(panic_file)
        formatted_result = json.dumps(result, indent=2)
        click.echo(formatted_result)
        if output:
            Path(output).write_text(formatted_result)
            logging.info(f"Results saved to {output}")
    except Exception as e:
        logging.error(f"Failed to parse panic file: {e}")
        raise click.ClickException(str(e))
if __name__ == "__main__":
    cli()