# Panic ParserKit for macOS/iOS
A fully functional Panic Log ParserKit for macOS and iOS, built with Python 3.  
Supports both sandboxed environments (e.g., iOS/macOS apps) and full file access.
## Features
- Parses macOS/iOS kernel panic logs.
- Maps raw memory addresses to readable symbols.
- Works in sandboxed environments (restricts access to the `Documents` directory).
- Supports CLI usage.
- Outputs structured JSON metadata + decoded log.
## Requirements
- Python 3.8+
- See `requirements.txt` for dependencies.
## Installation
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
Usage
Basic command
python panic_parser.py parser parse <panic_file> <symbol_file> [--output OUTPUT]
Example
python panic_parser.py parser parse logs/panic.log symbols.txt -o parsed_output.json
Options
--verbose – Enable debug logging
--output, -o – Save the output JSON to a file
Symbol File Format
Your symbol file should contain address-symbol pairs, one per line:
0x1000 MainFunction
0x2000 HelperFunction
Panic Log Format
The panic log must have a first line that is valid JSON metadata. The rest is the raw log:
{"device": "iPhone12,1", "version": "iOS 15.0"}
panic(cpu 0 caller 0xfffffff00aabbcc): Kernel trap at 0x1000...
Notes
When sandboxed, file access is restricted to the user’s Documents folder.
Errors are logged and displayed in a user-friendly format.
## 🧠 What This Tool Does

This tool processes and analyzes **kernel panic logs** from macOS and iOS. It:

- Reads raw crash logs from devices
- Replaces low-level memory addresses with **human-readable symbols**
- Outputs structured, readable, JSON-formatted logs
- Works in **sandboxed environments**, limiting file access to `~/Documents`

---

## 💡 Why It's Needed

Kernel panic logs are filled with unreadable memory addresses like:

panic(cpu 0 caller 0xfffffff00aabbcc): Kernel trap at 0x1000...

yaml
Copy code

These are meaningless without symbolication.

**Symbolication** = Translating raw memory addresses into actual function or method names.

### This tool helps you:

- Debug system crashes effectively
- Trace logs back to the actual code that failed
- Use automation to process large numbers of crash logs
- Stay compatible with sandboxed environments like iOS apps

---

## ⚙️ How It Works examples 

### Step 1: Symbol File

A text file mapping memory addresses to function names:

0x1000 mainFunction
0x2000 helperFunction

bash
Copy code

### Step 2: Panic Log File

A crash log starting with a JSON metadata line, followed by the actual log:

```text
{"device": "iPhone12,1", "version": "iOS 15.0"}
panic(cpu 0 caller 0xfffffff00aabbcc): Kernel trap at 0x1000...
Step 3: Symbolication
The tool replaces every address like 0x1000 in the log with the mapped name from the symbol file (mainFunction, etc.).

Step 4: Output
Outputs a JSON object like:

json
Copy code
{
  "metadata": {
    "device": "iPhone12,1",
    "version": "iOS 15.0"
  },
  "log": "panic(cpu 0 caller 0xfffffff00aabbcc): Kernel trap at mainFunction..."
}
🚀 Command-Line Usage
bash
Copy code
python panic_parser.py parser parse <panic_file> <symbol_file> [--output OUTPUT]
Example:
bash
Copy code
python panic_parser.py parser parse logs/panic.log symbols.txt -o parsed_output.json
CLI Options:
--output, -o: Save result to a file

--verbose: Enable debug logging
