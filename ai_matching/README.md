# AI-Based Lost and Found Matching Module

## Overview
This module identifies and ranks possible matches between lost and found item reports using text similarity, image similarity and metadata comparison.

## Features
1. Text similarity using TF-IDF and cosine similarity.
2. Image similarity using MobileNetV2.
3. Metadata comparison using category, colour, location and date.
4. Combined weighted matching score.
5. Automatic ranking of possible matches.
6. Duplicate report detection.
7. Match-result classification.
8. Handling of missing and invalid image paths.

## Technologies
- Python
- Scikit-learn
- PyTorch
- Torchvision
- Pillow

## Main Integration Function

Import the matching function into the Flask backend:

```python
from ai_matching.smart_matching import find_best_matches
```

Call the function:

```python
results = find_best_matches(lost_item, found_items)
```

## Required Input Format

Each item must contain:

| Field | Description |
|---|---|
| description | Item description |
| category | Item category |
| colour | Item colour |
| location | Item location |
| date | Date in YYYY-MM-DD format |
| image | Image file path or None |

Both `lost_item` and every entry in `found_items` must follow this format.

Image paths must point to accessible image files. If an image is unavailable, use `None`.

## Output

The function returns a list of ranked matching results containing:

- found_item
- text_score
- image_score
- metadata_score
- final_score
- match_status

## Match Classification

- 50% or above: High-Priority Candidate
- 30%–49.99%: Needs Manual Review
- Below 30%: Low-Priority Candidate

These classifications are preliminary matching priorities, not probabilities of ownership.

## Important Note
AI matching only identifies possible matches. Final ownership verification and item handover must be handled by an authorised administrator.