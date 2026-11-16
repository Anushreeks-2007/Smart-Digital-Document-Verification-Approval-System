import os
import uuid
import sqlite3
from datetime import datetime

from flask import (
    Blueprint,
    request,
    jsonify,
    session,
    current_app,
    send_from_directory
)

from PIL import Image

from database.db import get_db_connection
from app.utils.auth_helpers import login_required
from app.utils.image_helpers import validate_image


items = Blueprint("items", __name__, url_prefix="/api/items")


# =====================================
# HELPER FUNCTIONS
# =====================================

def get_item_by_id(conn, item_id):
    return conn.execute(
        """
        SELECT *
        FROM items
        WHERE id = ? AND status = 'active'
        """,
        (item_id,)
    ).fetchone()


def can_manage_item(conn, item, user_id):

    if item["user_id"] == user_id:
        return True

    user = conn.execute(
        "SELECT role FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()

    return user is not None and user["role"] == "admin"


# =====================================
# 1. REPORT A LOST OR FOUND ITEM
# =====================================

@items.route("/", methods=["POST"])
@login_required
def report_item():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid request data"}), 400

    item_name = data.get("item_name")
    item_type = data.get("item_type")

    if not isinstance(item_name, str) or not isinstance(item_type, str):
        return jsonify({
            "error": "Item name and item type are required"
        }), 400

    item_name = item_name.strip()
    item_type = item_type.strip().lower()

    if not item_name or len(item_name) > 100:
        return jsonify({"error": "Invalid item name"}), 400

    if item_type not in ["lost", "found"]:
        return jsonify({
            "error": "Item type must be lost or found"
        }), 400

    optional_fields = [
        "category", "colour", "description", "location"
    ]

    values = {}

    for field in optional_fields:

        value = data.get(field)

        if value is not None and not isinstance(value, str):
            return jsonify({
                "error": f"{field} must be text"
            }), 400

        value = value.strip() if value else None

        if value and len(value) > 1000:
            return jsonify({
                "error": f"{field} is too long"
            }), 400

        values[field] = value

    item_date = data.get("item_date")

    if item_date is not None:

        if not isinstance(item_date, str):
            return jsonify({"error": "Invalid item date"}), 400

        try:
            datetime.strptime(item_date, "%Y-%m-%d")
        except ValueError:
            return jsonify({
                "error": "Date must be in YYYY-MM-DD format"
            }), 400

    try:

        with get_db_connection() as conn:

            cursor = conn.execute(
                """
                INSERT INTO items (
                    user_id,
                    item_name,
                    category,
                    colour,
                    description,
                    item_type,
                    location,
                    item_date
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session["user_id"],
                    item_name,
                    values["category"],
                    values["colour"],
                    values["description"],
                    item_type,
                    values["location"],
                    item_date
                )
            )

            item_id = cursor.lastrowid

        return jsonify({
            "message": "Item reported successfully",
            "item_id": item_id
        }), 201

    except sqlite3.Error:
        return jsonify({
            "error": "Could not report item"
        }), 500


# =====================================
# 2. VIEW ALL ACTIVE ITEMS
# =====================================

@items.route("/", methods=["GET"])
def get_items():

    item_type = request.args.get("item_type")
    category = request.args.get("category")
    location = request.args.get("location")
    search = request.args.get("search")

    try:
        limit = int(request.args.get("limit", 20))
        offset = int(request.args.get("offset", 0))

    except ValueError:
        return jsonify({
            "error": "Limit and offset must be numbers"
        }), 400

    if limit < 1 or limit > 100 or offset < 0:
        return jsonify({
            "error": "Invalid pagination values"
        }), 400

    query = """
        SELECT
            id,
            user_id,
            item_name,
            category,
            colour,
            description,
            item_type,
            location,
            item_date,
            image_path,
            status,
            created_at
        FROM items
        WHERE status = 'active'
    """

    parameters = []

    if item_type:

        item_type = item_type.strip().lower()

        if item_type not in ["lost", "found"]:
            return jsonify({
                "error": "Invalid item type"
            }), 400

        query += " AND item_type = ?"
        parameters.append(item_type)

    if category:
        query += " AND category = ?"
        parameters.append(category.strip())

    if location:
        query += " AND location LIKE ?"
        parameters.append(f"%{location.strip()}%")

    if search:

        query += """
            AND (
                item_name LIKE ?
                OR description LIKE ?
                OR category LIKE ?
            )
        """

        search_value = f"%{search.strip()}%"

        parameters.extend([
            search_value,
            search_value,
            search_value
        ])

    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"

    parameters.extend([limit, offset])

    try:

        with get_db_connection() as conn:
            rows = conn.execute(
                query,
                parameters
            ).fetchall()

        return jsonify({
            "items": [dict(row) for row in rows],
            "limit": limit,
            "offset": offset
        }), 200

    except sqlite3.Error:
        return jsonify({
            "error": "Could not retrieve items"
        }), 500


# =====================================
# 3. VIEW ONE ITEM
# =====================================

@items.route("/<int:item_id>", methods=["GET"])
def get_item(item_id):

    try:

        with get_db_connection() as conn:
            item = get_item_by_id(conn, item_id)

        if item is None:
            return jsonify({
                "error": "Item not found"
            }), 404

        return jsonify({
            "item": dict(item)
        }), 200

    except sqlite3.Error:
        return jsonify({
            "error": "Could not retrieve item"
        }), 500


# =====================================
# 4. EDIT AN ITEM
# =====================================

@items.route("/<int:item_id>", methods=["PUT"])
@login_required
def update_item(item_id):

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid request data"
        }), 400

    allowed_fields = {
        "item_name",
        "category",
        "colour",
        "description",
        "item_type",
        "location",
        "item_date"
    }

    if not data or not set(data.keys()).issubset(allowed_fields):
        return jsonify({
            "error": "Invalid or unsupported fields"
        }), 400

    try:

        with get_db_connection() as conn:

            item = get_item_by_id(conn, item_id)

            if item is None:
                return jsonify({
                    "error": "Item not found"
                }), 404

            if not can_manage_item(conn, item, session["user_id"]):
                return jsonify({
                    "error": "You cannot edit this item"
                }), 403

            updates = {}

            for field, value in data.items():

                if field == "item_name":

                    if not isinstance(value, str) or not value.strip():
                        return jsonify({
                            "error": "Invalid item name"
                        }), 400

                    value = value.strip()

                    if len(value) > 100:
                        return jsonify({
                            "error": "Item name is too long"
                        }), 400

                elif field == "item_type":

                    if not isinstance(value, str):
                        return jsonify({
                            "error": "Invalid item type"
                        }), 400

                    value = value.strip().lower()

                    if value not in ["lost", "found"]:
                        return jsonify({
                            "error": "Invalid item type"
                        }), 400

                elif field == "item_date":

                    if value is not None:

                        if not isinstance(value, str):
                            return jsonify({
                                "error": "Invalid item date"
                            }), 400

                        try:
                            datetime.strptime(value, "%Y-%m-%d")
                        except ValueError:
                            return jsonify({
                                "error": "Date must be in YYYY-MM-DD format"
                            }), 400

                else:

                    if value is not None and not isinstance(value, str):
                        return jsonify({
                            "error": f"{field} must be text"
                        }), 400

                    value = value.strip() if value else None

                    if value and len(value) > 1000:
                        return jsonify({
                            "error": f"{field} is too long"
                        }), 400

                updates[field] = value

            assignments = ", ".join(
                f"{field} = ?" for field in updates
            )

            values = list(updates.values())
            values.append(item_id)

            conn.execute(
                f"""
                UPDATE items
                SET {assignments}
                WHERE id = ?
                """,
                values
            )

        return jsonify({
            "message": "Item updated successfully"
        }), 200

    except sqlite3.Error:
        return jsonify({
            "error": "Could not update item"
        }), 500


# =====================================
# 5. SOFT DELETE AN ITEM
# =====================================

@items.route("/<int:item_id>", methods=["DELETE"])
@login_required
def delete_item(item_id):

    try:

        with get_db_connection() as conn:

            item = get_item_by_id(conn, item_id)

            if item is None:
                return jsonify({
                    "error": "Item not found"
                }), 404

            if not can_manage_item(conn, item, session["user_id"]):
                return jsonify({
                    "error": "You cannot delete this item"
                }), 403

            conn.execute(
                """
                UPDATE items
                SET status = 'deleted'
                WHERE id = ?
                """,
                (item_id,)
            )

        return jsonify({
            "message": "Item deleted successfully"
        }), 200

    except sqlite3.Error:
        return jsonify({
            "error": "Could not delete item"
        }), 500


# =====================================
# 6. UPLOAD ITEM IMAGE
# =====================================

@items.route("/<int:item_id>/image", methods=["POST"])
@login_required
def upload_item_image(item_id):

    image_file = request.files.get("image")

    if image_file is None or not image_file.filename:
        return jsonify({
            "error": "No image uploaded"
        }), 400

    extension = image_file.filename.rsplit(".", 1)[-1].lower()

    if extension not in current_app.config["ALLOWED_EXTENSIONS"]:
        return jsonify({
            "error": "Unsupported image extension"
        }), 400

    valid, error = validate_image(image_file)

    if not valid:
        return jsonify({
            "error": error
        }), 400

    format_extensions = {
        "JPEG": "jpg",
        "PNG": "png",
        "WEBP": "webp"
    }

    image_file.stream.seek(0)

    try:

        with Image.open(image_file.stream) as image:
            actual_format = image.format

    except (OSError, ValueError):
        return jsonify({
            "error": "Invalid image file"
        }), 400

    expected_extension = format_extensions.get(actual_format)

    if expected_extension is None:
        return jsonify({
            "error": "Unsupported image format"
        }), 400

    allowed_extensions = (
        {"jpg", "jpeg"}
        if expected_extension == "jpg"
        else {expected_extension}
    )

    if extension not in allowed_extensions:
        return jsonify({
            "error": "File extension does not match image format"
        }), 400

    image_file.stream.seek(0)

    filename = f"{uuid.uuid4().hex}.{expected_extension}"

    upload_folder = current_app.config["UPLOAD_FOLDER"]

    try:

        with get_db_connection() as conn:

            item = get_item_by_id(conn, item_id)

            if item is None:
                return jsonify({
                    "error": "Item not found"
                }), 404

            if not can_manage_item(conn, item, session["user_id"]):
                return jsonify({
                    "error": "You cannot upload an image for this item"
                }), 403

            os.makedirs(upload_folder, exist_ok=True)

            file_path = os.path.join(upload_folder, filename)

            image_file.save(file_path)

            try:

                conn.execute(
                    """
                    UPDATE items
                    SET image_path = ?
                    WHERE id = ?
                    """,
                    (filename, item_id)
                )

            except sqlite3.Error:

                if os.path.exists(file_path):
                    os.remove(file_path)

                raise

        return jsonify({
            "message": "Image uploaded successfully",
            "image_url": f"/api/items/images/{filename}"
        }), 201

    except sqlite3.Error:
        return jsonify({
            "error": "Could not save image"
        }), 500


# =====================================
# 7. SERVE ITEM IMAGE
# =====================================

@items.route("/images/<path:filename>", methods=["GET"])
def get_item_image(filename):

    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"],
        filename
    )