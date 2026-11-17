import torch
import torch.nn.functional as F
from torchvision import models
from PIL import Image
import os


# STEP 1: Load pretrained MobileNetV2
weights = models.MobileNet_V2_Weights.DEFAULT

model = models.mobilenet_v2(weights=weights)

# Remove the final classification layer to extract image features
model.classifier = torch.nn.Identity()

model.eval()

# Use the preprocessing required by the pretrained model
preprocess = weights.transforms()


# STEP 2: Extract features from an image
def extract_image_features(image_path):

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    image = Image.open(image_path).convert("RGB")

    image_tensor = preprocess(image).unsqueeze(0)

    with torch.no_grad():
        features = model(image_tensor)

    return F.normalize(features, p=2, dim=1)


# STEP 3: Compare two images
def compare_images(image1_path, image2_path):

    features1 = extract_image_features(image1_path)
    features2 = extract_image_features(image2_path)

    similarity = F.cosine_similarity(
        features1,
        features2
    )

    score = round(similarity.item() * 100, 2)

    if score >= 70:
        result = "High Visual Similarity"
    elif score >= 40:
        result = "Moderate Visual Similarity"
    else:
        result = "Low Visual Similarity"

    return score, result


# STEP 4: Test image matching
if __name__ == "__main__":

    folder = "ai_matching/sample_images"

    lost_image = os.path.join(folder, "lost_item.jpg")
    found_image = os.path.join(folder, "found_item.jpg")
    different_image = os.path.join(folder, "different_item.jpg")

    # Test 1: Lost bottle vs Found bottle
    score1, result1 = compare_images(lost_image, found_image)

    # Test 2: Lost bottle vs Different item (Backpack)
    score2, result2 = compare_images(lost_image, different_image)

    print("\nAI-BASED IMAGE MATCHING")
    print("=" * 60)

    print("\nTEST 1: Bottle vs Bottle")
    print(f"Similarity Score: {score1}%")
    print(f"Result: {result1}")

    print("\nTEST 2: Bottle vs Backpack")
    print(f"Similarity Score: {score2}%")
    print(f"Result: {result2}")

    print("\n" + "=" * 60)