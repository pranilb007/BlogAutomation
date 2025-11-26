import requests
import json
import os
import sys
import time
import shutil
import subprocess

VERSION_FILE_URL = "https://raw.githubusercontent.com/pranilb007/BlogAutomation/main/updater/version.json"
LOCAL_VERSION = "1.0.0"
APP_EXE = "BlogAutomation.exe"
DOWNLOAD_TMP = "update_tmp.exe"

def check_for_update():
    try:
        r = requests.get(VERSION_FILE_URL, timeout=5)
        r.raise_for_status()  # ensure HTTP 200

        # Decode safely and strip BOM / whitespace
        text = r.content.decode('utf-8-sig').strip()
        data = json.loads(text)

        latest_version = data.get("version")
        download_url = data.get("download_url")

        if latest_version != LOCAL_VERSION:
            print(f"New version available: {latest_version}")
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
        print("Download complete")
    except Exception as e:
        print("Download failed:", e)

def apply_update():
    try:
        if os.path.exists(APP_EXE):
            os.remove(APP_EXE)
        os.rename(DOWNLOAD_TMP, APP_EXE)
        print("Updated successfully!")
        return True
    except Exception as e:
        print("Update error:", e)
        return False

def restart_app():
    print("Restarting...")
    time.sleep(1)
    subprocess.Popen([APP_EXE])
    sys.exit()

if __name__ == "__main__":
    if check_for_update():
        if apply_update():
            restart_app()
