<div align="center">
<img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/Scikit--Learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white" />
<img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white" />
<br/><br/>
  
# *ML-Based Webcam Access Abuse Detection System*
</div>
### *Behavioral anomaly detection that protects your privacy — locally, in real time.*

<br/>

> Detects unauthorized or suspicious webcam access using machine learning, without ever sending your data to an external server.



---

## 📌 Overview

The **ML-Based Webcam Access Abuse Detection System** is a privacy-first, locally-running security tool that continuously monitors webcam usage on a user's machine. It uses **unsupervised machine learning** (Isolation Forest) to model normal webcam access behavior and raise real-time alerts when anomalies are detected — including stealthy, previously unknown threats that signature-based tools would miss.

Unlike conventional antivirus or permission-based access controls, this system is **behavior-aware**: it doesn't just ask *who* accessed the webcam, but *how*, *when*, and *why* — and flags anything that doesn't fit the learned pattern.

---

## 🚨 The Problem

Modern spyware, RATs (Remote Access Trojans), and rogue applications frequently exploit webcam access silently in the background. Traditional defenses:

-  Rely on known threat signatures
-  Only show a hardware indicator light (easily bypassed in software)
-  Require cloud connectivity, raising additional privacy concerns
-  Cannot detect **behavioral anomalies** from legitimate-looking processes

This system addresses all of the above.

---

## ✅ Key Features

| Feature | Description |
|---|---|
|  **Real-Time Monitoring** | Continuously tracks all processes accessing the webcam |
|  **ML Anomaly Detection** | Isolation Forest model identifies unusual access patterns |
|  **Fully Local** | No data ever leaves the user's machine |
|  **Monitoring Dashboard** | Visual overview of webcam activity and anomaly scores |
|  **Instant Alerts** | Immediate notifications when suspicious behavior is detected |
|  **Event Logging** | Structured logs of all flagged events for forensic review |
|  **Low Overhead** | Lightweight background process with minimal system impact |

---

##  How It Works

The system extracts **behavioral features** from any application accessing the webcam and scores them against a trained anomaly model.

### System Workflow
## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  1. 📡 Monitor system processes → detect webcam access      │
│                        │                                    │
│                        ▼                                    │
│  2. 🧩 Extract behavioral features                          │
│        (app identity, user interaction, network, duration)  │
│                        │                                    │
│                        ▼                                    │
│  3. ⚙️  Pre-process via Feature Scaler                       │
│                        │                                    │
│                        ▼                                    │
│  4. 🤖 Pass to trained Isolation Forest model               │
│                        │                                    │
│                        ▼                                    │
│  5. 📈 Calculate anomaly score → classify behavior          │
│                        │                                    │
│                        ▼                                    │
│  6. 🔔 Alert user if suspicious behavior detected           │
│                        │                                    │
│                        ▼                                    │
│  7. 📝 Log suspicious event for further analysis            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Behavioral Features Extracted

- **Application Identity** — which process is accessing the camera and its metadata
- **User Interaction State** — is the user actively using the machine or is it idle?
- **Network Connectivity** — is the accessing process communicating externally?
- **Webcam Usage Duration** — how long has the camera been in use?
- **Process Context** — parent process, execution path, and behavioral history

### Anomaly Detection: Isolation Forest

The **Isolation Forest** algorithm works by randomly partitioning feature space. Anomalous data points are isolated faster (shorter path length in the tree) than normal ones, making it highly effective for:

- Detecting **novel, unknown threats** without labeled training data
- Operating in **unsupervised mode** (no manual labeling required)
- Running efficiently with **low memory and CPU overhead**

---

## 🛠️ Tech Stack

```
Language     →  Python 3.8+
ML Engine    →  Scikit-learn  (Isolation Forest, Feature Scaling)
Monitoring   →  psutil        (Process & system-level webcam tracking)
Data Layer   →  Pandas        (Feature engineering & log management)
```

---

## 📂 Project Structure

```
ml-based-webcam-abuse-detector/
│
├── src/                              # Core source files
│
├── mlmodel/                          # Isolation Forest model & training logic
│
├── dashboard/                        # Real-time monitoring dashboard
│
├── frontend/                         # UI layer (HTML/CSS/JS)
│
├── alerts/                           # Alert generation & notification handling
│
├── logs/                             # Suspicious event logs
│
├── process_identifier.py             # Main webcam process identification engine
├── test_process_identifier.py        # Unit tests for process identifier
├── process_features.json             # Extracted behavioral feature definitions
├── generated_suspicious_samples.xlsx # Sample suspicious activity dataset
├── handle64.exe                      # Windows handle utility for device tracking
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

```bash
Python 3.8+
pip
```

### Installation

```bash
# Clone the repository
git clone https://github.com/JunitSarah/ml-based-webcam-abuse-detector.git
cd ml-based-webcam-abuse-detector

# Install dependencies
pip install -r requirements.txt
```

### Running the System

```bash
# Start the webcam process detection engine
python process_identifier.py

# Launch the monitoring dashboard
python dashboard/
```

### Running Tests

```bash
python test_process_identifier.py
```

---

## 📊 Sample Output

```
[2024-01-15 14:32:01] ✅ NORMAL   — Process: chrome.exe       | Score: -0.12 | Duration: 00:03:21
[2024-01-15 14:35:44] ✅ NORMAL   — Process: zoom.exe         | Score: -0.08 | Duration: 00:45:10
[2024-01-15 14:41:09] 🚨 ALERT    — Process: svchost.exe      | Score:  0.61 | Duration: 00:00:04
                       → No active user session detected
                       → External network connection active
                       → Event logged: logs/suspicious_events.csv
```

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---
## 🙏 Acknowledgments

A huge thank you to the amazing people who contributed to this project:

| Contributor | GitHub |
|-------------|--------|
| Eva Elizabeth | [@evaelizabeth1123](https://github.com/evaelizabeth1123) |
| Jovina Roy | [@Jovina123](https://github.com/Jovina123) |
| Malavika Vijay | [@MalavikaVijay-00](https://github.com/MalavikaVijay-00) |

This project wouldn't have been possible without your hard work, creativity, and collaboration. 💙

<div align="center">

⭐ If this project helped you, consider giving it a star!

</div>
