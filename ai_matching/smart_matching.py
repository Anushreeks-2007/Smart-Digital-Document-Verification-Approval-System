import os

try:
    from .text_matching import compare_items
    from .image_matching import compare_images
    from .metadata_matching import calculate_metadata_score
    from .category_prediction import predict_category
except ImportError:
    from text_matching import compare_items
    from image_matching import compare_images
    from metadata_matching import calculate_metadata_score
    from category_prediction import predict_category


def calculate_combined_score(text_score, image_score, metadata_score):
    if image_score is None:
        final_score = (
            text_score * (0.40 / 0.70) +
            metadata_score * (0.30 / 0.70)
        )
    else:
        final_score = (
            text_score * 0.40 +
            image_score * 0.30 +
            metadata_score * 0.30
        )

    return round(final_score, 2)


def find_best_matches(lost_item, found_items):
    lost_item = lost_item.copy()

    if not lost_item.get("category"):
        lost_item["category"] = predict_category(
            lost_item.get("description", "")
        )

    results = []

    for found_item in found_items:
        found_item = found_item.copy()

        if not found_item.get("category"):
            found_item["category"] = predict_category(
                found_item.get("description", "")
            )

        text_score, text_result = compare_items(
            lost_item.get("description", ""),
            found_item.get("description", "")
        )

        image_score = None

        lost_image = lost_item.get("image")
        found_image = found_item.get("image")

        if lost_image and found_image:
            try:
                image_score, image_result = compare_images(
                    lost_image,
                    found_image
                )
            except (FileNotFoundError, OSError, ValueError) as error:
                print(f"Image matching skipped: {error}")

        metadata_score = calculate_metadata_score(
            lost_item,
            found_item
        )

        final_score = calculate_combined_score(
            text_score,
            image_score,
            metadata_score
        )

        if final_score >= 50:
            match_status = "High-Priority Candidate"
        elif final_score >= 30:
            match_status = "Needs Manual Review"
        else:
            match_status = "Low-Priority Candidate"

        results.append({
            "found_item_id": found_item.get("id"),
            "found_item": found_item.get("description", ""),
            "text_score": text_score,
            "image_score": image_score,
            "metadata_score": metadata_score,
            "final_score": final_score,
            "match_status": match_status
        })

    results.sort(
        key=lambda x: x["final_score"],
        reverse=True
    )

    return results


if __name__ == "__main__":

    lost_item = {
        "id": 1,
        "description": "Black leather wallet",
        "category": "Wallet",
        "colour": "Black",
        "location": "Library",
        "date": "2026-11-17",
        "image": None
    }

    found_items = [
        {
            "id": 2,
            "description": "Black wallet found near library",
            "category": "Wallet",
            "colour": "Black",
            "location": "Library",
            "date": "2026-11-17",
            "image": None
        },
        {
            "id": 3,
            "description": "Brown leather purse",
            "category": "Wallet",
            "colour": "Brown",
            "location": "Canteen",
            "date": "2026-11-16",
            "image": None
        },
        {
            "id": 4,
            "description": "Red school bag",
            "category": "Bags",
            "colour": "Red",
            "location": "Classroom",
            "date": "2026-11-15",
            "image": None
        },
        {
            "id": 5,
            "description": "Black leather wallet found in classroom",
            "category": "Wallet",
            "colour": "Black",
            "location": "Classroom",
            "date": "2026-11-17",
            "image": None
        }
    ]

    results = find_best_matches(
        lost_item,
        found_items
    )

    for result in results:
        print("\n------------------------------")
        print("Found Item ID:", result["found_item_id"])
        print("Found Item:", result["found_item"])
        print("Text Similarity:", result["text_score"])
        print("Image Similarity:", result["image_score"])
        print("Metadata Similarity:", result["metadata_score"])
        print("Final Score:", result["final_score"])
        print("Status:", result["match_status"])