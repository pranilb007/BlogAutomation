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
LOCAL_VERSION = "1.0.6"
APP_EXE = "BlogAutomation.exe"
DOWNLOAD_TMP = "BlogAutomation_new.exe"
UPDATER_LAUNCHER = "update_launcher.py"
# -----------------------------

def check_for_update():
    try:
        r = requests.get(VERSION_FILE_URL, timeout=10)
        r.raise_for_status()

        # Strip BOM/whitespace and parse JSON
        text = r.content.decode('utf-8-sig').strip()
        data = json.loads(text)

        latest_version = data.get("version")
        download_url = data.get("download_url")

        if latest_version != LOCAL_VERSION:
            print(f"[UPDATE] New version available: {latest_version}")
            download_update(download_url)
            return True
        print("[UPDATE] You are using the latest version.")
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
        print(f"[UPDATE] Downloaded new EXE as {DOWNLOAD_TMP}")
    except Exception as e:
        print("Download failed:", e)
        sys.exit(1)

def launch_updater():
    """Launch temporary Python updater to safely replace EXE"""
    try:
        # Write temporary updater script
        launcher_code = f"""
import os, sys, time, shutil, subprocess

APP_EXE = r"{APP_EXE}"
NEW_EXE = r"{DOWNLOAD_TMP}"

# Wait until old EXE is closed
time.sleep(1)
while True:
    try:
        if os.path.exists(APP_EXE):
            os.remove(APP_EXE)
        break
    except PermissionError:
        time.sleep(0.5)

# Replace old EXE with new EXE
os.rename(NEW_EXE, APP_EXE)
print("[UPDATE] Update applied successfully!")

# Launch new EXE
subprocess.Popen([APP_EXE], cwd=os.getcwd())
sys.exit()
"""
        with open(UPDATER_LAUNCHER, "w", encoding="utf-8") as f:
            f.write(launcher_code)

        # Launch updater script
        subprocess.Popen([sys.executable, UPDATER_LAUNCHER], cwd=os.getcwd())
        print("[UPDATE] Launching updater and exiting old EXE...")
        sys.exit()
    except Exception as e:
        print("Failed to launch updater:", e)
        sys.exit(1)

if __name__ == "__main__":
    if check_for_update():
        launch_updater()
