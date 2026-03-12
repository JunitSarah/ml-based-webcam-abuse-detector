import pandas as pd
import numpy as np
import joblib
import os

from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.metrics import balanced_accuracy_score



from sklearn.metrics import roc_auc_score





FEATURES = [
    'is_known_app',
    'is_foreground',
    'user_active',
    'is_night',
    'has_network_connection',
    'network_connection_count',
    'duration_minutes'
]


def test():

    base_dir = os.path.dirname(__file__)

    print("\n📂 Loading model...")

    model = joblib.load(os.path.join(base_dir, "model/isolation_forest.pkl"))
    scaler = joblib.load(os.path.join(base_dir, "model/scaler.pkl"))

    print("✓ Model loaded")

    print("\n📂 Loading labeled dataset...")

    data = pd.read_excel(os.path.join(base_dir, "labeled_output.xlsx"))

    # convert labels to numeric
    data["label"] = data["label"].map({
        "Normal": 0,
        "Suspicious": 1
    })

    X = data[FEATURES].values
    y = data["label"].values

    X_scaled = scaler.transform(X)

    print("\n🔍 Predicting anomalies...")

    preds = model.predict(X_scaled)

    preds = np.where(preds == -1, 1, 0)

    print("\n📊 Evaluation Results")
    print("----------------------")


    print("\nConfusion Matrix")
    print(confusion_matrix(y, preds))

    print("\nClassification Report")
    print(classification_report(y, preds))
    print("Accuracy:", balanced_accuracy_score(y, preds))
    



if __name__ == "__main__":

    print("\n🚀 Running model evaluation\n")
    
    test()