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
LOCAL_VERSION = "1.0.8"
APP_EXE = "BlogAutomation.exe"
DOWNLOAD_TMP = "BlogAutomation_new.exe"
UPDATER_LAUNCHER = "update_launcher.py"
# -----------------------------


# ---------------------------------------
# POPUP - informs user new version exists
# ---------------------------------------
def show_update_popup(latest_version):
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo(
            "Update Available",
            f"A new version ({latest_version}) of BlogAutomation is available.\n"
            "Updating now..."
        )
        root.destroy()
    except Exception:
        print(f"[UPDATE] New version available: {latest_version}")


# ---------------------------------------
# CHECK FOR UPDATE
# ---------------------------------------
def check_for_update():
    try:
        r = requests.get(VERSION_FILE_URL, timeout=10)
        r.raise_for_status()

        text = r.content.decode('utf-8-sig').strip()
        data = json.loads(text)

        latest_version = data.get("version")
        download_url = data.get("download_url")

        if latest_version != LOCAL_VERSION:
            show_update_popup(latest_version)
            download_update(download_url)
            return True

        print("[UPDATE] You are using the latest version.")
        return False

    except Exception as e:
        print("Update check failed:", e)
        return False


# ---------------------------------------
# DOWNLOAD NEW EXE
# ---------------------------------------
def download_update(url):
    try:
        r = requests.get(url, stream=True)
        r.raise_for_status()

        with open(DOWNLOAD_TMP, "wb") as f:
            shutil.copyfileobj(r.raw, f)

        print(f"[UPDATE] Downloaded new version as {DOWNLOAD_TMP}")

        # Hide temp EXE (Windows only)
        try:
            subprocess.call(["attrib", "+h", DOWNLOAD_TMP])
        except:
            pass

    except Exception as e:
        print("Download failed:", e)
        sys.exit(1)


# ---------------------------------------
# APPLY UPDATE (from separate launcher)
# ---------------------------------------
def launch_updater():
    try:

        # Updater script that runs after old EXE quits
        launcher_code = f"""
import os, sys, time, shutil, subprocess

APP_EXE = r"{APP_EXE}"
NEW_EXE = r"{DOWNLOAD_TMP}"

# small wait
time.sleep(1)

# wait until old EXE releases lock
while True:
    try:
        if os.path.exists(APP_EXE):
            os.remove(APP_EXE)
        break
    except PermissionError:
        time.sleep(0.5)

# replace old EXE
os.rename(NEW_EXE, APP_EXE)
print("[UPDATE] Update applied successfully!")

# launch new updated EXE
subprocess.Popen([APP_EXE], cwd=os.getcwd())
sys.exit()
"""

        # write the updater launcher
        with open(UPDATER_LAUNCHER, "w", encoding="utf-8") as f:
            f.write(launcher_code)

        # hide updater script
        try:
            subprocess.call(["attrib", "+h", UPDATER_LAUNCHER])
        except:
            pass

        # run updater
        subprocess.Popen([sys.executable, UPDATER_LAUNCHER], cwd=os.getcwd())
        print("[UPDATE] Launching updater… exiting old app.")
        sys.exit()

    except Exception as e:
        print("Failed to launch updater:", e)
        sys.exit(1)


# ---------------------------------------
# MAIN
# ---------------------------------------
if __name__ == "__main__":
    if check_for_update():
        launch_updater()
