
from flask import Blueprint, request, jsonify, session
from database.db import get_db_connection

member4 = Blueprint("member4", __name__)


def get_db():
    return get_db_connection()


def login_required():
    return bool(session.get("user_id"))


def admin_required():
    return login_required() and session.get("role") == "admin"


# 1. Submit a claim
@member4.route("/submit-claim", methods=["POST"])
def submit_claim():

    if not login_required():
        return jsonify({"error": "Please login first"}), 401

    data = request.get_json(silent=True) or {}

    item_id = data.get("item_id")
    details = data.get("claim_description", "").strip()

    if not item_id or not details:
        return jsonify({"error": "Required fields missing"}), 400

    if len(details) < 10:
        return jsonify({"error": "Provide more details"}), 400

    db = get_db()

    try:
        item = db.execute(
            "SELECT id, user_id, status FROM items WHERE id = ?",
            (item_id,)
        ).fetchone()

        if not item:
            return jsonify({"error": "Item not found"}), 404

        if item["user_id"] == session["user_id"]:
            return jsonify({"error": "You cannot claim your own item"}), 400

        if item["status"].lower() != "active":
            return jsonify({"error": "Item is not available"}), 400

        result = db.execute("""
            INSERT INTO claims
            (item_id, user_id, claim_description)
            VALUES (?, ?, ?)
        """, (item_id, session["user_id"], details))

        db.commit()

        return jsonify({
            "message": "Claim submitted successfully",
            "claim_id": result.lastrowid,
            "status": "pending"
        }), 201

    finally:
        db.close()


# 2. Admin view all claims
@member4.route("/admin/claims", methods=["GET"])
def view_claims():

    if not admin_required():
        return jsonify({"error": "Admin access required"}), 403

    db = get_db()

    try:
        claims = db.execute("""
            SELECT claims.*, users.name, items.item_name
            FROM claims
            JOIN users ON claims.user_id = users.id
            JOIN items ON claims.item_id = items.id
            ORDER BY claims.created_at DESC
        """).fetchall()

        return jsonify([dict(c) for c in claims])

    finally:
        db.close()


# 3. Admin approve or reject claim
@member4.route(
    "/admin/update-claim/<int:claim_id>",
    methods=["POST"]
)
def update_claim(claim_id):

    if not admin_required():
        return jsonify({"error": "Admin access required"}), 403

    data = request.get_json(silent=True) or {}

    status = data.get("status", "").lower()

    if status not in ["approved", "rejected"]:
        return jsonify({"error": "Invalid status"}), 400

    db = get_db()

    try:
        claim = db.execute(
            "SELECT * FROM claims WHERE id = ?",
            (claim_id,)
        ).fetchone()

        if not claim:
            return jsonify({"error": "Claim not found"}), 404

        if claim["status"].lower() != "pending":
            return jsonify({"error": "Claim already reviewed"}), 409

        if status == "approved":

            item = db.execute(
                "SELECT status FROM items WHERE id = ?",
                (claim["item_id"],)
            ).fetchone()

            if not item or item["status"].lower() != "active":
                return jsonify({"error": "Item is not available"}), 409

            other_approved = db.execute("""
                SELECT id FROM claims
                WHERE item_id = ?
                AND status = 'approved'
                AND id != ?
            """, (claim["item_id"], claim_id)).fetchone()

            if other_approved:
                return jsonify({
                    "error": "Another claim is already approved"
                }), 409

        db.execute("""
            UPDATE claims
            SET status = ?
            WHERE id = ?
        """, (status, claim_id))

        message = f"Your claim has been {status}."

        db.execute("""
            INSERT INTO notifications (user_id, message)
            VALUES (?, ?)
        """, (claim["user_id"], message))

        db.commit()

        return jsonify({
            "message": message,
            "status": status
        })

    finally:
        db.close()


# 4. View notifications
@member4.route("/notifications", methods=["GET"])
def get_notifications():

    if not login_required():
        return jsonify({"error": "Please login first"}), 401

    db = get_db()

    try:
        notifications = db.execute("""
            SELECT * FROM notifications
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (session["user_id"],)).fetchall()

        return jsonify([dict(n) for n in notifications])

    finally:
        db.close()


# 5. Mark notification as read
@member4.route(
    "/notifications/read/<int:notification_id>",
    methods=["POST"]
)
def mark_notification_read(notification_id):

    if not login_required():
        return jsonify({"error": "Please login first"}), 401

    db = get_db()

    try:
        result = db.execute("""
            UPDATE notifications
            SET is_read = 1
            WHERE id = ? AND user_id = ?
        """, (notification_id, session["user_id"]))

        db.commit()

        if result.rowcount == 0:
            return jsonify({"error": "Notification not found"}), 404

        return jsonify({
            "message": "Notification marked as read"
        })

    finally:
        db.close()


# 6. Complete item recovery
@member4.route(
    "/admin/complete-recovery/<int:claim_id>",
    methods=["POST"]
)
def complete_recovery(claim_id):

    if not admin_required():
        return jsonify({"error": "Admin access required"}), 403

    db = get_db()

    try:
        claim = db.execute(
            "SELECT * FROM claims WHERE id = ?",
            (claim_id,)
        ).fetchone()

        if not claim:
            return jsonify({"error": "Claim not found"}), 404

        if claim["status"].lower() != "approved":
            return jsonify({
                "error": "Claim must be approved first"
            }), 400

        item = db.execute(
            "SELECT status FROM items WHERE id = ?",
            (claim["item_id"],)
        ).fetchone()

        if not item or item["status"].lower() == "recovered":
            return jsonify({"error": "Item already recovered"}), 409

        db.execute("""
            INSERT INTO recovery_history
            (item_id, claimant_id, admin_id)
            VALUES (?, ?, ?)
        """, (
            claim["item_id"],
            claim["user_id"],
            session["user_id"]
        ))

        db.execute("""
            UPDATE items
            SET status = 'recovered'
            WHERE id = ?
        """, (claim["item_id"],))

        db.execute("""
            INSERT INTO notifications (user_id, message)
            VALUES (?, ?)
        """, (
            claim["user_id"],
            "Your item has been successfully recovered."
        ))

        db.commit()

        return jsonify({
            "message": "Item recovered successfully"
        })

    finally:
        db.close()
