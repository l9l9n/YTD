import subprocess
import sys
import os

def find_venv_python():
    for name in ("venv", "env1", ".venv", "env"):
        python = os.path.join(name, "Scripts", "python.exe")  # Windows
        if os.path.exists(python):
            return python
        python = os.path.join(name, "bin", "python")  # Linux / macOS
        if os.path.exists(python):
            return python
    return sys.executable  # fallback — системный Python

venv_python = find_venv_python()
subprocess.run([venv_python, "main.py"])
