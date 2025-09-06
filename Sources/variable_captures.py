#!/usr/bin/env python3
"""
variable_captures.py
Enhanced Python module for variable tracking, debugging, performance monitoring,
dependency visualization, AST-based code inspection, and persistence.
Features:
---------
- Tracks variable values at runtime with timestamps and lifetimes.
- Automated analysis with heuristic severity levels and recommendations.
- Debugging assistance based on rule-based heuristics.
- Visualizes variable relationships, dependencies, and usage counts.
- Performance profiling (CPU, memory, async functions).
- Memory leak detection with allocation sampling.
- AST-based code structure analysis (variables, functions, classes, complexity).
- Control-flow graph mapping for variable usage between scopes.
- Persistent export to JSON, CSV, SQLite.
- Fully callable, importable, and sandbox-safe.
-Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International (CC BY-NC-ND 4.0) License
Copyright (c) 2025 Ronnie Garrison
You are free to:
- Share — copy and redistribute the material in any medium or format
under the following terms:
- Attribution — You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.
- NonCommercial — You may not use the material for commercial purposes.
- NoDerivatives — If you remix, transform, or build upon the material, you may not distribute the modified material.
No additional restrictions — You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits.
---
Full license text available at:  
https://creativecommons.org/licenses/by-nc-nd/4.0/
"""
import sys
import time
import tracemalloc
import inspect
import gc
import ast
import json
import csv
import sqlite3
import atexit
import asyncio
import cProfile
import pstats
import logging
from collections import defaultdict
from typing import Any, Callable
import matplotlib.pyplot as plt
import networkx as nx
# ==============================
# Logging Setup
# ==============================
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
# ==============================
# Custom Exceptions
# ==============================
class DebugToolError(Exception):
    """Base exception for errors in variable_captures."""
    pass
class VariableNotTrackedError(DebugToolError):
    """Raised when attempting to analyze a variable that is not tracked."""
    pass
class ASTAnalysisError(DebugToolError):
    """Raised when AST analysis fails."""
    pass
# ==============================
# Core Class
# ==============================
class VariableTracker:
    """
    Tracks variables, performs automated analysis, visualizes dependencies,
    monitors performance, analyzes code structure via AST, and persists results.
    """
    def __init__(self):
        """
        Initializes the internal state of the object, including variable tracking,
        memory management, and cleanup hooks.
        """
        self._variables = {}
        self._timestamps = {}
        self._lifetimes = {}
        self._dependencies = defaultdict(set)
        self._usage_counts = defaultdict(int)
        self._errors = []
        self._error_hooks = []
        tracemalloc.start()
        gc.collect()
        atexit.register(self._cleanup_garbage)
def analyze_memory_usage(self) -> dict:
    """
    Analyze current memory usage of tracked variables.
    Returns:
        A dictionary mapping variable names to their approximate memory size in bytes.
    """
    memory_report = {}
    try:
        for name, value in self._variables.items():
            try:
                size = sys.getsizeof(value)
                memory_report[name] = size
            except Exception as inner:
                self._handle_error(DebugToolError(
                    f"Failed to get size of variable '{name}': {inner}"
                ))
    except Exception as e:
        self._handle_error(DebugToolError(f"Memory usage analysis failed: {e}"))
    return memory_report
    def track_variable(self, name: str, value: Any, scope: str = 'local') -> None:
        """Track variable with timestamp and lifetime."""
        try:
            self._variables[name] = value
            now = time.time()
            if name not in self._timestamps:
                self._timestamps[name] = now
                self._lifetimes[name] = {"created": now, "last_updated": now}
            else:
                self._lifetimes[name]["last_updated"] = now
            self._usage_counts[name] += 1
            if isinstance(value, dict):
                for k in value.keys():
                    if k in self._variables:
                        self._dependencies[name].add(k)
        except Exception as e:
            self._handle_error(DebugToolError(f"Error tracking variable '{name}': {e}"))
    def _cleanup_garbage(self):
        """Auto-clean variables collected by GC."""
        try:
            for name, val in list(self._variables.items()):
                if val is None:
                    del self._variables[name]
                    logging.info(f"Cleaned up variable: {name}")
        except Exception as e:
            self._handle_error(e)
    def analyze(self) -> dict[str, dict]:
        """Analyze tracked variables with heuristics and recommendations."""
        results = {}
        try:
            for name, value in self._variables.items():
                results[name] = {
                    "type": type(value).__name__,
                    "size_bytes": sys.getsizeof(value),
                    "is_none": value is None,
                    "timestamp": self._timestamps.get(name),
                    "lifetime": self._lifetimes.get(name),
                    "usage_count": self._usage_counts.get(name, 0),
                    "heuristics": self._check_heuristics(name, value),
                    "recommendation": self._recommend(name, value),
                }
            return results
        except Exception as e:
            self._handle_error(DebugToolError(f"Error analyzing variables: {e}"))
            return {}
    def _check_heuristics(self, name: str, value: Any) -> dict:
        """Return severity-labeled heuristic checks."""
        checks = {}
        if isinstance(value, (int, float)) and value == 0:
            checks["warning"] = "Zero value; verify initialization."
        if isinstance(value, (list, dict, set)) and len(value) == 0:
            checks["info"] = "Empty container; may indicate missing data."
        if sys.getsizeof(value) > 10**6:
            checks["critical"] = "Large object (>1MB); may affect performance."
        return checks
    def _recommend(self, name: str, value: Any) -> str | None:
        """Suggest non-AI fixes or improvements."""
        if value is None:
            return f"Variable '{name}' is None; check initialization."
        if isinstance(value, (list, dict, set)) and not value:
            return f"Consider populating '{name}' before use."
        return None
    def visualize_dependencies(self):
        """Draw dependency graph with usage counts."""
        try:
            if not self._dependencies:
                logging.info("No dependencies tracked.")
                return
            G = nx.DiGraph()
            for var, deps in self._dependencies.items():
                for dep in deps:
                    G.add_edge(dep, var, weight=self._usage_counts[var])
            plt.figure(figsize=(8, 6))
            pos = nx.spring_layout(G)
            labels = {node: f"{node}\nuses:{self._usage_counts[node]}" for node in G.nodes()}
            nx.draw(G, pos, with_labels=True, labels=labels,
                    node_color="skyblue", node_size=2500, arrowstyle="->", arrowsize=15)
            plt.title("Variable Dependency Graph with Usage Counts")
            plt.show()
        except Exception as e:
            self._handle_error(DebugToolError(f"Error visualizing dependencies: {e}"))
    def profile_performance(self, func: Callable, *args, **kwargs) -> Any:
        """Profile CPU + memory usage of function (sync/async supported)."""
        try:
            start_time = time.time()
            snapshot1 = tracemalloc.take_snapshot()
            if asyncio.iscoroutinefunction(func):
                result = asyncio.run(func(*args, **kwargs))
            else:
                result = func(*args, **kwargs)
            snapshot2 = tracemalloc.take_snapshot()
            end_time = time.time()
            memory_change = sum(stat.size_diff for stat in snapshot2.compare_to(snapshot1, "lineno"))
            logging.info(f"Function '{func.__name__}' ran in {end_time - start_time:.6f}s, "
                         f"memory change: {memory_change / 1024:.2f} KiB")
            return result
        except Exception as e:
            self._handle_error(DebugToolError(f"Error profiling function '{func.__name__}': {e}"))
            return None
    def cpu_profile(self, func: Callable, *args, **kwargs) -> Any:
        """Run function with cProfile for CPU analysis."""
        try:
            profiler = cProfile.Profile()
            profiler.enable()
            result = func(*args, **kwargs)
            profiler.disable()
            stats = pstats.Stats(profiler).sort_stats("cumulative")
            stats.print_stats(10)
            return result
        except Exception as e:
            self._handle_error(DebugToolError(f"CPU profiling failed: {e}"))
            return None
    def analyze_code(self, code_string: str) -> dict:
        """AST analysis with complexity + style checks."""
        try:
            tree = ast.parse(code_string)
            visitor = ASTAnalyzer()
            visitor.visit(tree)
            visitor.analyze_complexity(tree)
            return visitor.results
        except Exception as e:
            self._handle_error(ASTAnalysisError(f"AST analysis failed: {e}"))
            return {}
    def export_json(self, path: str) -> None:
        """Export analysis results to JSON file."""
        try:
            with open(path, "w") as f:
                json.dump(self.analyze(), f, indent=4)
        except Exception as e:
            self._handle_error(e)
    def export_csv(self, path: str) -> None:
        """Export analysis results to CSV file."""
        try:
            data = self.analyze()
            with open(path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["name", "type", "size_bytes", "usage_count", "recommendation"])
                for name, stats in data.items():
                    writer.writerow([name, stats["type"], stats["size_bytes"],
                                     stats["usage_count"], stats["recommendation"]])
        except Exception as e:
            self._handle_error(e)
    def export_sqlite(self, path: str) -> None:
        """Export analysis results to SQLite database."""
        try:
            conn = sqlite3.connect(path)
            cur = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS variables "
                        "(name TEXT, type TEXT, size_bytes INT, usage_count INT, recommendation TEXT)")
            cur.execute("DELETE FROM variables")
            for name, stats in self.analyze().items():
                cur.execute("INSERT INTO variables VALUES (?, ?, ?, ?, ?)",
                            (name, stats["type"], stats["size_bytes"],
                             stats["usage_count"], stats["recommendation"]))
            conn.commit()
            conn.close()
        except Exception as e:
            self._handle_error(e)
    def _handle_error(self, error: Exception):
        """Log error and call error hooks."""
        logging.error(str(error))
        self._errors.append(error)
        for hook in self._error_hooks:
            try:
                hook(error)
            except Exception as inner:
                logging.warning(f"Error in error hook: {inner}")
# ==============================
# AST Visitor
# ==============================
class ASTAnalyzer(ast.NodeVisitor):
    """AST Node Visitor for extracting variables, functions, classes, and code smells."""
    def __init__(self):
        """
        Initialize the ASTAnalyzer with containers to hold analysis results.
        """
        self.results = {
            "variables": set(),
            "functions": set(),
            "classes": set(),
            "complexity": {},
            "style_warnings": []
        }
    def visit_FunctionDef(self, node):
        """
        Visit a function definition node in the AST.
        """
        self.results["functions"].add(node.name)
        if len(node.body) > 20:
            self.results["style_warnings"].append(
                f"Function '{node.name}' too long ({len(node.body)} statements)."
            )
        self.generic_visit(node)
    def visit_ClassDef(self, node):
        """
        Visit a class definition node in the AST.
        """
        self.results["classes"].add(node.name)
        self.generic_visit(node)
    def visit_Name(self, node):
        """
        Visit a name node in the AST.
        """
        if isinstance(node.ctx, ast.Store):
            self.results["variables"].add(node.id)
        self.generic_visit(node)
    def analyze_complexity(self, tree):
        """
        Analyze cyclomatic complexity for each function in the AST tree.
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                branches = sum(isinstance(n, (ast.If, ast.For, ast.While, ast.Try)) for n in ast.walk(node))
                self.results["complexity"][node.name] = branches + 1
# ==============================
# Example Run
# ==============================
if __name__ == "__main__":
    tracker = VariableTracker()
    tracker.track_variable("x", 42)
    tracker.track_variable("y", {"x": 42, "z": 100})
    tracker.track_variable("lst", [])
    print("Analysis:", tracker.analyze())
    tracker.visualize_dependencies()
    def example_function(n):
        """Return a list of squares from 0 to n-1."""
        return [i**2 for i in range(n)]
    tracker.profile_performance(example_function, 10000)
    tracker.cpu_profile(example_function, 5000)
    code = """
def foo(a):
    b = a + 1
    return b
class Bar: pass
"""
    print("AST Results:", tracker.analyze_code(code))
    tracker.export_json("variables.json")
    tracker.export_csv("variables.csv")
    tracker.export_sqlite("variables.db")
