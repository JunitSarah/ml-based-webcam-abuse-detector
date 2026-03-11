"""
train.py — Train Isolation Forest on behavioral dataset
"""

import pandas as pd
import numpy as np
import joblib
import os

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

FEATURES = [
    'is_known_app',
    'is_foreground',
    'user_active',
    'is_night',
    'has_network_connection',
    'network_connection_count',
    'duration_minutes'
]

CONTAMINATION = 0.05


def train():

    print("\n📂 Loading dataset...")

    data_path = os.path.join(os.path.dirname(__file__), "training_data.xlsx")

    df = pd.read_excel(data_path)

    print(f"Dataset size: {len(df)} rows")

    X = df[FEATURES].values

    print("\n⚙ Scaling features...")

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    print("\n🌲 Training Isolation Forest...")

    model = IsolationForest(
        n_estimators=200,
        contamination=CONTAMINATION,
        random_state=42
    )

    model.fit(X_scaled)

    print("✓ Model training complete")

    # Compute anomaly scores
    scores = model.decision_function(X_scaled)

    threshold = np.percentile(scores, CONTAMINATION * 100)

    print("\n📉 Score statistics")
    print("----------------------")
    print(f"Score range : [{scores.min():.4f}, {scores.max():.4f}]")
    print(f"Threshold   : {threshold:.4f}")

    model_dir = os.path.join(os.path.dirname(__file__), "model")
    os.makedirs(model_dir, exist_ok=True)

    joblib.dump(model, os.path.join(model_dir, "isolation_forest.pkl"))
    joblib.dump(scaler, os.path.join(model_dir, "scaler.pkl"))
    joblib.dump(FEATURES, os.path.join(model_dir, "features.pkl"))
    joblib.dump(threshold, os.path.join(model_dir, "threshold.pkl"))

    print("\n✅ Training complete")


if __name__ == "__main__":

    print("\n🚀 Starting ML training pipeline\n")

    train()