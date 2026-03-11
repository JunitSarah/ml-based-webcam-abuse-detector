"""
popup_alert.py — Desktop popup alert system for webcam-abuse-detector.

Drop this file into your project root or mlmodel/ folder.
Call raise_popup_alert() from ml_detector.py or process_detector.py
whenever a suspicious event is detected.

Dependencies:
    pip install plyer tkinter  (tkinter is built-in with Python)

Cross-platform support:
    Windows  → tkinter MessageBox (always works, no extra install)
    macOS    → osascript notification + tkinter fallback
    Linux    → libnotify (notify-send) + tkinter fallback
"""

import threading
import platform
import subprocess
import os
import datetime
import logging
from pathlib import Path

# ── Log setup ────────────────────────────────────────────────────────────────
LOG_PATH = Path(__file__).parent / "alerts" / "alerts_log.txt"
LOG_PATH.parent.mkdir(exist_ok=True)

logging.basicConfig(
    filename=str(LOG_PATH),
    level=logging.WARNING,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

# ── Severity thresholds ───────────────────────────────────────────────────────
def get_severity(score: float) -> str:
    if score < -0.20:
        return "CRITICAL"
    elif score < -0.10:
        return "HIGH"
    elif score < 0.0:
        return "MEDIUM"
    return "LOW"


def get_severity_color(severity: str) -> str:
    return {
        "CRITICAL": "#c0392b",
        "HIGH":     "#e67e22",
        "MEDIUM":   "#f1c40f",
        "LOW":      "#27ae60",
    }.get(severity, "#2c3e50")


# ── Core popup function ───────────────────────────────────────────────────────
def raise_popup_alert(
    score: float,
    label: str = "Suspicious",
    reason: str = "",
    extra_info: dict = None,
    blocking: bool = False,
):
    """
    Main function to call from your detector scripts.

    Args:
        score      : Isolation Forest anomaly score (negative = suspicious)
        label      : 'Suspicious' or 'Normal'
        reason     : Short description e.g. 'Unknown process spike'
        extra_info : Dict of extra details e.g. {'process': 'xyz.exe', 'cpu': '98%'}
        blocking   : If True, waits for user to close popup before returning

    Example:
        from popup_alert import raise_popup_alert
        raise_popup_alert(score=-0.23, label='Suspicious',
                          reason='Unknown process spike',
                          extra_info={'process': 'unknown.exe', 'cpu': '98%'})
    """
    if label != "Suspicious":
        return  # Only alert on suspicious events

    severity  = get_severity(score)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    extra_str = ""
    if extra_info:
        extra_str = "\n".join(f"  {k}: {v}" for k, v in extra_info.items())

    # Log to file
    log_msg = (
        f"[{severity}] Score={score:.4f} | {reason} | {extra_str.replace(chr(10), ' | ')}"
    )
    logging.warning(log_msg)
    print(f"🚨 [{timestamp}] {severity} ALERT → {reason} | Score: {score:.4f}")

    # Launch popup in background thread (non-blocking by default)
    t = threading.Thread(
        target=_show_popup,
        args=(severity, score, reason, extra_str, timestamp),
        daemon=True,
    )
    t.start()
    if blocking:
        t.join()


# ── Platform dispatcher ───────────────────────────────────────────────────────
def _show_popup(severity, score, reason, extra_str, timestamp):
    system = platform.system()
    try:
        if system == "Windows":
            _popup_windows(severity, score, reason, extra_str, timestamp)
        elif system == "Darwin":
            _popup_macos(severity, score, reason, extra_str, timestamp)
        else:
            _popup_linux(severity, score, reason, extra_str, timestamp)
    except Exception as e:
        print(f"[PopupAlert] Primary popup failed ({e}), using tkinter fallback...")
        _popup_tkinter(severity, score, reason, extra_str, timestamp)


# ── Windows popup ─────────────────────────────────────────────────────────────
def _popup_windows(severity, score, reason, extra_str, timestamp):
    """
    Rich tkinter window — works on ALL Windows machines with no extra install.
    """
    _popup_tkinter(severity, score, reason, extra_str, timestamp)


# ── macOS popup ───────────────────────────────────────────────────────────────
def _popup_macos(severity, score, reason, extra_str, timestamp):
    msg = f"{severity} | Score: {score:.4f} | {reason}"
    subprocess.run([
        "osascript", "-e",
        f'display notification "{msg}" with title "⚠️ Webcam Abuse Detector" '
        f'subtitle "{timestamp}" sound name "Basso"'
    ], timeout=5)
    # Also show tkinter window for details
    _popup_tkinter(severity, score, reason, extra_str, timestamp)


# ── Linux popup ───────────────────────────────────────────────────────────────
def _popup_linux(severity, score, reason, extra_str, timestamp):
    msg = f"{severity} | Score: {score:.4f}\n{reason}"
    try:
        subprocess.run(
            ["notify-send", "-u", "critical", "-t", "8000",
             "⚠️ Webcam Abuse Detector", msg],
            timeout=5
        )
    except FileNotFoundError:
        pass  # notify-send not installed, fall through to tkinter
    _popup_tkinter(severity, score, reason, extra_str, timestamp)


# ── Tkinter popup (universal fallback + Windows primary) ─────────────────────
def _popup_tkinter(severity, score, reason, extra_str, timestamp):
    """
    Fully styled tkinter popup window — works everywhere Python is installed.
    """
    try:
        import tkinter as tk
        from tkinter import font as tkfont

        root = tk.Tk()
        root.withdraw()  # hide root first

        win = tk.Toplevel(root)
        win.title("⚠️ Behavioral Anomaly Detected")
        win.resizable(False, False)
        win.attributes("-topmost", True)   # always on top
        win.attributes("-alpha", 0.97)

        BG       = "#1a1a2e"
        CARD_BG  = "#16213e"
        FG       = "#e0e0e0"
        ACCENT   = get_severity_color(severity)
        BTN_BG   = "#0f3460"
        BTN_FG   = "#e0e0e0"

        win.configure(bg=BG)
        win.geometry("420x320")

        # ── Top colour bar ────────────────────────────────────────────────────
        bar = tk.Frame(win, bg=ACCENT, height=6)
        bar.pack(fill="x")

        # ── Header ────────────────────────────────────────────────────────────
        header = tk.Frame(win, bg=CARD_BG, pady=12)
        header.pack(fill="x", padx=0)

        icon_label = tk.Label(
            header, text="🚨", font=("Segoe UI Emoji", 28),
            bg=CARD_BG, fg=ACCENT
        )
        icon_label.pack(side="left", padx=(18, 0))

        title_frame = tk.Frame(header, bg=CARD_BG)
        title_frame.pack(side="left", padx=12)

        tk.Label(
            title_frame, text=f"{severity} ANOMALY DETECTED",
            font=("Segoe UI", 13, "bold"), bg=CARD_BG, fg=ACCENT
        ).pack(anchor="w")

        tk.Label(
            title_frame, text=f"Webcam Abuse Detector  ·  {timestamp}",
            font=("Segoe UI", 8), bg=CARD_BG, fg="#888"
        ).pack(anchor="w")

        # ── Body ──────────────────────────────────────────────────────────────
        body = tk.Frame(win, bg=BG, padx=18, pady=10)
        body.pack(fill="both", expand=True)

        def row(label, value, value_color=FG):
            f = tk.Frame(body, bg=BG)
            f.pack(fill="x", pady=3)
            tk.Label(f, text=label, width=20, anchor="w",
                     font=("Segoe UI", 9), bg=BG, fg="#888").pack(side="left")
            tk.Label(f, text=value, anchor="w",
                     font=("Segoe UI", 9, "bold"), bg=BG, fg=value_color).pack(side="left")

        score_color = ACCENT if score < 0 else "#27ae60"
        row("Severity:",     severity,           ACCENT)
        row("Anomaly Score:", f"{score:.4f}",    score_color)
        row("Reason:",        reason or "—")

        if extra_info_lines := extra_str.strip().split("\n") if extra_str.strip() else []:
            tk.Frame(body, bg="#333", height=1).pack(fill="x", pady=6)
            for line in extra_info_lines[:5]:
                if ":" in line:
                    k, _, v = line.partition(":")
                    row(k.strip() + ":", v.strip())

        # ── Buttons ───────────────────────────────────────────────────────────
        btn_frame = tk.Frame(win, bg=BG, pady=10)
        btn_frame.pack(fill="x", padx=18)

        def dismiss():
            win.destroy()
            root.destroy()

        def view_log():
            import subprocess, sys
            log = str(LOG_PATH)
            if platform.system() == "Windows":
                os.startfile(log)
            elif platform.system() == "Darwin":
                subprocess.run(["open", log])
            else:
                subprocess.run(["xdg-open", log])

        tk.Button(
            btn_frame, text="Dismiss", command=dismiss,
            bg=BTN_BG, fg=BTN_FG, relief="flat",
            font=("Segoe UI", 9, "bold"),
            padx=18, pady=6, cursor="hand2"
        ).pack(side="right", padx=(6, 0))

        tk.Button(
            btn_frame, text="View Log", command=view_log,
            bg="#1e3a5f", fg=BTN_FG, relief="flat",
            font=("Segoe UI", 9),
            padx=18, pady=6, cursor="hand2"
        ).pack(side="right")

        # Auto-close after 15 seconds if not dismissed
        win.after(15000, lambda: (win.destroy(), root.destroy()) if win.winfo_exists() else None)

        # Center on screen
        win.update_idletasks()
        w, h = win.winfo_width(), win.winfo_height()
        sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
        win.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

        win.deiconify()
        root.mainloop()

    except Exception as e:
        print(f"[PopupAlert] tkinter popup failed: {e}")


# ── Integration helpers ───────────────────────────────────────────────────────
def alert_if_suspicious(prediction: int, score: float, features: dict = None):
    """
    Convenience wrapper — pass Isolation Forest outputs directly.

    Args:
        prediction : model.predict() result — -1 = suspicious, 1 = normal
        score      : model.decision_function() result
        features   : dict of feature values to display in popup

    Example (in ml_detector.py):
        from popup_alert import alert_if_suspicious
        pred  = model.predict(X_scaled)[0]
        score = model.decision_function(X_scaled)[0]
        alert_if_suspicious(pred, score, features=live_features)
    """
    if prediction != -1:
        return

    severity = get_severity(score)
    reasons  = []
    extra    = {}

    if features:
        if features.get("suspicious_process_detected"):
            reasons.append("Suspicious process detected")
        if features.get("unknown_process_count", 0) > 20:
            reasons.append(f"High unknown process count ({features['unknown_process_count']})")
        if features.get("high_cpu_process_count", 0) > 3:
            reasons.append(f"High CPU usage ({features['high_cpu_process_count']} processes)")
        if features.get("is_night") and not features.get("user_active"):
            reasons.append("Night-time activity with inactive user")

        extra = {k: v for k, v in features.items()
                 if k not in ("process_names_sample",) and v is not None}

    reason = "; ".join(reasons) if reasons else "Anomalous behavioral pattern"
    raise_popup_alert(score=score, label="Suspicious",
                      reason=reason, extra_info=extra)


# ── Standalone test ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Testing CRITICAL alert popup...")
    raise_popup_alert(
        score=-0.25,
        label="Suspicious",
        reason="Unknown process spike detected",
        extra_info={
            "process":           "unknown_miner.exe",
            "cpu_usage":         "94%",
            "unknown_processes": 28,
            "session_duration":  "42 min",
            "network_conns":     7,
        },
        blocking=True,   # Wait for popup to close in test mode
    )
    print("✅ Popup test complete. Check alerts/alerts_log.txt for the log entry.")