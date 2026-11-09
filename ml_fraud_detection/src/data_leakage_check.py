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

# Keep track of original document IDs
X = data[["marks", "attendance", "duplicate"]]
y = data["altered"]
document_ids = data["document_id"]

# Split data BEFORE applying SMOTE
X_train, X_test, y_train, y_test, id_train, id_test = (
    train_test_split(
        X, y, document_ids,
        test_size=0.25,
        random_state=42,
        stratify=y
    )
)

# Check for overlap
print("TRAINING DOCUMENTS:")
print(list(id_train))

print("\nTESTING DOCUMENTS:")
print(list(id_test))

overlap = set(id_train).intersection(set(id_test))

print("\nOVERLAPPING DOCUMENTS:", overlap)

if len(overlap) == 0:
    print("SUCCESS: No document overlap!")

# Apply SMOTE only to training data
smote = SMOTE(random_state=42, k_neighbors=1)

X_train_balanced, y_train_balanced = (
    smote.fit_resample(X_train, y_train)
)

print("\nTraining data before SMOTE:", X_train.shape)
print("Training data after SMOTE:", X_train_balanced.shape)

print("\nTesting data remains unchanged:", X_test.shape)