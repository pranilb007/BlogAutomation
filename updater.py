import requests
import json
import os
import sys
import time
import shutil
import subprocess

# -----------------------------
# CONFIG
# -----------------------------
VERSION_FILE_URL = "https://raw.githubusercontent.com/pranilb007/BlogAutomation/main/updater/version.json"
LOCAL_VERSION = "1.0.7"
APP_EXE = "BlogAutomation.exe"
DOWNLOAD_TMP = "BlogAutomation_new.exe"
UPDATER_LAUNCHER = "update_launcher.py"
# -----------------------------


def check_for_update():
    try:
        r = requests.get(VERSION_FILE_URL, timeout=10)
        r.raise_for_status()

        text = r.content.decode("utf-8-sig").strip()
        data = json.loads(text)

        latest_version = data.get("version")
        download_url = data.get("download_url")

        if latest_version != LOCAL_VERSION:
            print(f"[UPDATE] New version available: {latest_version}")
            download_update(download_url)
            return True

        return False

    except Exception as e:
        print("Update check failed:", e)
        return False


def download_update(url):
    try:
        r = requests.get(url, stream=True)
        r.raise_for_status()
        with open(DOWNLOAD_TMP, "wb") as f:
            shutil.copyfileobj(r.raw, f)
        print(f"[UPDATE] Download completed: {DOWNLOAD_TMP}")
    except Exception as e:
        print("Download failed:", e)
        sys.exit(1)


def launch_updater():
    """Launch temporary updater to safely replace EXE"""

    launcher_code = f"""
import os, time, shutil, subprocess, sys

APP_EXE = r"{APP_EXE}"
NEW_EXE = r"{DOWNLOAD_TMP}"

# wait for old EXE to fully close
time.sleep(1)
while True:
    try:
        os.remove(APP_EXE)
        break
    except PermissionError:
        time.sleep(0.5)

# replace old EXE
os.rename(NEW_EXE, APP_EXE)

print("[UPDATE] Update applied successfully!")

# relaunch updated EXE
subprocess.Popen([APP_EXE])
sys.exit()
"""

    # write update launcher script
    with open(UPDATER_LAUNCHER, "w", encoding="utf-8") as f:
        f.write(launcher_code)

    # ---- FIX: Use bundled Python interpreter instead of EXE ----
    python_exec = sys._MEIPASS + "\\python.exe" if hasattr(sys, "_MEIPASS") else sys.executable

    subprocess.Popen([python_exec, UPDATER_LAUNCHER])

    print("[UPDATE] Applying update…")
    sys.exit()


if __name__ == "__main__":
    if check_for_update():
        launch_updater()
