import subprocess
import re
import time
import socket
import urllib.request
import urllib.parse
import json
import os
import signal
import sys
from pathlib import Path

# ============================================================
# CHECK INTERNET
# ============================================================

def internet_available():

    try:
        socket.create_connection(
            ("1.1.1.1", 53),
            timeout=3
        )
        return True

    except OSError:
        return False


# ============================================================
# RESTART SERVICE
# ============================================================
def restart_service():
    try:
        subprocess.run(
            ["systemctl", "restart", "autotunel.service"],
            check=False,
            capture_output=True,
            text=True,
            timeout=30
        )
        print("✅ Đã chạy lệnh: systemctl restart autotunel.service")
    except Exception as e:
        print("❌ Không thể chạy lệnh restart autotunel.service:", e)


# ============================================================
# Load config
# ============================================================
def load_env_file():
    env_path = Path(__file__).resolve().parent / ".env"

    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        elif value.startswith("'") and value.endswith("'"):
            value = value[1:-1]

        os.environ.setdefault(key, value)