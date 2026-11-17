from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# STEP 1: Compare two report descriptions
def calculate_similarity(report1, report2):

    descriptions = [report1, report2]

    vectorizer = TfidfVectorizer(ngram_range=(1, 2))

    matrix = vectorizer.fit_transform(descriptions)

    similarity = cosine_similarity(
        matrix[0:1],
        matrix[1:2]
    )[0][0]

    return round(similarity * 100, 2)


# STEP 2: Detect duplicate reports
def detect_duplicate(new_report, existing_reports):

    results = []

    for report in existing_reports:

        score = calculate_similarity(
            new_report,
            report
        )

        if score >= 20:

            results.append({
                "report": report,
                "similarity": score,
                "status": "Possible Duplicate"
            })

        else:

            results.append({
                "report": report,
                "similarity": score,
                "status": "Different Report"
            })

    results.sort(
        key=lambda x: x["similarity"],
        reverse=True
    )

    return results


# STEP 3: Test duplicate detection
if __name__ == "__main__":

    new_report = "Blue reusable water bottle lost near library"

    existing_reports = [

        "Blue water bottle missing from the library",

        "Red school backpack found in classroom",

        "Blue reusable bottle lost near college library",

        "Black headphones found in cafeteria"

    ]

    results = detect_duplicate(
        new_report,
        existing_reports
    )

    print("\nAI-BASED DUPLICATE REPORT DETECTION")
    print("=" * 70)

    print(f"\nNew Report: {new_report}\n")

    for index, item in enumerate(results, start=1):

        print(f"Report {index}: {item['report']}")
        print(f"Similarity: {item['similarity']}%")
        print(f"Status: {item['status']}")
        print("-" * 70)

    print("=" * 70)