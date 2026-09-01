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
# TELEGRAM
# ============================================================

def send_telegram(message):

    url = (
        f"https://api.telegram.org/"
        f"bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    )

    data = urllib.parse.urlencode({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }).encode()

    request = urllib.request.Request(
        url,
        data=data,
        method="POST"
    )

    # Sử dụng vòng lặp để thử gửi telegram nhiều lần nếu thất bại
    max_retries = 30

    for attempt in range(1, max_retries + 1):

        try:

            with urllib.request.urlopen(
                request,
                timeout=15
            ) as response:

                result = json.loads(
                    response.read().decode()
                )

            if result.get("ok"):

                print("✅ Telegram: gửi thành công")
                return True

            print(f"❌ Telegram error (attempt {attempt}/{max_retries}):")
            print(result)

        except Exception as e:

            print(
                f"❌ Không thể gửi Telegram (attempt {attempt}/{max_retries}):",
                e
            )

        if attempt < max_retries:
            time.sleep(5)

    print(
        f"❌ Đã thử gửi Telegram {max_retries} lần nhưng vẫn thất bại. Reset service right now..."
    )

    restart_service()

    return False