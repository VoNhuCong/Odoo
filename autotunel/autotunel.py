### `autotunel.py`
#!/usr/bin/env python3
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
import 
from pathlib import Path

# ============================================================
# LOAD ENV
# ============================================================
load_env_file()

# ============================================================
# CONFIG
# ============================================================

NEXTCLOUD_CONTAINER = os.getenv("NEXTCLOUD_CONTAINER", "nextcloud_app_1")
NEXTCLOUD_LOCAL_URL = os.getenv("NEXTCLOUD_LOCAL_URL", "http://192.168.0.6:8080")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")


CHECK_INTERNET_INTERVAL = 5

# ============================================================
# GLOBAL
# ============================================================

cloudflared_process = None


# ============================================================
# START EVERYTHING
# ============================================================

def start_tunnel():

    print("")
    print("======================================")
    print("🌐 INTERNET ĐÃ TRỞ LẠI")
    print("======================================")

    cloudflare_url = start_cloudflared(NEXTCLOUD_LOCAL_URL)

    if not cloudflare_url:

        print(
            "❌ Không thể tạo Cloudflare Tunnel"
        )

        return

    # Cho tunnel ổn định
    time.sleep(2)

    # Cập nhật Nextcloud
    nextcloud_ok = update_nextcloud(
        cloudflare_url
    )

    # Gửi Telegram
    if nextcloud_ok:

        message = (
            "🚀 Nextcloud Tunnel đã sẵn sàng\n\n"
            f"🔗 {cloudflare_url}\n\n"
            "✅ Nextcloud trusted_domains: OK"
        )

    else:

        message = (
            "⚠️ Cloudflare Tunnel đã tạo\n\n"
            f"🔗 {cloudflare_url}\n\n"
            "❌ Nextcloud trusted_domains: FAILED"
        )

    send_telegram(message)


# ============================================================
# MAIN MONITOR
# ============================================================

def main():
    global cloudflared_process

    # Kiểm tra trạng thái internet ban đầu
    previous_status = internet_available()

    #----------------------------------------------------
    if previous_status:
        print("🌐 Internet: ONLINE")
        start_tunnel()
    else:
        print("🔴 Internet: OFFLINE")

    # Liên tục kiểm tra trạng thái internet và gen tại cloudflare url khi internet trở lại
    while True:
        # sleep một khoảng thời gian trước khi kiểm tra lại trạng thái internet
        time.sleep(CHECK_INTERNET_INTERVAL)
        # Kiểm tra trạng thái internet hiện tại
        current_status = internet_available()

        # trang thái internet thay đổi từ online sang offline
        if previous_status and not current_status:
            print("INTERNET ĐÃ MẤT")
            stop_cloudflared()
        # trạng thái internet thay đổi từ offline sang online
        elif not previous_status and current_status:
            print("INTERNET ĐÃ TRỞ LẠI")
            start_tunnel()
        previous_status = current_status


# ============================================================
# CTRL+C
# ============================================================

def signal_handler(
    sig,
    frame
):

    print("")
    print(
        "🛑 Đang thoát chương trình..."
    )

    stop_cloudflared()

    sys.exit(0)


signal.signal(
    signal.SIGINT,
    signal_handler
)

signal.signal(
    signal.SIGTERM,
    signal_handler
)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()