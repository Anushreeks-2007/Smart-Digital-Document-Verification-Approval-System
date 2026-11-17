import os
import sqlite3

from flask import Blueprint, jsonify, session, current_app

from database.db import get_db_connection
from app.utils.auth_helpers import login_required
from ai_matching.smart_matching import find_best_matches


matching = Blueprint(
    "matching",
    __name__,
    url_prefix="/api/matching"
)


@matching.route("/<int:item_id>", methods=["GET"])
@login_required
def get_matches(item_id):

    try:
        with get_db_connection() as conn:

            # Find the lost item
            lost_item = conn.execute(
                """
                SELECT *
                FROM items
                WHERE id = ?
                AND item_type = 'lost'
                AND status = 'active'
                """,
                (item_id,)
            ).fetchone()

            if lost_item is None:
                return jsonify({
                    "error": "Active lost item not found"
                }), 404

            # Only the owner or an admin can request matches
            user = conn.execute(
                "SELECT role FROM users WHERE id = ?",
                (session["user_id"],)
            ).fetchone()

            if (
                lost_item["user_id"] != session["user_id"]
                and (user is None or user["role"] != "admin")
            ):
                return jsonify({
                    "error": "You cannot view matches for this item"
                }), 403

            # Retrieve active found items
            found_rows = conn.execute(
                """
                SELECT *
                FROM items
                WHERE item_type = 'found'
                AND status = 'active'
                """
            ).fetchall()

        if not found_rows:
            return jsonify({
                "message": "No found items available for matching",
                "matches": []
            }), 200

        upload_folder = current_app.config["UPLOAD_FOLDER"]

        # Convert database records into AI input
        lost_image = (
            os.path.join(upload_folder, lost_item["image_path"])
            if lost_item["image_path"]
            else None
        )

        if lost_image and not os.path.isfile(lost_image):
            lost_image = None

        lost_data = {
            "id": lost_item["id"],
            "description": (
                lost_item["description"] or lost_item["item_name"]
            ),
            "category": lost_item["category"],
            "colour": lost_item["colour"],
            "location": lost_item["location"],
            "date": lost_item["item_date"],
            "image": lost_image
        }

        found_items = []
        found_lookup = {}

        for row in found_rows:

            image_path = (
                os.path.join(upload_folder, row["image_path"])
                if row["image_path"]
                else None
            )

            if image_path and not os.path.isfile(image_path):
                image_path = None

            found_data = {
                "id": row["id"],
                "description": (
                    row["description"] or row["item_name"]
                ),
                "category": row["category"],
                "colour": row["colour"],
                "location": row["location"],
                "date": row["item_date"],
                "image": image_path
            }

            found_items.append(found_data)
            found_lookup[row["id"]] = row

        # Run AI matching
        results = find_best_matches(
            lost_data,
            found_items
        )

        matches = []

        for result in results:

            found_id = result.get("found_item_id")
            row = found_lookup.get(found_id)

            matches.append({
                "found_item_id": found_id,
                "item": {
                    "item_name": row["item_name"],
                    "category": row["category"],
                    "colour": row["colour"],
                    "description": row["description"],
                    "location": row["location"],
                    "item_date": row["item_date"],
                    "image_url": (
                        f"/api/items/images/{row['image_path']}"
                        if row["image_path"]
                        else None
                    )
                } if row else None,
                "text_score": result["text_score"],
                "image_score": result["image_score"],
                "metadata_score": result["metadata_score"],
                "final_score": result["final_score"],
                "match_status": result["match_status"]
            })

        return jsonify({
            "lost_item_id": item_id,
            "total_matches": len(matches),
            "matches": matches
        }), 200

    except sqlite3.Error:
        current_app.logger.exception("Database error during AI matching")
        return jsonify({
            "error": "Could not retrieve matching items"
        }), 500

    except Exception:
        current_app.logger.exception("AI matching failed")
        return jsonify({
            "error": "AI matching could not be completed"
        }), 500