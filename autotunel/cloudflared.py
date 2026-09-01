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
# STOP CLOUDFLARED
# ============================================================

def stop_cloudflared():

    global cloudflared_process

    if cloudflared_process is None:
        return

    print("🛑 Đang dừng Cloudflare Tunnel...")

    try:

        cloudflared_process.terminate()

        cloudflared_process.wait(
            timeout=5
        )

    except subprocess.TimeoutExpired:

        cloudflared_process.kill()

    except Exception as e:

        print(
            "Lỗi khi dừng cloudflared:",
            e
        )

    cloudflared_process = None

    print("✅ Cloudflare Tunnel đã dừng")


# ============================================================
# START CLOUDFLARE
# ============================================================

def start_cloudflared(nextcloud_url):

    global cloudflared_process

    print("🚀 Đang khởi động Cloudflare Tunnel...")

    command = [
        "cloudflared",
        "tunnel",
        "--url",
        nextcloud_url
    ]

    cloudflared_process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    cloudflare_url = None

    start_time = time.time()

    while time.time() - start_time < 30:

        line = cloudflared_process.stdout.readline()

        if not line:
            continue

        line = line.strip()

        if line:
            print(
                "[cloudflared]",
                line
            )

        # Tìm URL trycloudflare
        match = re.search(
            r"https://[a-zA-Z0-9.-]+\.trycloudflare\.com",
            line
        )

        if match:

            cloudflare_url = (
                match.group(0)
                .rstrip("/")
            )

            break

    if not cloudflare_url:

        print(
            "❌ Không tìm thấy Cloudflare URL"
        )

        stop_cloudflared()

        return None

    print("")
    print("======================================")
    print("🌐 Cloudflare URL:")
    print(cloudflare_url)
    print("======================================")

    # fix bug error generate url started
    if "https://api.trycloudflare.com" == cloudflare_url:
        print(
            "❌ Cloudflare URL không hợp lệ"
        )

        stop_cloudflared()
        restart_service()
        return None
    # Fix bug error generate url ended

    return cloudflare_url


# ============================================================
# UPDATE NEXTCLOUD
# ============================================================

def update_nextcloud(cloudflare_url):

    domain = cloudflare_url.replace(
        "https://",
        ""
    ).rstrip("/")

    print("")
    print(
        "🔧 Đang cập nhật Nextcloud:"
    )

    print(
        f"   trusted_domains = {domain}"
    )

    command = [
        "docker",
        "exec",
        "-u",
        "www-data",
        NEXTCLOUD_CONTAINER,
        "php",
        "occ",
        "config:system:set",
        "trusted_domains",
        "1",
        f"--value={domain}"
    ]

    try:

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30
        )

    except Exception as e:

        print(
            "❌ Không chạy được occ:",
            e
        )

        return False

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print(result.stderr)

    if result.returncode != 0:

        print(
            "❌ Cập nhật trusted_domains thất bại"
        )

        return False

    print(
        "✅ Nextcloud đã được cập nhật"
    )

    return True
