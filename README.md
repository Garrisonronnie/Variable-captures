# Variable Captures
**Author:** Ronnie Garrison
**License:** [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/)
**Status:** Stable & Usable on Windows
---
## 📌 Overview
`variable_captures.py` is a **sandbox-safe Python debugging and analysis tool** designed to make variable tracking, performance profiling, code inspection, and visualization easier and more professional.
This tool goes beyond simple debugging:
- It records variables and their lifetimes.
- It runs **heuristic-based anomaly checks** (e.g., empty containers, zero values, large memory objects).
- It builds **dependency graphs** between variables for clarity.
- It performs **CPU and memory profiling** on both synchronous and asynchronous functions.
- It runs **AST-based code analysis** to find variables, functions, classes, complexity, and style warnings.
- It can **export results** to JSON, CSV, or SQLite for persistence.  
It is **importable** as a module for use in larger projects or can be run **standalone** for testing.
---
## ⚙️ Features
✅ **Variable Tracking**
- Tracks values at runtime with timestamps and lifetimes.  
- Records usage counts and updates.
✅ **Automated Analysis**
- Heuristic warnings (e.g., empty containers, `None` values).
- Recommendations for fixes without AI dependencies.
- Severity levels (`info`, `warning`, `critical`).
✅ **Dependency Graphs**
- Visualize variable relationships with [NetworkX](https://networkx.org) + [Matplotlib](https://matplotlib.org).
✅ **Performance Profiling**
- CPU + memory usage tracking.
- Supports synchronous and asynchronous functions.
- Built-in `cProfile` integration.
✅ **AST Analysis**
- Extracts functions, variables, and classes.
- Estimates cyclomatic complexity.
- Reports basic style/code-smell warnings.
✅ **Persistence & Export**
- Save results to `variables.json`, `variables.csv`, or `variables.db` (SQLite).
---
## 🖥️ Installation (Windows)
Clone the repository into your workspace (example path:
`C:\Users\youruser\Documents\veritable-captures`):
```bash
git clone https://github.com/<your-username>/veritable-captures.git
cd veritable-captures
- python -m venv venv
- venv\Scripts\activate
- pip install -r requirements.txt
- python variable_captures.py
from variable_captures import VariableTracker
tracker = VariableTracker()
tracker.track_variable("x", 100)
tracker.track_variable("data", [1, 2, 3])
# Analyze results
print(tracker.analyze())
# Export to JSON
tracker.export_json("variables.json")
 
Example json
{
    "x": {
        "type": "int",
        "size_bytes": 28,
        "is_none": false,
        "timestamp": 1693951223.1234,
        "lifetime": {"created": 1693951223.1234, "last_updated": 1693951223.1234},
        "usage_count": 1,
        "heuristics": {},
        "recommendation": null
    }
}
# Additional details and setup use and Discription 
VariableTracker — Automated Python Variable & Code Analysis Tool
Description
VariableTracker is a comprehensive Python debugging and analysis utility designed to:
Track and monitor variables during program execution
Analyze memory usage, lifetimes, and usage patterns
Profile CPU and memory performance of functions (sync or async)
Parse Python source code to extract functions, classes, variables, and code complexity
Visualize variable dependencies with an interactive graph
Export collected data to JSON, CSV, and SQLite formats for further inspection
Ideal for developers who want deep insight into their Python code behavior, detect potential performance issues, or build tools based on static/dynamic code analysis.
Features
Automatic variable tracking with timestamps and dependencies
Memory usage analysis per variable
Heuristic checks and improvement recommendations
AST-based code structure and complexity analysis
Performance profiling with detailed CPU and memory stats
Visual dependency graphs using NetworkX and Matplotlib
Persistent export to popular data formats
Setup & Usage Guide
Prerequisites
Python 3.8 or higher installed on your machine
Basic familiarity with running Python scripts
1. Installing Python
Mac
Python 3 usually comes pre-installed. To check:
python3 --version
To install or upgrade, use Homebrew:
brew install python
Windows
Download the official installer from python.org
Run the installer and make sure to check “Add Python to PATH” during installation
Verify installation:
python --version
Linux (Ubuntu/Debian)
Install Python 3 and pip:
sudo apt update
sudo apt install python3 python3-pip
Verify:
python3 --version
2. Install Required Python Packages
Your script depends on several third-party libraries. Install them with:
pip install matplotlib networkx
3. Download or Create Your VariableTracker Script
Save your full script as, for example, variable_tracker.py
4. Using VariableTracker
Here's how to use your tool within your Python programs or interactively:
Example Usage
from variable_tracker import VariableTracker  # or import your class if in same file
tracker = VariableTracker()
# Track variables
tracker.track_variable("x", 42)
tracker.track_variable("y", {"x": 42, "z": 100})
# Analyze current tracked variables
results = tracker.analyze()
print(results)
# Visualize dependencies (will pop up a graph window)
tracker.visualize_dependencies()
# Profile performance of a function
def example_function(n):
    """Return squares from 0 to n-1."""
    return [i**2 for i in range(n)]
tracker.profile_performance(example_function, 10000)
# Analyze code with AST
code = """
def foo(a):
    b = a + 1
    return b
class Bar: pass
"""
ast_results = tracker.analyze_code(code)
print(ast_results)
# Export results to files
tracker.export_json("variables.json")
tracker.export_csv("variables.csv")
tracker.export_sqlite("variables.db")
5. Run Your Script
From the command line, navigate to the directory containing your script:
python variable_tracker.py
If you add an if __name__ == "__main__": block with example calls, this will execute automatically.
Tips
If visualization windows do not appear on Linux, ensure you have a GUI environment running.
Use virtual environments (python -m venv venv) to isolate dependencies.
For large projects, consider integrating this tracker into your unit tests or debugging workflows.
Summary
Step	Command/Action
Install Python	brew install python / official installer / apt install python3
Install dependencies	pip install matplotlib networkx
Save script	Save as variable_tracker.py
Run script	python variable_tracker.py
Use in your code	Import and call VariableTracker methods