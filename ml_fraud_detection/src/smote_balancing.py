import pandas as pd
from pathlib import Path

from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE

# Load dataset
project_path = Path(__file__).resolve().parents[2]

dataset_path = (
    project_path / "ml_fraud_detection" /
    "dataset" / "documents.csv"
)

data = pd.read_csv(dataset_path)

# Select features and target
X = data[["marks", "attendance", "duplicate"]]
y = data["altered"]

# Split before applying SMOTE
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

print("Before SMOTE:")
print(y_train.value_counts())

# Apply SMOTE only to training data
smote = SMOTE(random_state=42, k_neighbors=1)

X_train_balanced, y_train_balanced = smote.fit_resample(
    X_train, y_train
)

print("\nAfter SMOTE:")
print(y_train_balanced.value_counts())

print("\nOriginal training shape:", X_train.shape)
print("Balanced training shape:", X_train_balanced.shape)