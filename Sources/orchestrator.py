#!/usr/bin/env python3
"""
Production-Ready Python Utility Orchestrator
============================================
Features:
- Dependency-aware DAG execution with parallelism
- Rich progress bars and live console feedback
- Retry logic with exponential backoff
- Logging + JSON dashboard export
- CLI fully integrated
MIT License
Copyright (c) 2025 [Ronnie Garrison]
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
import subprocess
import argparse
import json
import time
import sys
from pathlib import Path
from typing import List, Dict, Set
from concurrent.futures import ThreadPoolExecutor, as_completed
# Optional dependency
try:
    import yaml
except ImportError:
    print("PyYAML is required. Install via `pip install pyyaml`.", file=sys.stderr)
    raise
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
import logging
# ===== Configuration =====
DEFAULT_BUILD_FILE = Path("build.yaml")
DEFAULT_SCRIPT_FOLDER = Path("scripts")
DEFAULT_LOG_FOLDER = Path("logs")
DEFAULT_LOG_FILE = DEFAULT_LOG_FOLDER / "build.log"
DASHBOARD_FILE = DEFAULT_LOG_FOLDER / "dashboard.json"
MAX_RETRIES = 2
executed_scripts: Set[str] = set()
script_results: Dict[str, Dict] = {}
console = Console()
# ===== Logging Setup =====
DEFAULT_LOG_FOLDER.mkdir(parents=True, exist_ok=True)
LEVEL_MAP = {
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "success": logging.INFO
}
logging.basicConfig(
    filename=DEFAULT_LOG_FILE,
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
def log_message(message: str, level: str = "info") -> None:
    """Log messages to file and console."""
    logging.log(LEVEL_MAP.get(level.lower(), logging.INFO), message)
    console.print(f"[{level.upper()}] {message}")
# ===== Script Execution =====
def run_script(script: Path, retries: int = MAX_RETRIES) -> bool:
    """Run a script with retries and backoff."""
    if not script.exists():
        log_message(f"Script {script} not found!", "error")
        script_results[script.name] = {
            "status": "not_found",
            "stdout": "",
            "stderr": "",
            "duration": "0s",
            "attempts": 0,
        }
        return False
    attempt = 0
    backoff = 1.0
    while attempt <= retries:
        log_message(f"Running {script} (Attempt {attempt + 1})", "info")
        start_time = time.time()
        try:
            if script.suffix == ".py":
                cmd = ["python3", str(script)]
            elif script.suffix in {".sh", ".bash"}:
                cmd = ["bash", str(script)]
            else:
                log_message(f"Unsupported script type: {script}", "error")
                script_results[script.name] = {
                    "status": "unsupported",
                    "stdout": "",
                    "stderr": "",
                    "duration": "0s",
                    "attempts": attempt + 1,
                }
                return False
            result = subprocess.run(cmd, capture_output=True, text=True)
            duration = time.time() - start_time
            script_results[script.name] = {
                "status": "success" if result.returncode == 0 else "failed",
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "duration": f"{duration:.2f}s",
                "attempts": attempt + 1,
            }
            if result.stdout.strip():
                log_message(result.stdout.strip(), "info")
            if result.stderr.strip():
                log_message(result.stderr.strip(), "warning")
            if result.returncode == 0:
                log_message(f"Finished {script} successfully", "success")
                return True
            else:
                attempt += 1
                if attempt <= retries:
                    log_message(f"Retrying {script} after {backoff:.1f}s...", "warning")
                    time.sleep(backoff)
                    backoff = min(backoff * 2, 30)
        except Exception as e:
            log_message(f"Error running script {script}: {e}", "error")
            script_results[script.name] = {
                "status": "error",
                "stdout": "",
                "stderr": str(e),
                "duration": "0s",
                "attempts": attempt + 1,
            }
            return False
    log_message(f"Script {script} failed after {retries + 1} attempts", "error")
    return False
# ===== Dependency Management =====
def load_dependencies(build_file: Path = DEFAULT_BUILD_FILE) -> Dict[str, List[str]]:
    if not build_file.exists():
        log_message(f"No build file found at {build_file}", "warning")
        return {}
    try:
        if build_file.suffix in [".yaml", ".yml"]:
            return yaml.safe_load(build_file) or {}
        else:
            return json.loads(build_file.read_text())
    except Exception as e:
        log_message(f"Failed to load build file {build_file}: {e}", "error")
        return {}
def detect_circular_dependencies(dependencies: Dict[str, List[str]]) -> bool:
    visited: Set[str] = set()
    stack: Set[str] = set()
    cycle_found = False
    def visit(node: str) -> bool:
        nonlocal cycle_found
        if node in stack:
            log_message(f"Circular dependency detected: {' -> '.join(list(stack))} -> {node}", "error")
            cycle_found = True
            return True
        if node in visited:
            return False
        stack.add(node)
        for dep in dependencies.get(node, []):
            visit(dep)
        stack.remove(node)
        visited.add(node)
        return False
    for script in dependencies.keys():
        visit(script)
    return cycle_found
def resolve_dependencies_parallel(dependencies: Dict[str, List[str]]) -> None:
    """Execute scripts respecting dependencies in parallel when possible."""
    in_degree = {s: len(dependencies.get(s, [])) for s in dependencies}
    ready = [s for s, deg in in_degree.items() if deg == 0]
    total_scripts = len(dependencies)
    with Progress(
        SpinnerColumn(),
        TextColumn("{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Running Scripts", total=total_scripts)
        with ThreadPoolExecutor() as executor:
            futures = {}
            while ready or futures:
                while ready:
                    s = ready.pop()
                    script_path = DEFAULT_SCRIPT_FOLDER / s
                    futures[executor.submit(run_script, script_path)] = s
                for future in as_completed(list(futures.keys())):
                    s = futures.pop(future)
                    executed_scripts.add(s)
                    progress.update(task, advance=1)
                    for dependent, deps in dependencies.items():
                        if s in deps:
                            in_degree[dependent] -= 1
                            if in_degree[dependent] == 0:
                                ready.append(dependent)
                    break
# ===== Dashboard & Logging =====
def clear_logs(log_file: Path = DEFAULT_LOG_FILE) -> None:
    if log_file.exists():
        log_file.unlink()
        console.print(f"[green]Logs cleared: {log_file}")
    else:
        console.print(f"[yellow]No logs found to clear.")
def print_dashboard(export_json: bool = True) -> None:
    table = Table(title="Build Dashboard")
    table.add_column("Script", style="cyan")
    table.add_column("Status")
    table.add_column("Duration")
    table.add_column("Attempts")
    for script, info in script_results.items():
        status = info["status"]
        color = "green" if status == "success" else "red"
        table.add_row(script, f"[{color}]{status}", info.get("duration", "N/A"), str(info.get("attempts", 0)))
    console.print(table)
    if export_json:
        try:
            DASHBOARD_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(DASHBOARD_FILE, "w") as f:
                json.dump(script_results, f, indent=2)
            log_message(f"Dashboard exported to {DASHBOARD_FILE}", "info")
        except Exception as e:
            log_message(f"Failed to export dashboard: {e}", "error")
# ===== CLI =====
def main():
    parser = argparse.ArgumentParser(description="Production-Ready Python Utility Orchestrator")
    parser.add_argument("--script", help="Run a specific script (with its dependencies)")
    parser.add_argument("--all", action="store_true", help="Run all scripts")
    parser.add_argument("--clear-logs", action="store_true", help="Clear logs")
    parser.add_argument("--no-parallel", action="store_true", help="Disable parallel execution")
    args = parser.parse_args()
    dependencies = load_dependencies(DEFAULT_BUILD_FILE)
    if detect_circular_dependencies(dependencies):
        sys.exit("Circular dependency detected. Aborting.")
    if args.clear_logs:
        clear_logs()
        return
    if args.script:
        if args.script not in dependencies:
            log_message(f"Script '{args.script}' not found in build.yaml", "error")
            sys.exit(1)
        resolve_dependencies_parallel({args.script: dependencies.get(args.script, [])})
    elif args.all:
        if dependencies:
            if args.no_parallel:
                for script in dependencies:
                    resolve_dependencies_parallel({script: dependencies.get(script, [])})
            else:
                resolve_dependencies_parallel(dependencies)
        else:
            log_message("No scripts to run.", "warning")
    else:
        parser.print_help()
        return
    print_dashboard(export_json=True)
    if any(info["status"] != "success" for info in script_results.values()):
        sys.exit(1)
if __name__ == "__main__":
    main()
