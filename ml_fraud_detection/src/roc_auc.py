import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    roc_curve,
    roc_auc_score,
    auc
)

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

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=42,
    stratify=y
)

# Train model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

# Get prediction probabilities
probabilities = model.predict_proba(X_test)[:, 1]

# Calculate ROC values
fpr, tpr, thresholds = roc_curve(
    y_test,
    probabilities
)

# Calculate AUC
roc_auc = auc(fpr, tpr)

print("ROC AUC Score:", roc_auc)

# Plot ROC curve
plt.figure(figsize=(7, 5))

plt.plot(
    fpr,
    tpr,
    label=f"Random Forest (AUC = {roc_auc:.2f})"
)

plt.plot(
    [0, 1],
    [0, 1],
    linestyle="--",
    label="Random Guessing"
)

plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")

plt.title("ROC Curve - Fraud Detection")

plt.legend()
plt.grid()

plt.tight_layout()
plt.show()