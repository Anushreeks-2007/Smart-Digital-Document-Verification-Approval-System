import hashlib


def calculate_file_hash(file_bytes):
    return hashlib.sha256(file_bytes).hexdigest()


def detect_tampering(uploaded_file, trusted_hash):

    uploaded_hash = calculate_file_hash(uploaded_file)

    tampering_detected = uploaded_hash != trusted_hash

    return {
        "tampering_suspected": tampering_detected,
        "risk": "REVIEW" if tampering_detected else "LOW",
        "message": (
            "Document content differs from trusted original."
            if tampering_detected
            else "Document matches trusted original."
        ),
        "uploaded_hash": uploaded_hash
    }


if __name__ == "__main__":

    original = b"Student marks: 85"
    modified = b"Student marks: 100"

    trusted_hash = calculate_file_hash(original)

    print("TEST 1")
    print(detect_tampering(original, trusted_hash))

    print("TEST 2")
    print(detect_tampering(modified, trusted_hash))