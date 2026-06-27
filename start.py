import subprocess
import sys
import os

venv_python = os.path.join("env1", "Scripts", "python.exe")

# Запускаем основной скрипт внутри виртуального окружения
subprocess.run([venv_python, "main.py"])