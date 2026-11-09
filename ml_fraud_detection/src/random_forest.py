import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    cross_val_score,
    GridSearchCV
)

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)


# ==========================================
# 1. LOAD DATASET
# ==========================================

project_path = Path(__file__).resolve().parents[2]

dataset_path = (
    project_path
    / "ml_fraud_detection"
    / "dataset"
    / "documents.csv"
)

data = pd.read_csv(dataset_path)

print("\nDATASET:")
print(data.head())


# ==========================================
# 2. SELECT FEATURES AND TARGET
# ==========================================

X = data[["marks", "attendance", "duplicate"]]
y = data["altered"]


# ==========================================
# 3. SPLIT DATASET
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=42,
    stratify=y
)

print("\nTraining records:", len(X_train))
print("Testing records:", len(X_test))


# ==========================================
# 4. CREATE RANDOM FOREST MODEL
# ==========================================

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)


# ==========================================
# 5. MODEL PREDICTION
# ==========================================

predictions = model.predict(X_test)

print("\nACTUAL VALUES:")
print(list(y_test))

print("\nPREDICTED VALUES:")
print(list(predictions))


# ==========================================
# 6. MODEL EVALUATION
# ==========================================

print("\nINITIAL MODEL EVALUATION")

print("Accuracy:", accuracy_score(y_test, predictions))

print("\nClassification Report:")
print(classification_report(
    y_test,
    predictions,
    zero_division=0
))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, predictions))


# ==========================================
# 7. OVERFITTING CHECK
# ==========================================

train_predictions = model.predict(X_train)
test_predictions = model.predict(X_test)

print("\nOVERFITTING CHECK")

print(
    "Training Accuracy:",
    accuracy_score(y_train, train_predictions)
)

print(
    "Testing Accuracy:",
    accuracy_score(y_test, test_predictions)
)


# ==========================================
# 8. CROSS VALIDATION
# ==========================================

print("\nCROSS VALIDATION")

cv = StratifiedKFold(
    n_splits=3,
    shuffle=True,
    random_state=42
)

cv_scores = cross_val_score(
    model,
    X,
    y,
    cv=cv,
    scoring="accuracy"
)

print("Cross-validation scores:", cv_scores)
print("Average CV accuracy:", cv_scores.mean())


# ==========================================
# 9. HYPERPARAMETER TUNING
# ==========================================

print("\nHYPERPARAMETER TUNING")

param_grid = {
    "n_estimators": [50, 100, 150],
    "max_depth": [3, 5, 10],
    "min_samples_split": [2, 4]
}

grid_search = GridSearchCV(
    estimator=RandomForestClassifier(random_state=42),
    param_grid=param_grid,
    cv=2,
    scoring="f1",
    error_score="raise"
)

# IMPORTANT: Fit before accessing best_estimator_
grid_search.fit(X_train, y_train)

print("Best Parameters:", grid_search.best_params_)
print("Best CV F1 Score:", grid_search.best_score_)

best_model = grid_search.best_estimator_


# ==========================================
# 10. FEATURE IMPORTANCE
# ==========================================

print("\nFEATURE IMPORTANCE")

importance = best_model.feature_importances_

feature_importance = pd.DataFrame({
    "Feature": X.columns,
    "Importance": importance
})

feature_importance = feature_importance.sort_values(
    by="Importance",
    ascending=False
)

print(feature_importance)

plt.figure(figsize=(7, 4))

plt.bar(
    feature_importance["Feature"],
    feature_importance["Importance"]
)

plt.title("Random Forest Feature Importance")
plt.xlabel("Features")
plt.ylabel("Importance Score")

plt.tight_layout()
plt.show()


# ==========================================
# 11. THRESHOLD TUNING
# ==========================================

print("\nTHRESHOLD TUNING")

probabilities = best_model.predict_proba(X_test)[:, 1]

thresholds = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]

for threshold in thresholds:

    custom_predictions = (
        probabilities >= threshold
    ).astype(int)

    precision = precision_score(
        y_test,
        custom_predictions,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        custom_predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        custom_predictions,
        zero_division=0
    )

    print("\nThreshold:", threshold)
    print("Precision:", precision)
    print("Recall:", recall)
    print("F1 Score:", f1)

print("\nALL TASKS COMPLETED!")