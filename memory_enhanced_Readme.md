# 📘 memory_status_enhanced
### 🔍 Enhanced Interface for Memory Monitoring and Diagnostics
`memory_status_enhanced` is a high-level Python wrapper around the low-level `memory_status`
module. It provides a clean, safe, and extensible interface for accessing system memory statistics
such as page states, memory pressure, compression activity, and more.
This module is designed for developers, system engineers, and monitoring tools that need
a robust interface for working with structured memory data.
---
## 🚀 Features
- ✅ **Safe Initialization** with exception handling  
- ✅ **Detailed Summary Reports** via `.summary()` methods  
- ✅ **Clear Text & Debug Output** with `__repr__` and `__str__`  
- ✅ **Memory Pressure Detection** via `.is_under_pressure()`  
- ✅ **Full Access to Page Statistics** (active, inactive, purgeable, wired, etc.)  
- ✅ **Drop-in Compatible** with the original `memory_status` module  
- ✅ **Logging Support** for debugging and observability  
- ✅ **Fully Typed** for type checking and IDE support  
---
## 📦 Installation
To use this module, ensure you have access to the base `memory_status` module:
```bash
# Hypothetical install command — replace with actual source
pip install memory-status-lib
🛠️ Usage
How to Use in Real World
Install psutil:
pip install psutil
Run via CLI:
python memory_status_enhanced.py
Log to file:
python memory_status_enhanced.py --json --logfile mem_status.log
 # example
Importing
from memory_status_enhanced import MemoryStatus
Example: Load and Inspect Memory Status
from memory_status_enhanced import MemoryStatus
import json
# Replace with your actual JSON source
mock_data = {
    "__compressor_size": 2048,
    "__compressions": 1234,
    "__decompressions": 567,
    "__busy_buffer_count": 8,
    "__memory_pressure": True,
    "__size": 102400,
    "__wanted": 2048,
    "__reclaimed": 1024,
    "__active": 4096,
    "__throttled": 128,
    "__file_backed": 8192,
    "__wired": 2048,
    "__purgeable": 512,
    "__inactive": 1024,
    "__free": 2048,
    "__speculative": 512
}
status = MemoryStatus(mock_data)
# Check if the system is under memory pressure
if status.is_under_pressure():
    print("⚠️ System is under memory pressure!")
# Get full structured output
print(json.dumps(status.summary(), indent=4))
🧩 Module Structure
MemoryStatus (Enhanced)
Property	Description
compressor_size	Size of memory compressor (int)
compressions	Number of compression operations (int)
decompressions	Number of decompressions (int)
busy_buffer_count	Number of busy buffers (int)
memory_pressure	Whether system is under memory pressure (bool)
pages_info	Returns an enhanced PagesInfo object
summary()	Returns all data as a clean dict
is_under_pressure()	Returns True if memory pressure is present
PagesInfo (Enhanced)
Property	Description
size	Total memory size (int)
active, inactive	Memory page states (int)
free, wired, purgeable, file_backed	Page types
summary()	Returns page state info as dict