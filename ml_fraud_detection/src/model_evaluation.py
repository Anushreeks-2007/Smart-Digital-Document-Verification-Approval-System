from sklearn.metrics import (
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report
)

# Example actual labels
# 1 = Suspicious, 0 = Normal
actual = [1, 1, 0, 0, 1, 0, 1, 0]

# Example model predictions
predicted = [1, 0, 0, 0, 1, 1, 1, 0]

# Confusion matrix
cm = confusion_matrix(actual, predicted)

print("CONFUSION MATRIX:")
print(cm)

# Evaluation metrics
print("\nACCURACY:", accuracy_score(actual, predicted))
print("PRECISION:", precision_score(actual, predicted))
print("RECALL:", recall_score(actual, predicted))
print("F1 SCORE:", f1_score(actual, predicted))

print("\nCLASSIFICATION REPORT:")
print(classification_report(actual, predicted))