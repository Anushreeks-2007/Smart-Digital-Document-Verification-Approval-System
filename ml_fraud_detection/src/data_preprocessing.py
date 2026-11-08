import pandas as pd
from pathlib import Path

# Find the project folder automatically
project_path = Path(__file__).resolve().parents[2]

# Locate the dataset
dataset_path = project_path / "ml_fraud_detection" / "dataset" / "documents.csv"

# Load the dataset
data = pd.read_csv(dataset_path)

print("\nDOCUMENT DATA:")
print(data)

print("\nDATASET INFORMATION:")
data.info()

print("\nMISSING VALUES:")
print(data.isnull().sum())

print("\nSTATISTICAL SUMMARY:")
print(data.describe())