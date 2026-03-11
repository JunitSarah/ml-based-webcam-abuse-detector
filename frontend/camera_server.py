from flask import Flask, send_from_directory, jsonify
import csv
import os

app = Flask(__name__, static_folder=".")

# Path to CSV log file
LOG_FILE = os.path.join(os.getcwd(), "logs", "webcam_logs.csv")


@app.route("/")
def dashboard():
    return send_from_directory(".", "index.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(".", path)


@app.route("/alerts")
def get_alerts():

    alerts = []

    alert_file = os.path.join(os.path.dirname(os.getcwd()), "alerts", "alerts_log.txt")

    if os.path.exists(alert_file):

        with open(alert_file,"r") as f:
            lines = f.readlines()

        alerts = [line.strip() for line in lines if line.strip()]

    return jsonify(alerts)

@app.route("/logs")
def get_logs():

    logs = []

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, newline="") as f:
            reader = csv.DictReader(f)
            logs = list(reader)

    return jsonify(logs)


if __name__ == "__main__":
    print("Starting Dashboard Server...")
    app.run(debug=True)