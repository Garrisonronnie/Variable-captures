# usbmuxc.py
A standalone, production-safe companion module and CLI tool for `pymobiledevice3`-based tools.  
Provides diagnostics, logging, environment checks, and safe wrappers for USBMUXD/iOS device interactions.
---
## Overview
`usbmuxc.py` helps developers and users who interact with iOS devices on macOS, Linux, and Windows by:
- Verifying that `usbmuxd` (the USB multiplexing daemon) is running.
- Listing connected iOS devices with detailed connection information.
- Running diagnostic checks to validate your environment for iOS device communication.
- Providing structured logging for easier debugging and tracking.
This tool is designed for integration with Python projects using `pymobiledevice3`, or as a standalone utility.
---
## Features
- **Cross-platform support:** macOS, Linux, and Windows (with caveats).
- **Automatic detection** of the USBMUX daemon status.
- **Device enumeration** with connection type and serial numbers.
- **Detailed logging** to both console and a file (`usbmuxc.log`).
- **Command-line interface (CLI)** for ease of use.
- **Graceful error handling** with clear messages.
---
## Requirements
- Python 3.7 or higher.
- [`pymobiledevice3`] (install via pip):
  
  ```bash
  pip install pymobiledevice3
Installation
Clone or download this repository and ensure Python 3 and dependencies are installed.
Optionally, add the script to your PATH or execute directly via:
python usbmuxc.py [options]
Usage
Run the script with the following command-line options:
Option	Description
--diagnostics	Run full environment diagnostics and device listing.
--list	List all connected iOS devices.
--debug	Enable debug-level logging output.
Examples
Run diagnostics (checks platform, usbmuxd status, lists devices):
python usbmuxc.py --diagnostics
List connected iOS devices only:
python usbmuxc.py --list
Run diagnostics with debug logs enabled:
python usbmuxc.py --diagnostics --debug
Show help/usage:
python usbmuxc.py --help
Logging
Logs are saved to usbmuxc.log in the script directory.
Output is also sent to the console.
Debug mode (--debug) provides detailed logs for troubleshooting.
Limitations
usbmuxd must be installed and running for device communication.
Windows support is limited because usbmuxd is not officially available natively.
The script requires pymobiledevice3; without it, device listing won’t work.
## Disclaimer
This script is **not** an original work but is inspired by the [`pymobiledevice3`](https://github.com/BlackJacx/pymobiledevice3) project.  
There is **no copyright infringement, cloning, or unauthorized copying** intended or implied.  
The original work has been left unaltered and unchanged where applicable, and proper attribution is provided to respect the original authors' rights and contributions.
 