import pandas as pd
from pathlib import Path
from sklearn.ensemble import IsolationForest

# Locate dataset
project_path = Path(__file__).resolve().parents[2]
dataset_path = project_path / "ml_fraud_detection" / "dataset" / "documents.csv"

# Load data
data = pd.read_csv(dataset_path)

# Select numerical features
features = data[["marks", "attendance"]]

# Create ML model
model = IsolationForest(
    contamination=0.2,
    random_state=42
)

# Train model
model.fit(features)

# Predict anomalies
data["anomaly"] = model.predict(features)

# Convert predictions
data["anomaly_status"] = data["anomaly"].map({
    1: "Normal",
    -1: "Potential Anomaly"
})

print("\nANOMALY DETECTION RESULTS:")
print(data[["document_id", "marks", "attendance", "anomaly_status"]])

print("\nANOMALY DETECTION COMPLETED!")