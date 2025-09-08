#!/usr/bin/env python3
# memory_status_enhanced.py
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
import logging
import psutil
from typing import Any, Dict
import platform
# Logger Configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)
# ---------------------------
# PagesInfo (real memory info)
# ---------------------------
class PagesInfo:
    """Wraps low-level memory statistics using psutil for cross-platform support."""
    def __init__(self) -> None:
        vm = psutil.virtual_memory()
        sm = psutil.swap_memory()
        self.total = vm.total
        self.available = vm.available
        self.used = vm.used
        self.free = vm.free
        self.active = getattr(vm, "active", 0)
        self.inactive = getattr(vm, "inactive", 0)
        self.wired = getattr(vm, "wired", 0)  # macOS only
        self.buffers = getattr(vm, "buffers", 0)  # Linux only
        self.cached = getattr(vm, "cached", 0)  # Linux only
        self.swap_total = sm.total
        self.swap_used = sm.used
        self.swap_free = sm.free
    def summary(self) -> Dict[str, int]:
        return {
            "total": self.total,
            "available": self.available,
            "used": self.used,
            "free": self.free,
            "active": self.active,
            "inactive": self.inactive,
            "wired": self.wired,
            "buffers": self.buffers,
            "cached": self.cached,
            "swap_total": self.swap_total,
            "swap_used": self.swap_used,
            "swap_free": self.swap_free,
        }
    def __repr__(self) -> str:
        return f"<PagesInfo(total={self.total}, used={self.used}, free={self.free})>"
    def __str__(self) -> str:
        return f"PagesInfo Summary: {self.summary()}"
# ---------------------------
# MemoryStatus
# ---------------------------
class MemoryStatus:
    """Provides structured system memory inspection."""
    def __init__(self) -> None:
        self.__pages_info = PagesInfo()
        self.memory_pressure = self.__calculate_pressure()
    def __calculate_pressure(self) -> bool:
        """Determine memory pressure heuristically."""
        try:
            percent_used = psutil.virtual_memory().percent
            return percent_used > 85  # Adjustable threshold
        except Exception as e:
            logger.error("Failed to calculate memory pressure: %s", e)
            return False
    @property
    def pages_info(self) -> PagesInfo:
        return self.__pages_info
    def is_under_pressure(self) -> bool:
        return self.memory_pressure
    def summary(self) -> Dict[str, Any]:
        return {
            "under_pressure": self.memory_pressure,
            "pages_info": self.__pages_info.summary(),
        }
    def __repr__(self) -> str:
        return f"<MemoryStatus(under_pressure={self.memory_pressure})>"
    def __str__(self) -> str:
        return f"MemoryStatus Summary: {self.summary()}"
# ---------------------------
# Utility Functions
# ---------------------------
def get_memory_status_summary() -> Dict[str, Any]:
    """Convenience function to return memory summary."""
    try:
        status = MemoryStatus()
        return status.summary()
    except Exception as e:
        logger.error("Failed to create memory summary: %s", e)
        return {"error": str(e)}
# ---------------------------
# CLI Support
# ---------------------------
if __name__ == "__main__":
    import json
    import argparse
    parser = argparse.ArgumentParser(description="System Memory Status Tool")
    parser.add_argument('--json', action='store_true', help="Output in JSON format")
    parser.add_argument('--logfile', type=str, help="Save output to a log file")
    args = parser.parse_args()
    status_summary = get_memory_status_summary()
    if args.json:
        output = json.dumps(status_summary, indent=4)
    else:
        output = str(MemoryStatus())
    print(output)
    if args.logfile:
        try:
            with open(args.logfile, 'a') as f:
                f.write(output + "\n")
            logger.info("Memory status logged to %s", args.logfile)
        except Exception as e:

            logger.error("Failed to write log file: %s", e)
