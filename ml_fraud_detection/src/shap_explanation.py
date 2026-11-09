import pandas as pd
import shap

from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Locate dataset
project_path = Path(__file__).resolve().parents[2]
dataset_path = project_path / "ml_fraud_detection" / "dataset" / "documents.csv"

data = pd.read_csv(dataset_path)

# Select features and target
X = data[["marks", "attendance", "duplicate"]]
y = data["altered"]

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

# Train Random Forest
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Create SHAP explainer
explainer = shap.TreeExplainer(model)

# Explain test data
shap_values = explainer(X_test)

# Display SHAP summary plot
shap.plots.beeswarm(shap_values[:, :, 1])