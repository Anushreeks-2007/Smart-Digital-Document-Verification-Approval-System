from PIL import Image, UnidentifiedImageError


ALLOWED_IMAGE_FORMATS = {
    "JPEG",
    "PNG",
    "WEBP"
}


def validate_image(image_file):

    if image_file is None or not image_file.filename:
        return False, "No image selected"

    try:
        # Check the actual image content, not just its extension.
        image_file.stream.seek(0)

        with Image.open(image_file.stream) as image:
            image_format = image.format
            image.verify()

        image_file.stream.seek(0)

        if image_format not in ALLOWED_IMAGE_FORMATS:
            return False, "Only JPG, PNG and WEBP images are allowed"

        return True, None

    except (UnidentifiedImageError, OSError, ValueError):
        image_file.stream.seek(0)
        return False, "Invalid or corrupted image file"