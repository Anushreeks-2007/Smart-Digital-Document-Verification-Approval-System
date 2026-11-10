def calculate_risk(duplicate, tampering, inconsistency, anomaly):

    score = 0
    reasons = []

    if duplicate:
        score += 40
        reasons.append("Duplicate document detected")

    if tampering:
        score += 30
        reasons.append("Possible document tampering")

    if inconsistency:
        score += 20
        reasons.append("Document field inconsistencies")

    if anomaly:
        score += 10
        reasons.append("Unusual document pattern")

    score = min(score, 100)

    if score >= 60:
        risk_level = "HIGH"
    elif score >= 30:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "risk_score": score,
        "risk_level": risk_level,
        "reasons": reasons,
        "recommendation": (
            "Manual review required"
            if score >= 30
            else "No immediate risk flags"
        )
    }


if __name__ == "__main__":

    print("TEST 1: Normal document")
    print(calculate_risk(False, False, False, False))

    print("\nTEST 2: Suspicious document")
    print(calculate_risk(True, True, True, False))

    print("\nTEST 3: Highly suspicious document")
    print(calculate_risk(True, True, True, True))