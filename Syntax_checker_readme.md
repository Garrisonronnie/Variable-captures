Script Syntax Checker Framework

Author: Ronnie Garrison
License: MIT
Repository: github.com/Garrisonronnie/python-Helper-library

A multi-language, modular script syntax checking framework for validating and analyzing scripts using static and AI-assisted tools. Supports Python, Bash, Batch, and PowerShell with optional OpenAI-based review, file change detection, and structured logging.

🔧 Features

Multi-language support:

Python (.py)

Bash (.sh)

Batch (.bat, .cmd)

PowerShell (.ps1)

Syntax validation:

Python: AST-based parsing

Bash: bash -n static check

Batch & PowerShell: Stubs ready for extension

Safe path filtering: Ignores sensitive/system directories by default

Skip unchanged files: Uses SHA256 hash cache to skip files that haven’t changed

Dry-run mode: Preview matched files without running analysis

AI-powered analysis (optional):

OpenAI API integration (e.g. GPT-3.5/GPT-4)

Single-issue feedback per script

Auto fallback if OpenAI not configured

Structured logging:

Time-stamped logs of all issues

Written to disk in a dedicated log directory

Modular architecture:

Centralized, callable process_scripts() function

Designed for reuse in larger automation or testing pipelines

📦 Installation
1. Clone the repository
git clone https://github.com/Garrisonronnie/python-Helper-library.git
cd python-Helper-library

2. (Optional) Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install dependencies
pip install -r requirements.txt


Note: If using OpenAI features, set your API key as an environment variable:
OPENAI_API_KEY=your-key-here

🚀 Usage
CLI (Command-Line Interface)
python ai_script_checker.py --dir "C:/scripts" --skip-unchanged --report

Common Options
Option	Description
--dir	Directory to scan (default: C:/)
--ext .py .sh	File extensions to include
--max-size 50	Max file size in KB (default: 50)
--dry-run	Preview files without analyzing
--skip-unchanged	Use file hash cache to skip unchanged files
--report	Output summary as JSON
--model gpt-4	Select OpenAI model (default: gpt-3.5-turbo)
Example: Analyze Python and Shell scripts only
python ai_script_checker.py --dir "/projects/scripts" --ext .py .sh --model gpt-4

🔍 Programmatic Use
from ai_script_checker import process_scripts

summary = process_scripts(
    search_dir="C:/my/scripts",
    skip_unchanged=True,
    report=True,
    model="gpt-3.5-turbo"
)
print(summary)

📄 License

This project is licensed under the MIT License
.

📁 Repository

GitHub: https://github.com/Garrisonronnie/python-Helper-library