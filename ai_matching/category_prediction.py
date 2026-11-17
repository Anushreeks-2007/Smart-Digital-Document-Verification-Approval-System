from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


# Sample training descriptions and their categories
training_data = [
    ("blue water bottle", "Bottle"),
    ("steel drinking bottle", "Bottle"),
    ("plastic reusable bottle", "Bottle"),
    ("black school backpack", "Bag"),
    ("red travel bag", "Bag"),
    ("small college handbag", "Bag"),
    ("black leather wallet", "Wallet"),
    ("brown purse wallet", "Wallet"),
    ("money wallet", "Wallet"),
    ("mobile phone", "Electronics"),
    ("laptop charger", "Electronics"),
    ("wireless earphones", "Electronics"),
    ("house keys", "Keys"),
    ("car keychain", "Keys"),
    ("key ring", "Keys"),
    ("college textbook", "Books"),
    ("notebook and textbook", "Books"),
    ("printed study notes", "Books"),
    ("wrist watch", "Accessories"),
    ("silver bracelet", "Accessories"),
    ("black sunglasses", "Accessories"),
    ("blue jacket", "Clothing"),
    ("white shirt", "Clothing"),
    ("black sweater", "Clothing"),
]

# Prepare the machine learning model
descriptions = [item[0] for item in training_data]
categories = [item[1] for item in training_data]

category_model = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
    ("classifier", LogisticRegression(max_iter=1000))
])

category_model.fit(descriptions, categories)


def predict_category(description):
    """Predict an item's category from its description."""

    if not description or not description.strip():
        return "Unknown"

    prediction = category_model.predict([description])[0]
    return prediction


if __name__ == "__main__":
    test_items = [
        "dark blue reusable water bottle",
        "black college backpack",
        "leather money wallet",
        "wireless bluetooth headphones",
        "silver house keys"
    ]

    print("\nAI-BASED ITEM CATEGORY PREDICTION")
    print("=" * 45)

    for item in test_items:
        result = predict_category(item)
        print(f"Item: {item}")
        print(f"Predicted Category: {result}")
        print("-" * 45)