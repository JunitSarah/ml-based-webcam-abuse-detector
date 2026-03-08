"""
train.py — Train Isolation Forest on behavioral dataset and save model + scaler.
Run once before starting the monitor:

python model/train.py
"""

import pandas as pd
import numpy as np
import joblib
import os

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# Features used by the ML model
FEATURES = [
    'is_known_app',
    'is_foreground',
    'user_active',
    'is_night',
    'has_network_connection',
    'network_connection_count',
    'duration_minutes'
]

# Expected anomaly percentage
CONTAMINATION = 0.05


def train():

    print("\n📂 Loading dataset...")

    data_path = os.path.join(os.path.dirname(__file__), "training_data.xlsx")

    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Dataset not found: {data_path}")

    df = pd.read_excel(data_path)

    print(f"Dataset size: {len(df)} rows")

    # Validate required features
    missing = [f for f in FEATURES if f not in df.columns]

    if missing:
        raise ValueError(f"Dataset missing required features: {missing}")

    # Extract features
    X = df[FEATURES].values

    print("\n⚙ Scaling features...")

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    print("\n🌲 Training Isolation Forest...")

    model = IsolationForest(
        n_estimators=200,
        contamination=CONTAMINATION,
        max_samples='auto',
        random_state=42
    )

    model.fit(X_scaled)

    print("✓ Model training complete")

    # Predict anomalies on training data
    preds = model.predict(X_scaled)

    scores = model.decision_function(X_scaled)

    df['anomaly_score'] = scores

    df['label'] = ['Suspicious' if p == -1 else 'Normal' for p in preds]

    # Compute anomaly threshold
    threshold = np.percentile(scores, CONTAMINATION * 100)

    normal_count = (preds == 1).sum()
    suspicious_count = (preds == -1).sum()

    print("\n📊 Training Results")

    print("--------------------------------")

    print(f"Total samples : {len(df)}")
    print(f"Normal        : {normal_count} ({normal_count/len(df)*100:.1f}%)")
    print(f"Suspicious    : {suspicious_count} ({suspicious_count/len(df)*100:.1f}%)")

    print(f"Score range   : [{scores.min():.4f}, {scores.max():.4f}]")
    print(f"Threshold     : {threshold:.4f}")

    # Create model directory
    model_dir = os.path.join(os.path.dirname(__file__), "model")
    os.makedirs(model_dir, exist_ok=True)

    print("\n💾 Saving model files...")

    joblib.dump(model, os.path.join(model_dir, "isolation_forest.pkl"))
    joblib.dump(scaler, os.path.join(model_dir, "scaler.pkl"))
    joblib.dump(FEATURES, os.path.join(model_dir, "features.pkl"))
    joblib.dump(threshold, os.path.join(model_dir, "threshold.pkl"))

    # Save labeled dataset
    labeled_path = os.path.join(os.path.dirname(__file__), "labeled_output.xlsx")

    df.to_excel(labeled_path, index=False)

    print("\n✅ Training complete")

    print("Saved files:")
    print("  model/isolation_forest.pkl")
    print("  model/scaler.pkl")
    print("  model/features.pkl")
    print("  model/threshold.pkl")
    print("  data/labeled_output.xlsx")

    return model, scaler


if __name__ == "__main__":

    print("\n🚀 Starting ML training pipeline\n")

    train()