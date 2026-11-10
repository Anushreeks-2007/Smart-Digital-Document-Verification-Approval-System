import hashlib


def calculate_file_hash(file_bytes):
    return hashlib.sha256(file_bytes).hexdigest()


def detect_duplicate(file_bytes, existing_hashes):
    document_hash = calculate_file_hash(file_bytes)

    if document_hash in existing_hashes:
        return {
            "is_duplicate": True,
            "document_hash": document_hash,
            "risk": "HIGH",
            "message": "Duplicate document detected."
        }

    return {
        "is_duplicate": False,
        "document_hash": document_hash,
        "risk": "LOW",
        "message": "No exact duplicate found."
    }


if __name__ == "__main__":

    existing_document = b"Student marks card 2026"
    uploaded_document = b"Student marks card 2026"
    different_document = b"Student marks card 2025"

    existing_hashes = {
        calculate_file_hash(existing_document)
    }

    print("TEST 1: Same document")
    print(detect_duplicate(uploaded_document, existing_hashes))

    print("\nTEST 2: Different document")
    print(detect_duplicate(different_document, existing_hashes))