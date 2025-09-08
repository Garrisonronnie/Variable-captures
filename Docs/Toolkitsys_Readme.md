# ToolkitSys
**ToolkitSys** is a Python-based terminal toolkit library, providing advanced and stylized terminal output features. It extends the functionality of a base `RichToolkit` to make terminal interfaces more visually appealing, interactive, and user-friendly.
---
## Features
ToolkitSys provides the following key utilities:
1. **Stylized Panels**
- Display content in beautifully formatted panels with customizable titles, borders, padding, and styles.
- Supports metadata like `expand` and `border_style` for advanced customization.
2. **Alert System**
- Print alert messages with severity levels (`info`, `warning`, `error`, `success`).
- Optional symbolic icons for clear and intuitive visual feedback.
- Color-coded messages for easy recognition in terminal output.
3. **Boxed Lists**
- Display lists of items inside a boxed panel with customizable bullet symbols.
- Automatically handles empty lists with a warning alert.
---
## Installation
ToolkitSys requires Python 3.9+ and the `rich` library. You can install dependencies via pip:
```bash
pip install rich
# Usage examples 
from toolkitsys import ExtendedRichToolkit
toolkit = ExtendedRichToolkit()
# Display a panel
toolkit.print_panel("Welcome", "This is a styled Rich panel!")
# Show alerts
toolkit.alert("Informational message", level="info")
toolkit.alert("Check your inputs!", level="warning")
toolkit.alert("Operation failed", level="error")
toolkit.alert("Operation succeeded", level="success")
# Display a boxed list
toolkit.print_boxed_list("Tasks", ["Task 1", "Task 2", "Task 3"])
Legal
This project is licensed under the MIT License:
You are free to use, copy, modify, merge, publish, distribute, sublicense, and sell copies of the software.
You must include the copyright notice and license in all copies or substantial portions of the software.
The software is provided “as-is”, without warranty of any kind.
For the toolkitsys script you provided, the primary Python package requirement is:
rich – for styled terminal output, panels, text, and console rendering.
Install with:
pip install rich
To clone this or to download it and use it on your own build, use this link
git clone https://github.com/Garrisonronnie/python-Helper-library.git
