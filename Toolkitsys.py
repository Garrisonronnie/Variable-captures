#!/usr/bin/env python3
# MIT License
# Copyright (c) 2025 Ronnie Garrison
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from typing import Any, List
from rich.panel import Panel
from rich.text import Text
from rich.console import Group
from .toolkit import RichToolkit
class ExtendedRichToolkit(RichToolkit):
    """
    An extended toolkit built on top of RichToolkit, providing higher-level
    utility methods for styled terminal output using the Rich library.
    """
    def print_panel(self, title: str, content: str, **metadata: Any) -> None:
        """
        Displays the given content in a stylized Rich panel with a title.
        Args:
            title (str): Title of the panel.
            content (str): Content to display inside the panel.
            **metadata: Optional parameters like expand, border_style, etc.
        """
        rendered_content = self.style.render_element(content, **metadata)
        rendered_title = self.style.render_element(title, title=True)
        panel = Panel(
            rendered_content,
            title=rendered_title,
            expand=metadata.get("expand", False),
            border_style=metadata.get("border_style", "dim"),
            padding=(1, 2),
        )
        self.console.print(panel)
    def alert(self, message: str, level: str = "info", *, icon: bool = True) -> None:
        """
        Prints a stylized alert message with severity level indicators.
        Args:
            message (str): The alert message.
            level (str): One of 'info', 'warning', 'error', 'success'. Default is 'info'.
            icon (bool): If True, includes a symbolic prefix (text-based). Default is True.
        """
        level = level.lower()
        level_config = {
            "info":    {"color": "cyan", "symbol": "INFO"},
            "warning": {"color": "yellow", "symbol": "WARN"},
            "error":   {"color": "red", "symbol": "ERROR"},
            "success": {"color": "green", "symbol": "OK"},
        }
        config = level_config.get(level, {"color": "white", "symbol": ""})
        symbol = f"{config['symbol']}: " if icon and config['symbol'] else ""
        styled = Text(f"{symbol}{message}", style=f"{config['color']} bold")
        self.console.print(styled)
    def print_boxed_list(self, title: str, items: List[str], *, bullet: str = "-") -> None:
        """
        Displays a titled list of items inside a boxed panel with bullets.
        Args:
            title (str): Title of the list.
            items (List[str]): List of strings to display.
            bullet (str): Bullet symbol for list items. Default is '-'.
        """
        if not items:
            self.alert("No items to display.", level="warning")
            return
        lines = [f"{bullet} {item}" for item in items]
        group = Group(*[Text(line) for line in lines])
        self.print_panel(title, group)