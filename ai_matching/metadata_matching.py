from datetime import datetime


# STEP 1: Compare categories
def compare_category(category1, category2):

    if category1.lower() == category2.lower():
        return 100

    return 0


# STEP 2: Compare colours
def compare_colour(colour1, colour2):

    if colour1.lower() == colour2.lower():
        return 100

    return 0


# STEP 3: Compare locations
def compare_location(location1, location2):

    if location1.lower() == location2.lower():
        return 100

    return 0


# STEP 4: Compare dates
def compare_date(date1, date2):

    date1 = datetime.strptime(date1, "%Y-%m-%d")
    date2 = datetime.strptime(date2, "%Y-%m-%d")

    difference = abs((date1 - date2).days)

    if difference == 0:
        return 100
    elif difference <= 1:
        return 80
    elif difference <= 3:
        return 60
    elif difference <= 7:
        return 30
    else:
        return 0


# STEP 5: Calculate combined metadata score
def calculate_metadata_score(lost_item, found_item):

    category_score = compare_category(
        lost_item["category"],
        found_item["category"]
    )

    colour_score = compare_colour(
        lost_item["colour"],
        found_item["colour"]
    )

    location_score = compare_location(
        lost_item["location"],
        found_item["location"]
    )

    date_score = compare_date(
        lost_item["date"],
        found_item["date"]
    )

    final_score = (
        category_score * 0.30 +
        colour_score * 0.25 +
        location_score * 0.25 +
        date_score * 0.20
    )

    return round(final_score, 2)


# STEP 6: Test metadata matching
if __name__ == "__main__":

    lost_item = {
        "category": "Bottle",
        "colour": "Blue",
        "location": "Library",
        "date": "2026-11-10"
    }

    found_items = [

        {
            "category": "Bottle",
            "colour": "Blue",
            "location": "Library",
            "date": "2026-11-10"
        },

        {
            "category": "Bottle",
            "colour": "Red",
            "location": "Library",
            "date": "2026-11-11"
        },

        {
            "category": "Bag",
            "colour": "Red",
            "location": "Canteen",
            "date": "2026-11-15"
        }
    ]

    print("\nAI-BASED METADATA MATCHING")
    print("=" * 65)

    for index, found_item in enumerate(found_items, start=1):

        score = calculate_metadata_score(
            lost_item,
            found_item
        )

        print(f"\nMatch {index}")
        print(f"Category: {found_item['category']}")
        print(f"Colour: {found_item['colour']}")
        print(f"Location: {found_item['location']}")
        print(f"Date: {found_item['date']}")
        print(f"Metadata Similarity: {score}%")

    print("\n" + "=" * 65)