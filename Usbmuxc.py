#!/usr/bin/env python3
"""
usbmuxc.py - A standalone, production-safe companion module for pymobiledevice3-based tools.
Provides diagnostics, logging, environment checks, and safe wrappers
for USBMUXD/iOS device interactions.
Author: Ronnie Garrison
License: MIT License
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
import platform
import subprocess
from typing import List, Optional, Dict
try:
    from pymobiledevice3 import usbmux
except ImportError:
    usbmux = None
def setup_logger(name: str = "usbmuxc", log_file: str = "usbmuxc.log", level=logging.INFO) -> logging.Logger:
    """
    Sets up and returns a logger instance.
    Args:
        name (str): Logger name.
        log_file (str): Path to the log file.
        level (int): Logging level.
    Returns:
        logging.Logger: Configured logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.hasHandlers():
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
    return logger
logger = setup_logger()
def is_macos() -> bool:
    """Return True if the current system is macOS."""
    return platform.system() == "Darwin"
def is_linux() -> bool:
    """Return True if the current system is Linux."""
    return platform.system() == "Linux"
def is_windows() -> bool:
    """Return True if the current system is Windows."""
    return platform.system() == "Windows"
def check_usbmuxd_running() -> bool:
    """
    Verify if usbmuxd is active on supported platforms.
    Returns:
        bool: True if running or supported natively (macOS), False otherwise.
    """
    if is_linux():
        try:
            subprocess.check_output(["pgrep", "usbmuxd"], stderr=subprocess.STDOUT)
            logger.info("usbmuxd process is running.")
            return True
        except subprocess.CalledProcessError:
            logger.warning("usbmuxd is not running.")
            return False
        except FileNotFoundError:
            logger.error("pgrep command not found. Cannot check usbmuxd status.")
            return False
    if is_macos():
        logger.info("macOS detected; usbmuxd managed by system services.")
        return True
    if is_windows():
        logger.warning("Windows detected; usbmuxd is not natively supported for USB communication.")
        return False
    logger.warning("Unknown platform detected.")
    return False
def list_connected_devices(usbmux_address: Optional[str] = None) -> List[Dict[str, object]]:
    """
    List connected iOS devices using pymobiledevice3.
    Args:
        usbmux_address (Optional[str]): Custom usbmuxd socket address (if any).
    Returns:
        List[Dict[str, object]]: List of connected device info dictionaries.
    Raises:
        RuntimeError: If pymobiledevice3 is not installed.
        Exception: On connection or communication errors.
    """
    if usbmux is None:
        raise RuntimeError("pymobiledevice3 is not installed. Please install it to list devices.")
    try:
        devices = usbmux.list_devices(usbmux_address=usbmux_address)
        logger.info(f"{len(devices)} device(s) detected.")
        result = []
        for device in devices:
            info = {
                "serial": device.serial,
                "usb": device.is_usb,
                "network": device.is_network,
                "connection_type": device.connection_type,
            }
            logger.debug(f"Device info: {info}")
            result.append(info)
        return result
    except Exception as exc:
        logger.exception("Failed to list connected devices.")
        raise
def run_diagnostics() -> None:
    """
    Run a diagnostic routine to validate environment and list devices.
    Outputs results via logger and stdout.
    """
    logger.info("Running usbmuxc diagnostics.")
    logger.info(f"Platform: {platform.system()} {platform.release()}")
    if not check_usbmuxd_running():
        print("usbmuxd is not running or not supported on this platform.")
        return
    try:
        devices = list_connected_devices()
        if not devices:
            print("No iOS devices detected.")
        else:
            print("Connected iOS devices:")
            for device in devices:
                print(f" - UDID: {device['serial']} ({device['connection_type']})")
    except Exception as exc:
        print(f"Device detection failed: {exc}")
def main() -> None:
    """
    CLI entry point for standalone execution.
    """
    import argparse
    parser = argparse.ArgumentParser(
        description="usbmuxc - USBMUX Diagnostic and Device Utility"
    )
    parser.add_argument(
        "--diagnostics", action="store_true", help="Run environment diagnostics."
    )
    parser.add_argument(
        "--list", action="store_true", help="List connected iOS devices."
    )
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug-level logging output."
    )
    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled.")
    if args.diagnostics:
        run_diagnostics()
    elif args.list:
        try:
            devices = list_connected_devices()
            if not devices:
                print("No iOS devices detected.")
            else:
                for dev in devices:
                    print(dev)
        except Exception as exc:
            print(f"Error: {exc}")
    else:
        parser.print_help()
if __name__ == "__main__":
    main()
