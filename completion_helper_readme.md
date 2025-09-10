# Shell Completion Installer Backup Script
# completion_helper
## Overview

This Python script assists with safely installing shell completions for the `pymobiledevice3` tool by:

- Detecting the user's active shell (`bash`, `zsh`, or `fish`).
- Backing up the corresponding shell configuration file (`~/.bashrc`, `~/.zshrc`, or `~/.config/fish/config.fish`) before any modifications.
- Running the original `pymobiledevice3 install_completions` command to install completions.
- Informing the user of the process status and any errors encountered.

By creating a backup of the shell configuration, it prevents accidental loss of user customizations.

---

## Features

- **Shell detection**: Automatically detects the active shell environment.
- **Backup creation**: Creates a `.bak` backup of the shell configuration file if it exists.
- **Error handling**: Gracefully handles missing configuration files, backup failures, and errors from the completion installer command.
- **User feedback**: Prints informative messages to guide the user throughout the process.

--- 

## Installation

1. Ensure you have Python 3 installed on your system.
2. Make sure `pymobiledevice3` is installed and available in your system PATH.
3. Download or clone this script to your local machine.
git clone https://github.com/Garrisonronnie/python-Helper-library.git

---

## Usage

Run the script using Python from your terminal:

```bash
python path/to/your_script.py
