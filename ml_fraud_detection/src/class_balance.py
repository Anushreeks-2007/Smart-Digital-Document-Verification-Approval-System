import pandas as pd
from pathlib import Path

project_path = Path(__file__).resolve().parents[2]

dataset_path = (
    project_path / "ml_fraud_detection" /
    "dataset" / "documents.csv"
)

data = pd.read_csv(dataset_path)

print("Class Distribution:")
print(data["altered"].value_counts())

print("\nClass Percentages:")
print(data["altered"].value_counts(normalize=True) * 100)

data["altered"].value_counts().plot(
    kind="bar",
    title="Genuine vs Altered Documents"
)

import matplotlib.pyplot as plt

plt.xlabel("Document Class")
plt.ylabel("Number of Documents")
plt.show()