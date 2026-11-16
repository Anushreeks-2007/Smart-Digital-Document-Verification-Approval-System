import os

try:
    from .text_matching import compare_items
    from .image_matching import compare_images
    from .metadata_matching import calculate_metadata_score

except ImportError:
    from text_matching import compare_items
    from image_matching import compare_images
    from metadata_matching import calculate_metadata_score


# STEP 1: Calculate combined matching score
def calculate_combined_score(text_score, image_score, metadata_score):

    if image_score is None:
        # If image is unavailable, redistribute its weight
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


# STEP 2: Compare lost item with found items
def find_best_matches(lost_item, found_items):

    results = []

    for found_item in found_items:

        # Text matching
        text_score, text_result = compare_items(
            lost_item["description"],
            found_item["description"]
        )

        # Image matching with missing-image handling
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

        # Metadata matching
        metadata_score = calculate_metadata_score(
            lost_item,
            found_item
        )

        # Combined matching
        final_score = calculate_combined_score(
            text_score,
            image_score,
            metadata_score
        )
                # Classify matching results
        if final_score >= 50:
            match_status = "High-Priority Candidate"

        elif final_score >= 30:
            match_status = "Needs Manual Review"

        else:
            match_status = "Low-Priority Candidate"

        results.append({

            "found_item": found_item["description"],
            "text_score": text_score,
            "image_score": image_score,
            "metadata_score": metadata_score,
            "final_score": final_score,
            "match_status": match_status

        })

    # Rank matches from highest to lowest
    results.sort(
        key=lambda x: x["final_score"],
        reverse=True
    )

    return results


# STEP 3: Test combined AI matching
if __name__ == "__main__":

    folder = "ai_matching/sample_images"

    lost_item = {

        "description": "Blue grey reusable water bottle",
        "category": "Bottle",
        "colour": "Blue",
        "location": "Library",
        "date": "2026-11-10",
        "image": os.path.join(folder, "lost_item.jpg")

    }

    found_items = [

        {
            "description": "Dark blue reusable water bottle",
            "category": "Bottle",
            "colour": "Blue",
            "location": "Library",
            "date": "2026-11-11",
            "image": os.path.join(folder, "found_item.jpg")
        },

        {
            "description": "Red school backpack",
            "category": "Bag",
            "colour": "Red",
            "location": "Canteen",
            "date": "2026-11-15",
            "image": os.path.join(folder, "different_item.jpg")
        },

        {
            "description": "Blue water bottle found near classroom",
            "category": "Bottle",
            "colour": "Blue",
            "location": "Classroom",
            "date": "2026-11-10",
            "image": None
        },
                        
        {
            "description": "Blue reusable bottle found near classroom",
            "category": "Bottle",
            "colour": "Blue",
            "location": "Classroom",
            "date": "2026-11-10",
            "image": os.path.join(folder, "missing_image.jpg")
        }


    ]

    results = find_best_matches(lost_item, found_items)

    print("\nCOMBINED AI-BASED LOST AND FOUND MATCHING")
    print("=" * 75)

    for index, item in enumerate(results, start=1):

        print(f"\nRank {index}: {item['found_item']}")

        print(f"Text Similarity: {item['text_score']}%")

        if item["image_score"] is None:
            print("Image Similarity: Not Available")
        else:
            print(f"Image Similarity: {item['image_score']}%")

        print(f"Metadata Similarity: {item['metadata_score']}%")
        print(f"FINAL MATCH SCORE: {item['final_score']}%")
        print(f"Match Status: {item['match_status']}")

    print("\n" + "=" * 75)