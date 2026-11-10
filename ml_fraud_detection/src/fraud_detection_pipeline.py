import pandas as pd
from pathlib import Path
from sklearn.ensemble import IsolationForest

from duplicate_detection import (
    calculate_file_hash,
    detect_duplicate
)

from tampering_detection import (
    calculate_file_hash as calculate_trusted_hash,
    detect_tampering
)

from Field_inconsistency import detect_inconsistencies

from risk_scoring import calculate_risk


# =====================================
# 1. LOAD DATASET
# =====================================

PROJECT_PATH = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_PATH
    / "ml_fraud_detection"
    / "dataset"
    / "documents.csv"
)

data = pd.read_csv(DATASET_PATH)

features = data[["marks", "attendance"]]


# =====================================
# 2. TRAIN ANOMALY DETECTION MODEL
# =====================================

anomaly_model = IsolationForest(
    contamination=0.2,
    random_state=42
)

anomaly_model.fit(features)


# =====================================
# 3. MAIN FRAUD DETECTION FUNCTION
# =====================================

def analyze_document(
    file_bytes,
    existing_hashes,
    document_data,
    trusted_hash=None
):

    # Duplicate detection
    duplicate_result = detect_duplicate(
        file_bytes,
        existing_hashes
    )

    # Tampering detection
    if trusted_hash is not None:

        tampering_result = detect_tampering(
            file_bytes,
            trusted_hash
        )

        tampering = tampering_result["tampering_suspected"]

    else:

        tampering_result = {
            "tampering_suspected": None,
            "message": "Trusted original hash unavailable."
        }

        tampering = False

    # Field inconsistency detection
    inconsistency_result = detect_inconsistencies(
        document_data
    )

    # Anomaly detection
    anomaly_input = pd.DataFrame([{
        "marks": document_data["marks"],
        "attendance": document_data["attendance"]
    }])

    anomaly_prediction = anomaly_model.predict(
        anomaly_input
    )[0]

    is_anomaly = anomaly_prediction == -1

    # Risk scoring
    risk_result = calculate_risk(
        duplicate=duplicate_result["is_duplicate"],
        tampering=tampering,
        inconsistency=inconsistency_result["has_inconsistencies"],
        anomaly=is_anomaly
    )

    # Final report
    return {
        "duplicate_detection": duplicate_result,

        "tampering_detection": tampering_result,

        "inconsistency_detection": inconsistency_result,

        "anomaly_detection": {
            "is_anomaly": bool(is_anomaly),
            "status": (
                "Potential Anomaly"
                if is_anomaly
                else "Normal"
            )
        },

        "risk_assessment": risk_result
    }


# =====================================
# 4. TESTING
# =====================================

if __name__ == "__main__":

    original_document = b"Student marks card 2026"

    existing_hashes = {
        calculate_file_hash(original_document)
    }

    trusted_hash = calculate_trusted_hash(
        original_document
    )

    test_document = {
        "student_name": "Rahul",
        "document_id": "DOC100",
        "marks": 150,
        "total_marks": 100,
        "attendance": 120
    }

    result = analyze_document(
        file_bytes=original_document,
        existing_hashes=existing_hashes,
        document_data=test_document,
        trusted_hash=trusted_hash
    )

    print("\n========== FRAUD DETECTION REPORT ==========")

    for section, details in result.items():
        print(f"\n{section.upper()}")
        print(details)

    print("\n========== ANALYSIS COMPLETED ==========")