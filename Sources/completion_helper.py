"""
MIT License

Copyright (c) 2025 Your Name

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

import os
import subprocess
from pathlib import Path

SHELL_CONFIGS = {
    'bash': Path('~/.bashrc').expanduser(),
    'zsh': Path('~/.zshrc').expanduser(),
    'fish': Path('~/.config/fish/config.fish').expanduser(),
}

def detect_shell():
    shell = os.environ.get('SHELL', '')
    if 'zsh' in shell:
        return 'zsh'
    elif 'bash' in shell:
        return 'bash'
    elif 'fish' in shell:
        return 'fish'
    return None

def backup_config(shell):
    config_path = SHELL_CONFIGS.get(shell)
    if config_path and config_path.exists():
        backup_path = config_path.with_suffix(config_path.suffix + '.bak')
        if not backup_path.exists():
            try:
                config_path.replace(backup_path)
                print(f"[INFO] Backup created: {backup_path}")
            except Exception as e:
                print(f"[WARNING] Could not create backup for {config_path}: {e}")
        else:
            print(f"[INFO] Backup already exists: {backup_path}")
    else:
        print(f"[INFO] No configuration file found for {shell} at {config_path}")

def run_original_completion_installer():
    try:
        # Call pymobiledevice3 CLI with install_completions command
        subprocess.run(['pymobiledevice3', 'install_completions'], check=True)
        print("[INFO] Original completion installer ran successfully.")
    except FileNotFoundError:
        print("[ERROR] 'pymobiledevice3' command not found in PATH.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Completion installation failed with exit code {e.returncode}")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")

def main():
    shell = detect_shell()
    if shell:
        print(f"[INFO] Detected shell: {shell}")
        backup_config(shell)
    else:
        print("[INFO] Could not detect active shell. Continuing without backup.")

    run_original_completion_installer()

    print("[INFO] Completion installation process complete. Please restart your terminal.")

if __name__ == '__main__':
    main()
