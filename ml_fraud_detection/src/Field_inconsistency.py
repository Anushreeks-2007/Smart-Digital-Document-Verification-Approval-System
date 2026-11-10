def detect_inconsistencies(document_data):

    issues = []

    marks = document_data.get("marks")
    total_marks = document_data.get("total_marks")
    attendance = document_data.get("attendance")

    if marks is not None and total_marks is not None:
        if marks < 0 or marks > total_marks:
            issues.append("Marks exceed the valid range.")

    if attendance is not None:
        if attendance < 0 or attendance > 100:
            issues.append("Invalid attendance percentage.")

    if not document_data.get("student_name"):
        issues.append("Student name is missing.")

    if not document_data.get("document_id"):
        issues.append("Document ID is missing.")

    return {
        "has_inconsistencies": len(issues) > 0,
        "issues": issues,
        "risk": "REVIEW" if issues else "LOW"
    }


if __name__ == "__main__":

    valid_document = {
        "student_name": "Rahul",
        "document_id": "DOC001",
        "marks": 85,
        "total_marks": 100,
        "attendance": 92
    }

    suspicious_document = {
        "student_name": "Rahul",
        "document_id": "DOC002",
        "marks": 150,
        "total_marks": 100,
        "attendance": 120
    }

    print("TEST 1: Valid document")
    print(detect_inconsistencies(valid_document))

    print("\nTEST 2: Suspicious document")
    print(detect_inconsistencies(suspicious_document))
    