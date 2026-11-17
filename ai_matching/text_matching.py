from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re


# STEP 1: Preprocess item descriptions
def preprocess_text(text):

    synonyms = {
        "phone": "mobile",
        "phones": "mobile",
        "cover": "case",
        "covers": "case"
    }

    words = re.findall(r'\b\w+\b', text.lower())
    words = [synonyms.get(word, word) for word in words]

    return " ".join(words)


# STEP 2: Compare two item descriptions
def compare_items(lost_item, found_item):

    lost_item = preprocess_text(lost_item)
    found_item = preprocess_text(found_item)

    descriptions = [lost_item, found_item]

    vectorizer = TfidfVectorizer(ngram_range=(1, 2))

    tfidf_matrix = vectorizer.fit_transform(descriptions)

    similarity = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:2]
    )[0][0]

    score = round(similarity * 100, 2)

    if score >= 15:
        result = "Possible Match"
    else:
        result = "No Match"

    return score, result


# STEP 3: Compare one lost item with multiple found items
def rank_matches(lost_item, found_items):

    results = []

    for found_item in found_items:

        score, result = compare_items(lost_item, found_item)

        results.append({
            "lost_item": lost_item,
            "found_item": found_item,
            "score": score,
            "result": result
        })

    # Sort results from highest similarity to lowest
    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return results


# STEP 4: Test the AI matching system
if __name__ == "__main__":

    lost_item = "Black leather wallet"

    found_items = [
        "Black wallet found near library",
        "Brown leather purse",
        "Red school bag",
        "Black leather wallet found in classroom",
        "Small blue water bottle"
    ]

    results = rank_matches(lost_item, found_items)

    print("\nAI-BASED LOST AND FOUND ITEM MATCHING")
    print("=" * 100)

    print(f"Lost Item: {lost_item}\n")

    print(
        f"{'Found Item':45} {'Score':15} {'Result'}"
    )

    print("-" * 100)

    for item in results:

        print(
            f"{item['found_item']:45} "
            f"{item['score']:<15} "
            f"{item['result']}"
        )

    print("=" * 100)