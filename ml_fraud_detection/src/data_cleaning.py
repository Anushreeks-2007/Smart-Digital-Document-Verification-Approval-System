import pandas as pd
from pathlib import Path

# Locate the dataset
project_path = Path(__file__).resolve().parents[2]
dataset_path = project_path / "ml_fraud_detection" / "dataset" / "documents.csv"

# Load data
data = pd.read_csv(dataset_path)

print("ORIGINAL DATA:")
print(data)

# 1. Check missing values
print("\nMISSING VALUES:")
print(data.isnull().sum())

# 2. Check duplicate rows
print("\nDUPLICATE ROWS:")
print(data.duplicated().sum())

# 3. Check invalid marks
invalid_marks = data[(data["marks"] < 0) | (data["marks"] > 100)]
print("\nINVALID MARKS:")
print(invalid_marks)

# 4. Check invalid attendance
invalid_attendance = data[
    (data["attendance"] < 0) | (data["attendance"] > 100)
]
print("\nINVALID ATTENDANCE:")
print(invalid_attendance)

# 5. Remove exact duplicate rows
cleaned_data = data.drop_duplicates().copy()

print("\nCLEANED DATA:")
print(cleaned_data)

print("\nDATA CLEANING COMPLETED!")