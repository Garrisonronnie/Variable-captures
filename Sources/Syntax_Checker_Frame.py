#!/usr/bin/env python3
"""
Script Syntax Checker Framework - Multi-language
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
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
DEALINGS IN THE SOFTWARE.
Framework: A collection of tools and libraries providing a structured
way to build applications.
Scans directories for scripts, performs hash-based change detection,
performs local syntax checks for Python, Bash, Batch, and PowerShell,
optionally uses OpenAI for advanced review, and logs issues found.
"""
from __future__ import annotations
import os
import sys
import time
import json
import hashlib
import argparse
import ast
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Generator, List, Dict, Union
# Optional OpenAI import
try:
    from openai import OpenAI
    openai_available = True
except ImportError:
    openai_available = False
# -------------------- Configuration --------------------
DEFAULT_EXTENSIONS: List[str] = [".py", ".sh", ".bat", ".cmd", ".ps1"]
DEFAULT_MAX_FILE_SIZE_KB: int = 50
DEFAULT_EXCLUDED_PATHS: List[str] = [
    "C:\\Windows", "C:\\Program Files", "C:\\Program Files (x86)",
    "C:\\ProgramData", "C:\\$Recycle.Bin", "C:\\System Volume Information",
    "C:\\Users\\All Users", "C:\\Recovery"
]
DEFAULT_MODEL: str = "gpt-3.5-turbo"
HASH_CACHE_FILE: str = "script_hashes.json"
# -------------------- Framework --------------------
class Framework:
    """A structured collection of tools and libraries to build applications."""
    @staticmethod
    def log(level: str, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level.upper()}] {message}")
    @staticmethod
    def init_log_file(log_path: Path) -> None:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "w", encoding="utf-8") as log_file:
            log_file.write("Script Error Report\n")
            log_file.write("=" * 60 + "\n")
    @staticmethod
    def log_issue(script_path: str, analysis: str, log_file: Path) -> None:
        with open(log_file, "a", encoding="utf-8") as log_f:
            log_f.write(f"\n[{time.ctime()}] Script: {script_path}\n\n")
            log_f.write(analysis + "\n")
            log_f.write("-" * 60 + "\n")
    @staticmethod
    def is_safe_path(path: str, excluded_paths: List[str]) -> bool:
        return not any(path.startswith(excluded) for excluded in excluded_paths)
    @staticmethod
    def hash_file(path: str) -> Optional[str]:
        try:
            with open(path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return None
    @staticmethod
    def load_hash_cache(path: Path) -> Dict[str, str]:
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    @staticmethod
    def save_hash_cache(path: Path, cache: Dict[str, str]) -> None:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2)
    @staticmethod
    def get_all_scripts(
        search_dir: str,
        extensions: List[str],
        max_file_size: int,
        excluded_paths: List[str]
    ) -> Generator[str, None, None]:
        for root, _, files in os.walk(search_dir):
            if not Framework.is_safe_path(root, excluded_paths):
                continue
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    full_path = os.path.join(root, file)
                    try:
                        if os.path.getsize(full_path) <= max_file_size:
                            yield full_path
                    except Exception:
                        continue
    @staticmethod
    def check_syntax_python(code: str) -> str:
        try:
            ast.parse(code)
            return "No syntax issues found."
        except SyntaxError as e:
            return f"SyntaxError: {e}"
    @staticmethod
    def check_syntax_bash(path: str) -> str:
        try:
            result = subprocess.run(["bash", "-n", path], capture_output=True, text=True)
            return result.stderr.strip() or "No syntax issues found."
        except Exception as e:
            return f"Error checking Bash syntax: {e}"
    @staticmethod
    def check_syntax_batch(path: str) -> str:
        # Batch static analysis is limited; placeholder
        return "Batch syntax check placeholder (manual review recommended)."
    @staticmethod
    def check_syntax_powershell(path: str) -> str:
        # PowerShell static analysis limited; placeholder
        return "PowerShell syntax check placeholder (manual review recommended)."
    @staticmethod
    def detect_and_check_syntax(path: str, code: str) -> str:
        if path.endswith(".py"):
            return Framework.check_syntax_python(code)
        elif path.endswith(".sh"):
            return Framework.check_syntax_bash(path)
        elif path.endswith(".bat") or path.endswith(".cmd"):
            return Framework.check_syntax_batch(path)
        elif path.endswith(".ps1"):
            return Framework.check_syntax_powershell(path)
        else:
            return "No local syntax checker available for this file type."
# -------------------- Analyzer --------------------
class ScriptAnalyzer:
    """Handles script analysis: local checks and optional AI review"""
    def __init__(self, model: str = DEFAULT_MODEL, use_ai: bool = False):
        self.model = model
        self.use_ai = use_ai and openai_available
        self.ok = False
        if self.use_ai:
            try:
                self.client = OpenAI()
                self.ok = True
            except Exception as e:
                Framework.log("error", f"OpenAI initialization failed: {e}")
                self.use_ai = False
        if not self.use_ai:
            Framework.log("info", "AI analysis disabled. Only local checks will run.")
    def analyze(self, code: str, path: str) -> str:
        # Local syntax check
        syntax_result = Framework.detect_and_check_syntax(path, code)
        if "issues" in syntax_result.lower():
            return syntax_result
        # AI analysis (optional)
        if not self.use_ai:
            return "Analysis completed (local only)."
        prompt = f"""
Review this script for errors or improvements. Return:
- Problematic lines (if any)
- Corrected version
- Explanation
If no issues, return "No issues found."
Script path: {path}
Script content:
{code}
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error analyzing script: {e}"
# -------------------- Main Processing --------------------
def process_scripts(
    search_dir: str = "C:/",
    log_dir: str = "C:/scripts_checked",
    extensions: Optional[List[str]] = None,
    max_file_size_kb: int = DEFAULT_MAX_FILE_SIZE_KB,
    excluded_paths: Optional[List[str]] = None,
    dry_run: bool = False,
    skip_unchanged: bool = False,
    report: bool = False,
    use_ai: bool = False,
    model: str = DEFAULT_MODEL
) -> Dict[str, Union[int, float, Optional[str]]]:
    start_time = time.time()
    extensions = extensions or DEFAULT_EXTENSIONS
    excluded_paths = excluded_paths or DEFAULT_EXCLUDED_PATHS
    max_file_size = max_file_size_kb * 1024
    log_dir_path = Path(log_dir)
    log_file = log_dir_path / "script_check_log.txt"
    hash_cache_path = log_dir_path / HASH_CACHE_FILE
    analyzer = ScriptAnalyzer(model=model, use_ai=use_ai)
    if not dry_run:
        Framework.init_log_file(log_file)
    hash_cache = Framework.load_hash_cache(hash_cache_path) if skip_unchanged else {}
    updated_cache: Dict[str, str] = {}
    stats = {"total": 0, "analyzed": 0, "issues": 0, "skipped": 0}
    for script_path in Framework.get_all_scripts(search_dir, extensions, max_file_size, excluded_paths):
        stats["total"] += 1
        script_path_str = str(script_path)
        file_hash = Framework.hash_file(script_path)
        updated_cache[script_path_str] = file_hash or ""
        if skip_unchanged and hash_cache.get(script_path_str) == file_hash:
            stats["skipped"] += 1
            continue
        if dry_run:
            Framework.log("info", f"Would analyze: {script_path}")
            continue
        try:
            with open(script_path, "r", encoding="utf-8", errors="ignore") as f:
                code = f.read()
            analysis = analyzer.analyze(code, script_path)
            stats["analyzed"] += 1
            if "no issues found" not in analysis.lower():
                stats["issues"] += 1
                Framework.log_issue(script_path, analysis, log_file)
        except Exception as e:
            Framework.log("error", f"Error reading {script_path}: {e}")
    if skip_unchanged and not dry_run:
        Framework.save_hash_cache(hash_cache_path, updated_cache)
    duration = round(time.time() - start_time, 2)
    summary = {
        "scanned": stats["total"],
        "analyzed": stats["analyzed"],
        "issues": stats["issues"],
        "skipped": stats["skipped"],
        "duration_sec": duration,
        "log_file": str(log_file) if not dry_run else None
    }
    if report:
        print(json.dumps(summary, indent=2))
    else:
        Framework.log("info", f"Scanned: {stats['total']}")
        Framework.log("info", f"Analyzed: {stats['analyzed']}")
        Framework.log("info", f"Issues found: {stats['issues']}")
        Framework.log("info", f"Skipped (unchanged): {stats['skipped']}")
        Framework.log("info", f"Duration: {duration} seconds")
        if not dry_run:
            Framework.log("info", f"Log file: {log_file}")
    return summary
# -------------------- CLI Entry --------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="Script syntax checker framework (multi-language, local and optional AI)")
    parser.add_argument("--dir", default="C:/", help="Directory to scan")
    parser.add_argument("--log-dir", default="C:/scripts_checked", help="Log file directory")
    parser.add_argument("--ext", nargs="+", help="File extensions to include (e.g. .py .sh)")
    parser.add_argument("--max-size", type=int, default=DEFAULT_MAX_FILE_SIZE_KB, help="Max file size (KB)")
    parser.add_argument("--skip-unchanged", action="store_true", help="Skip files that haven't changed")
    parser.add_argument("--dry-run", action="store_true", help="Scan without analyzing")
    parser.add_argument("--report", action="store_true", help="Output JSON summary")
    parser.add_argument("--use-ai", action="store_true", help="Enable AI-based analysis")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="OpenAI model to use (e.g. gpt-3.5-turbo)")
    args = parser.parse_args()
    process_scripts(
        search_dir=args.dir,
        log_dir=args.log_dir,
        extensions=args.ext,
        max_file_size_kb=args.max_size,
        skip_unchanged=args.skip_unchanged,
        dry_run=args.dry_run,
        report=args.report,
        use_ai=args.use_ai,
        model=args.model
    )
# -------------------- Entry Point --------------------
if __name__ == "__main__":

    main()
