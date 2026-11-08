import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Locate dataset
project_path = Path(__file__).resolve().parents[2]
dataset_path = project_path / "ml_fraud_detection" / "dataset" / "documents.csv"

data = pd.read_csv(dataset_path)

# 1. Marks distribution
plt.figure()
plt.hist(data["marks"], bins=6)
plt.title("Distribution of Marks")
plt.xlabel("Marks")
plt.ylabel("Number of Documents")
plt.show()

# 2. Attendance distribution
plt.figure()
plt.hist(data["attendance"], bins=6)
plt.title("Distribution of Attendance")
plt.xlabel("Attendance")
plt.ylabel("Number of Documents")
plt.show()

# 3. Duplicate document count
print("Duplicate Documents:")
print(data["duplicate"].value_counts())

# 4. Altered document count
print("\nAltered Documents:")
print(data["altered"].value_counts())

# 5. Relationship between marks and attendance
plt.figure()
plt.scatter(data["marks"], data["attendance"])
plt.title("Marks vs Attendance")
plt.xlabel("Marks")
plt.ylabel("Attendance")
plt.show()

print("\nEDA COMPLETED!")