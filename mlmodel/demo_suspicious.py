from ml_detector import predict

# Simulated suspicious behaviour
fake_features = {
    "is_known_app": 0,
    "is_foreground": 0,
    "user_active": 0,
    "is_night": 1,
    "has_network_connection": 1,
    "network_connection_count": 15,
    "duration_minutes": 20
}

result, score = predict(fake_features)

print("\nSimulated Webcam Access")
print("-----------------------")
print("Features:", fake_features)
print("Prediction:", result)
print("Anomaly Score:", score)