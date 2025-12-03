import requests
import json
import os
import sys
import time
import shutil
import subprocess
import tkinter as tk
from tkinter import messagebox

# --------------------------------------
# CONFIG
# --------------------------------------
VERSION_FILE_URL = "https://raw.githubusercontent.com/pranilb007/BlogAutomation/main/updater/version.json"
APP_EXE = "BlogAutomation.exe"
DOWNLOAD_TMP = "BlogAutomation_new.exe"
UPDATER_LAUNCHER = "update_launcher.py"
VERSION_TXT = "version.txt"
# --------------------------------------


# --------------------------------------
# Read local version from version.txt
# --------------------------------------
def get_local_version():
    try:
        with open(VERSION_TXT, "r") as f:
            return f.read().strip()
    except:
        return "0.0.0"  # force update if missing


LOCAL_VERSION = get_local_version()


# --------------------------------------
# Popup helper (Tkinter)
# --------------------------------------
def ask_user_update(latest_version, release_notes):
    root = tk.Tk()
    root.withdraw()  # hide main window

    msg = (
        f"A new version ({latest_version}) is available.\n\n"
        f"Current version: {LOCAL_VERSION}\n"
        f"Changes:\n{release_notes}\n\n"
        "Do you want to update now?"
    )

    return messagebox.askyesno("Update Available", msg)


# --------------------------------------
# Update checker
# --------------------------------------
def check_for_update():
    try:
        r = requests.get(VERSION_FILE_URL, timeout=10)
        r.raise_for_status()

        text = r.content.decode("utf-8-sig").strip()
        data = json.loads(text)

        latest_version = data.get("version")
        download_url = data.get("download_url")
        release_notes = data.get("release_notes", "")

        if latest_version != LOCAL_VERSION:
            print(f"[UPDATE] New version available: {latest_version}")

            # Show popup
            if ask_user_update(latest_version, release_notes):
                download_update(download_url)
                return True
            else:
                print("[UPDATE] User skipped update.")
                return False

        print("[UPDATE] You are using the latest version.")
        return False

    except Exception as e:
        print("Update check failed:", e)
        return False


# --------------------------------------
# Download the new EXE
# --------------------------------------
def download_update(url):
    try:
        print("[UPDATE] Downloading latest version...")
        r = requests.get(url, stream=True)
        r.raise_for_status()

        with open(DOWNLOAD_TMP, "wb") as f:
            shutil.copyfileobj(r.raw, f)

        print(f"[UPDATE] Downloaded as {DOWNLOAD_TMP}")

    except Exception as e:
        print("Download failed:", e)
        sys.exit(1)


# --------------------------------------
# Temporary updater script generator
# --------------------------------------
def launch_updater():
    try:
        launcher_code = f"""
import os, sys, time, shutil, subprocess

APP_EXE = r"{APP_EXE}"
NEW_EXE = r"{DOWNLOAD_TMP}"
VERSION_TXT = r"{VERSION_TXT}"

# Wait for old EXE to close
time.sleep(1)
while True:
    try:
        if os.path.exists(APP_EXE):
            os.remove(APP_EXE)
        break
    except PermissionError:
        time.sleep(0.5)

# Replace EXE
os.rename(NEW_EXE, APP_EXE)

# Update version.txt from folder of new EXE
with open(VERSION_TXT, "w") as vf:
    vf.write("{LOCAL_VERSION}")

print("[UPDATE] Update applied successfully!")

# Launch new EXE
subprocess.Popen([APP_EXE], cwd=os.getcwd())
sys.exit()
"""

        # Create updater file
        with open(UPDATER_LAUNCHER, "w", encoding="utf-8") as f:
            f.write(launcher_code)

        # Hide updater files on Windows
        try:
            subprocess.call(["attrib", "+h", UPDATER_LAUNCHER])
            subprocess.call(["attrib", "+h", DOWNLOAD_TMP])
        except:
            pass

        # Launch updater
        subprocess.Popen([sys.executable, UPDATER_LAUNCHER], cwd=os.getcwd())
        print("[UPDATE] Installing update…")
        sys.exit()

    except Exception as e:
        print("Failed to launch updater:", e)
        sys.exit(1)


# --------------------------------------
# MAIN ENTRY
# --------------------------------------
if __name__ == "__main__":
    if check_for_update():
        launch_updater()
