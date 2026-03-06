"""
process_identification.py
Identifies processes currently accessing the webcam on Windows
and extracts ML features.
"""

import csv
import json
import time
import ctypes
import ctypes.wintypes
import datetime

import psutil
import winreg

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────

OUTPUT_JSON = "process_features.json"
OUTPUT_CSV = "process_features.csv"

KNOWN_APPS = {
    "zoom", "ms-teams", "teams", "skype", "webex", "discord", "slack",
    "chrome", "firefox", "msedge", "opera", "brave",
    "obs64", "obs32", "vlc", "camera", "windowscamera",
    "facetime", "meet", "gotomeeting", "ringcentral",
}

FEATURE_KEYS = [
    "is_known_app",
    "is_foreground",
    "user_active",
    "is_night",
    "has_network_connection",
    "network_connection_count",
    "duration_minutes",
]

# Track session start time
_session_start = {}

# Windows APIs
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]


# ─────────────────────────────────────────────
# STEP 1 — REGISTRY DETECTION
# ─────────────────────────────────────────────

def _get_pids_via_registry():

    pids = {}

    registry_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\webcam",
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\webcam\NonPackaged",
    ]

    for reg_path in registry_paths:

        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path)
            i = 0

            while True:

                try:
                    subkey_name = winreg.EnumKey(key, i)
                    i += 1

                    subkey = winreg.OpenKey(key, subkey_name)

                    try:
                        start_time, _ = winreg.QueryValueEx(subkey, "LastUsedTimeStart")
                        stop_time, _ = winreg.QueryValueEx(subkey, "LastUsedTimeStop")

                        # Active webcam usage
                        if start_time > stop_time:

                            exe_name = subkey_name.replace("#", "\\").split("\\")[-1].lower()

                            for proc in psutil.process_iter(['pid','name','create_time','ppid']):

                                try:
                                    if proc.info['name'].lower() == exe_name:

                                        proc_obj = psutil.Process(proc.info['pid'])

                                        # Remove browser child processes
                                        parent = proc_obj.parent()
                                        if parent and parent.name().lower() == exe_name:
                                            continue

                                        # Ensure network activity
                                        try:
                                            connections = proc_obj.net_connections()
                                        except AttributeError:
                                            connections = proc_obj.connections()

                                        if len(connections) == 0:
                                            continue

                                        pids[proc.info['pid']] = proc.info['create_time']

                                except (psutil.NoSuchProcess, psutil.AccessDenied):
                                    continue

                    except FileNotFoundError:
                        pass

                    winreg.CloseKey(subkey)

                except OSError:
                    break

            winreg.CloseKey(key)

        except OSError:
            continue

    return pids


# ─────────────────────────────────────────────
# STEP 2 — FALLBACK DETECTION
# ─────────────────────────────────────────────

def _get_pids_via_name_fallback():

    pids = {}

    for proc in psutil.process_iter(['pid','name','create_time','ppid']):

        try:
            name = proc.info['name'].lower().replace(".exe","")

            if not any(k in name for k in KNOWN_APPS):
                continue

            proc_obj = psutil.Process(proc.info['pid'])

            parent = proc_obj.parent()

            if parent and parent.name().lower().replace(".exe","") == name:
                continue

            try:
                connections = proc_obj.net_connections()
            except AttributeError:
                connections = proc_obj.connections()

            if len(connections) == 0:
                continue

            pids[proc.info['pid']] = proc.info['create_time']

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return pids


def identify_webcam_processes():

    pids = _get_pids_via_registry()

    if pids:
        print(f"[process_identification] Registry detected {len(pids)} webcam process(es).")

    else:
        print("[process_identification] Registry returned no active webcam processes.")
        print("[process_identification] Falling back to known-app name detection.")
        pids = _get_pids_via_name_fallback()

    return pids


# ─────────────────────────────────────────────
# FEATURE EXTRACTION
# ─────────────────────────────────────────────

def _get_foreground_pid():

    hwnd = user32.GetForegroundWindow()

    pid = ctypes.wintypes.DWORD()

    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

    return pid.value


def _seconds_since_last_input():

    lii = LASTINPUTINFO()

    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)

    user32.GetLastInputInfo(ctypes.byref(lii))

    return (kernel32.GetTickCount() - lii.dwTime) / 1000.0


def extract_features(pid, proc_start):

    now = time.time()
    dt = datetime.datetime.now()

    try:
        proc = psutil.Process(pid)
        proc_name = proc.name().lower().replace(".exe","")
    except:
        proc = None
        proc_name = "unknown"

    is_known_app = int(any(k in proc_name for k in KNOWN_APPS))

    try:
        is_foreground = int(_get_foreground_pid() == pid)
    except:
        is_foreground = 0

    user_active = int(_seconds_since_last_input() < 60)

    is_night = int(dt.hour < 6 or dt.hour >= 22)

    net_count = 0
    has_network = 0

    if proc:

        try:
            try:
                conns = proc.net_connections()
            except AttributeError:
                conns = proc.connections()

            net_count = len(conns)
            has_network = int(net_count > 0)

        except:
            pass

    # Session-based duration
    first_seen = _session_start.setdefault(pid, now)

    duration_minutes = round((now - first_seen)/60,3)

    return {
        "is_known_app": is_known_app,
        "is_foreground": is_foreground,
        "user_active": user_active,
        "is_night": is_night,
        "has_network_connection": has_network,
        "network_connection_count": net_count,
        "duration_minutes": duration_minutes
    }


# ─────────────────────────────────────────────
# OUTPUT WRITING
# ─────────────────────────────────────────────

def write_json(features_list):

    with open(OUTPUT_JSON,"w") as f:
        json.dump(features_list,f,indent=2)

    print(f"[process_identification] JSON written → {OUTPUT_JSON} ({len(features_list)} process(es))")


def write_csv(features_list):

    if not features_list:
        return

    with open(OUTPUT_CSV,"w",newline="") as f:

        writer = csv.DictWriter(f,fieldnames=FEATURE_KEYS)

        writer.writeheader()

        writer.writerows(features_list)

    print(f"[process_identification] CSV written → {OUTPUT_CSV} ({len(features_list)} process(es))")


# ─────────────────────────────────────────────
# MAIN PIPELINE
# ─────────────────────────────────────────────

def run(output_format="json"):

    print("[process_identification] Scanning for active webcam processes...")

    webcam_pids = identify_webcam_processes()

    features_list = []

    if not webcam_pids:
        print("[process_identification] No webcam processes found.")

    else:

        for pid,start_time in webcam_pids.items():

            features = extract_features(pid,start_time)

            features_list.append(features)

            print(f"PID {pid}: {features}")

    if output_format in ("json","both"):
        write_json(features_list)

    if output_format in ("csv","both"):
        write_csv(features_list)

    return features_list


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--format",
        choices=["json","csv","both"],
        default="json"
    )

    args = parser.parse_args()

    while True:
      run(args.format)
      time.sleep(10)