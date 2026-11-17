# AI-Based Lost and Found Matching Module

## 1. Overview

This module identifies and ranks possible matches between lost and found item reports using AI-based text matching, image similarity, metadata comparison and automatic category prediction.

It helps users and administrators find potentially matching belongings more efficiently.

## 2. Features

1. **Text Similarity:** Uses TF-IDF and cosine similarity to compare item descriptions.
2. **Image Similarity:** Uses pretrained MobileNetV2 to extract image features and compare visual similarity.
3. **Metadata Matching:** Compares category, colour, location and date.
4. **Combined AI Matching:** Calculates a weighted score using text, image and metadata similarity.
5. **Automatic Category Prediction:** Uses TF-IDF and Logistic Regression to predict item categories from descriptions when a category is missing.
6. **Duplicate Detection:** Identifies potentially similar lost and found reports.
7. **Match Ranking:** Ranks possible matches from highest to lowest score.
8. **Missing Image Handling:** Continues matching when images are unavailable or invalid.

## 3. Technologies Used

- Python
- Scikit-learn
- PyTorch
- Torchvision
- OpenCV
- Pillow
- NumPy
- Pandas

## 4. AI Components

| Component | Technique |
|---|---|
| Text Matching | TF-IDF and Cosine Similarity |
| Image Matching | MobileNetV2 |
| Metadata Matching | Weighted Attribute Comparison |
| Category Prediction | TF-IDF and Logistic Regression |
| Duplicate Detection | TF-IDF and Cosine Similarity |

## 5. Main Integration Function

Import the matching function into the Flask backend:

```python
from ai_matching.smart_matching import find_best_matches
```

Call the function:

```python
results = find_best_matches(lost_item, found_items)
```

## 6. Required Input Format

Each item should contain:

| Field | Description |
|---|---|
| description | Item description |
| category | Item category (optional; predicted if missing) |
| colour | Item colour |
| location | Item location |
| date | Date in YYYY-MM-DD format |
| image | Image file path or None |

Both `lost_item` and every entry in `found_items` should follow this format.

If an image is unavailable, use `None`.

## 7. Output

The function returns ranked matching results containing:

- found_item
- text_score
- image_score
- metadata_score
- final_score
- match_status

## 8. Match Classification

- 50% or above: High-Priority Candidate
- 30%–49.99%: Needs Manual Review
- Below 30%: Low-Priority Candidate

These classifications represent preliminary matching priorities, not probabilities of ownership.

## 9. Important Notes

- Category prediction uses a sample training dataset and is a prototype. Prediction quality depends on the training data.
- Image similarity uses general pretrained visual features and does not establish that two images show the same physical object.
- Missing images are handled by redistributing the image matching weight.
- AI matching only identifies possible matches. Final ownership verification and item handover must be handled by an authorised administrator.