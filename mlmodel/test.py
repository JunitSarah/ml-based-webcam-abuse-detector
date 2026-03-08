"""
test.py — Evaluate the trained Isolation Forest model
Run using:

python mlmodel/test.py
"""

import pandas as pd
import numpy as np
import joblib
import os

from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


FEATURES = [
    'is_known_app',
    'is_foreground',
    'user_active',
    'is_night',
    'has_network_connection',
    'network_connection_count',
    'duration_minutes'
]


def test_model():

    print("\n📂 Loading model...")

    base_dir = os.path.dirname(__file__)

    model = joblib.load(os.path.join(base_dir, "model", "isolation_forest.pkl"))
    scaler = joblib.load(os.path.join(base_dir, "model", "scaler.pkl"))

    print("✓ Model loaded")

    print("\n📂 Loading dataset...")

    df = pd.read_excel(os.path.join(base_dir, "labeled_output.xlsx"))

    if 'label' not in df.columns:
        print("⚠ No ground truth labels found.")
        print("Accuracy cannot be computed.")
        return

    # Prepare features
    X = df[FEATURES].values

    # Convert labels to numeric
    y_true = df['label'].map({'Normal': 1, 'Suspicious': -1}).values

    # Scale features
    X_scaled = scaler.transform(X)

    # Predict
    preds = model.predict(X_scaled)

    print("\n📊 Model Evaluation")
    print("--------------------------------")

    acc = accuracy_score(y_true, preds)

    print(f"Accuracy: {acc*100:.2f}%")

    print("\nClassification Report:\n")
    print(classification_report(y_true, preds, target_names=["Suspicious","Normal"]))

    print("\nConfusion Matrix:\n")
    print(confusion_matrix(y_true, preds))


if __name__ == "__main__":

    print("\n🚀 Testing Isolation Forest Model\n")

    test_model()