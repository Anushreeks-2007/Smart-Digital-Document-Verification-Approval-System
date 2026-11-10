# Smart Digital Document Verification & Approval System
## ML Fraud Detection Module

### Overview
This module identifies suspicious digital documents using duplicate detection, tampering checks, field inconsistency detection, anomaly detection, and risk scoring.

### Features

1. Duplicate Detection
   - Uses SHA-256 hashing.
   - Identifies exact duplicate files.

2. Tampering Detection
   - Compares uploaded document hashes with trusted original hashes.
   - Flags content differences for review.

3. Field Inconsistency Detection
   - Checks marks against total marks.
   - Validates attendance percentages.
   - Checks missing student names and document IDs.

4. Anomaly Detection
   - Uses Isolation Forest.
   - Identifies unusual document patterns.

5. Risk Scoring
   - Combines detection results into a risk score.
   - Classifies risk as LOW, MEDIUM, or HIGH.
   - Recommends manual review when necessary.

### Technologies
- Python
- Pandas
- Scikit-learn
- NumPy
- Isolation Forest
- Random Forest
- SMOTE
- SHAP

### Project Structure

```text
ml_fraud_detection/
├── dataset/
│   └── documents.csv
├── models/
├── notebooks/
├── src/
│   ├── anomaly_detection.py
│   ├── duplicate_detection.py
│   ├── tampering_detection.py
│   ├── Field_inconsistency.py
│   ├── risk_scoring.py
│   ├── fraud_detection_pipeline.py
│   └── other ML modules
└── README.md
## Backend Integration Contract

### Python Import

```python
from src.fraud_detection_pipeline import analyze_document