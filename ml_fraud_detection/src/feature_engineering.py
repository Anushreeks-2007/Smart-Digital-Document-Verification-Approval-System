import pandas as pd
from pathlib import Path

# Locate dataset
project_path = Path(__file__).resolve().parents[2]
dataset_path = project_path / "ml_fraud_detection" / "dataset" / "documents.csv"

data = pd.read_csv(dataset_path)

# Create new features
data["invalid_marks"] = (
    (data["marks"] < 0) | (data["marks"] > 100)
).astype(int)

data["invalid_attendance"] = (
    (data["attendance"] < 0) | (data["attendance"] > 100)
).astype(int)

data["suspicious_document"] = (
    (data["duplicate"] == 1) |
    (data["altered"] == 1) |
    (data["invalid_marks"] == 1) |
    (data["invalid_attendance"] == 1)
).astype(int)

print("FEATURE ENGINEERING RESULTS:")
print(data)

print("\nSUSPICIOUS DOCUMENT COUNT:")
print(data["suspicious_document"].sum())

print("\nFEATURE ENGINEERING COMPLETED!")