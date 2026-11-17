from flask import Blueprint, request, jsonify, session

from database.db import get_db_connection
from app.utils.auth_helpers import login_required, admin_required


workflow = Blueprint("workflow", __name__, url_prefix="/api")


# =====================================
# CLAIMS
# =====================================

@workflow.route("/claims", methods=["POST"])
@login_required
def submit_claim():
    user_id = session.get("user_id")
    data = request.get_json(silent=True) or {}

    item_id = data.get("item_id")
    description = data.get("claim_description", "").strip()

    if not item_id:
        return jsonify({"error": "Item ID is required."}), 400

    if not isinstance(item_id, int) or isinstance(item_id, bool):
        return jsonify({"error": "Invalid item ID."}), 400

    if not description:
        return jsonify({"error": "Claim description is required."}), 400

    try:
        with get_db_connection() as conn:
            item = conn.execute(
                """
                SELECT id, user_id, item_name, item_type, status
                FROM items
                WHERE id = ?
                """,
                (item_id,)
            ).fetchone()

            if item is None:
                return jsonify({"error": "Item not found."}), 404

            if item["item_type"].lower() != "found":
                return jsonify({
                    "error": "Claims can only be submitted for found items."
                }), 400

            if item["status"] != "active":
                return jsonify({
                    "error": "This item is no longer available for claims."
                }), 409

            if item["user_id"] == user_id:
                return jsonify({
                    "error": "You cannot claim an item you reported."
                }), 403

            existing = conn.execute(
                """
                SELECT id FROM claims
                WHERE item_id = ? AND user_id = ?
                AND status = 'pending'
                """,
                (item_id, user_id)
            ).fetchone()

            if existing:
                return jsonify({
                    "error": "You already have a pending claim for this item."
                }), 409

            cursor = conn.execute(
                """
                INSERT INTO claims
                (item_id, user_id, claim_description)
                VALUES (?, ?, ?)
                """,
                (item_id, user_id, description)
            )

            claim_id = cursor.lastrowid

            conn.execute(
                """
                INSERT INTO notifications (user_id, message)
                VALUES (?, ?)
                """,
                (
                    item["user_id"],
                    f"A new claim has been submitted for your item: {item['item_name']}."
                )
            )

        return jsonify({
            "message": "Claim submitted successfully.",
            "claim_id": claim_id,
            "status": "pending"
        }), 201

    except Exception as error:
        print("Claim submission error:", error)
        return jsonify({"error": "Could not submit claim."}), 500


@workflow.route("/claims", methods=["GET"])
@login_required
def get_claims():
    user_id = session.get("user_id")

    try:
        with get_db_connection() as conn:
            user = conn.execute(
                "SELECT role FROM users WHERE id = ?",
                (user_id,)
            ).fetchone()

            if user is None:
                return jsonify({"error": "User not found."}), 404

            if user["role"] == "admin":
                rows = conn.execute(
                    """
                    SELECT
                        c.id,
                        c.item_id,
                        c.user_id,
                        c.claim_description,
                        c.status,
                        c.created_at,
                        i.item_name,
                        i.user_id AS item_owner_id
                    FROM claims c
                    JOIN items i ON i.id = c.item_id
                    ORDER BY c.created_at DESC
                    """
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT
                        c.id,
                        c.item_id,
                        c.user_id,
                        c.claim_description,
                        c.status,
                        c.created_at,
                        i.item_name,
                        i.user_id AS item_owner_id
                    FROM claims c
                    JOIN items i ON i.id = c.item_id
                    WHERE c.user_id = ? OR i.user_id = ?
                    ORDER BY c.created_at DESC
                    """,
                    (user_id, user_id)
                ).fetchall()

        return jsonify({
            "claims": [dict(row) for row in rows]
        }), 200

    except Exception as error:
        print("Get claims error:", error)
        return jsonify({"error": "Could not retrieve claims."}), 500


@workflow.route("/claims/<int:claim_id>/review", methods=["PUT"])
@admin_required
def review_claim(claim_id):
    admin_id = session.get("user_id")
    data = request.get_json(silent=True) or {}

    new_status = data.get("status", "").strip().lower()

    if new_status not in ("approved", "rejected"):
        return jsonify({
            "error": "Status must be approved or rejected."
        }), 400

    try:
        with get_db_connection() as conn:
            claim = conn.execute(
                """
                SELECT
                    c.id,
                    c.item_id,
                    c.user_id,
                    c.status,
                    i.user_id AS item_owner_id,
                    i.item_name,
                    i.status AS item_status
                FROM claims c
                JOIN items i ON i.id = c.item_id
                WHERE c.id = ?
                """,
                (claim_id,)
            ).fetchone()

            if claim is None:
                return jsonify({"error": "Claim not found."}), 404

            if claim["status"] != "pending":
                return jsonify({
                    "error": "This claim has already been reviewed."
                }), 409

            if new_status == "approved" and claim["item_status"] != "active":
                return jsonify({
                    "error": "This item is no longer available."
                }), 409

            conn.execute(
                "UPDATE claims SET status = ? WHERE id = ?",
                (new_status, claim_id)
            )

            if new_status == "approved":
                conn.execute(
                    "UPDATE items SET status = 'recovered' WHERE id = ?",
                    (claim["item_id"],)
                )

                conn.execute(
                    """
                    INSERT INTO recovery_history
                    (item_id, claimant_id, admin_id)
                    VALUES (?, ?, ?)
                    """,
                    (claim["item_id"], claim["user_id"], admin_id)
                )

                other_claims = conn.execute(
                    """
                    SELECT id, user_id FROM claims
                    WHERE item_id = ? AND id != ? AND status = 'pending'
                    """,
                    (claim["item_id"], claim_id)
                ).fetchall()

                for other in other_claims:
                    conn.execute(
                        "UPDATE claims SET status = 'rejected' WHERE id = ?",
                        (other["id"],)
                    )

                    conn.execute(
                        """
                        INSERT INTO notifications (user_id, message)
                        VALUES (?, ?)
                        """,
                        (
                            other["user_id"],
                            "Your claim was closed because another claim was approved."
                        )
                    )

                conn.execute(
                    """
                    INSERT INTO notifications (user_id, message)
                    VALUES (?, ?)
                    """,
                    (
                        claim["user_id"],
                        f"Your claim for {claim['item_name']} has been approved."
                    )
                )

                conn.execute(
                    """
                    INSERT INTO notifications (user_id, message)
                    VALUES (?, ?)
                    """,
                    (
                        claim["item_owner_id"],
                        f"The claim for your item {claim['item_name']} has been approved."
                    )
                )

            else:
                conn.execute(
                    """
                    INSERT INTO notifications (user_id, message)
                    VALUES (?, ?)
                    """,
                    (
                        claim["user_id"],
                        f"Your claim for {claim['item_name']} has been rejected."
                    )
                )

        return jsonify({
            "message": f"Claim {new_status} successfully.",
            "claim_id": claim_id,
            "status": new_status
        }), 200

    except Exception as error:
        print("Claim review error:", error)
        return jsonify({"error": "Could not review claim."}), 500


# =====================================
# NOTIFICATIONS
# =====================================

@workflow.route("/notifications", methods=["GET"])
@login_required
def get_notifications():
    user_id = session.get("user_id")

    try:
        with get_db_connection() as conn:
            rows = conn.execute(
                """
                SELECT id, message, is_read, created_at
                FROM notifications
                WHERE user_id = ?
                ORDER BY created_at DESC
                """,
                (user_id,)
            ).fetchall()

        notifications = [dict(row) for row in rows]

        return jsonify({
            "notifications": notifications,
            "unread_count": sum(
                1 for notification in notifications
                if not notification["is_read"]
            )
        }), 200

    except Exception as error:
        print("Get notifications error:", error)
        return jsonify({"error": "Could not retrieve notifications."}), 500


@workflow.route("/notifications/<int:notification_id>/read", methods=["PUT"])
@login_required
def mark_notification_read(notification_id):
    user_id = session.get("user_id")

    try:
        with get_db_connection() as conn:
            cursor = conn.execute(
                """
                UPDATE notifications
                SET is_read = 1
                WHERE id = ? AND user_id = ?
                """,
                (notification_id, user_id)
            )

            if cursor.rowcount == 0:
                return jsonify({
                    "error": "Notification not found."
                }), 404

        return jsonify({
            "message": "Notification marked as read."
        }), 200

    except Exception as error:
        print("Mark notification error:", error)
        return jsonify({"error": "Could not update notification."}), 500


# =====================================
# RECOVERY HISTORY
# =====================================

@workflow.route("/recovery-history", methods=["GET"])
@login_required
def get_recovery_history():
    user_id = session.get("user_id")

    try:
        with get_db_connection() as conn:
            user = conn.execute(
                "SELECT role FROM users WHERE id = ?",
                (user_id,)
            ).fetchone()

            if user is None:
                return jsonify({"error": "User not found."}), 404

            if user["role"] == "admin":
                rows = conn.execute(
                    """
                    SELECT
                        r.id,
                        r.item_id,
                        r.claimant_id,
                        r.admin_id,
                        r.recovered_at,
                        i.item_name
                    FROM recovery_history r
                    JOIN items i ON i.id = r.item_id
                    ORDER BY r.recovered_at DESC
                    """
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT
                        r.id,
                        r.item_id,
                        r.claimant_id,
                        r.admin_id,
                        r.recovered_at,
                        i.item_name
                    FROM recovery_history r
                    JOIN items i ON i.id = r.item_id
                    WHERE r.claimant_id = ? OR i.user_id = ?
                    ORDER BY r.recovered_at DESC
                    """,
                    (user_id, user_id)
                ).fetchall()

        return jsonify({
            "recovery_history": [dict(row) for row in rows]
        }), 200

    except Exception as error:
        print("Recovery history error:", error)
        return jsonify({
            "error": "Could not retrieve recovery history."
        }), 500