
from flask import Blueprint, request, jsonify, session, current_app
import sqlite3

member4 = Blueprint("member4", __name__)


def get_db():
    db = sqlite3.connect(current_app.config["DATABASE"])
    db.row_factory = sqlite3.Row
    return db


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
    details = data.get("identifying_details", "").strip()

    if not item_id or not details:
        return jsonify({"error": "Required fields missing"}), 400

    if len(details) < 10:
        return jsonify({"error": "Provide more details"}), 400

    db = get_db()

    try:
        item = db.execute(
            "SELECT id FROM items WHERE id = ?",
            (item_id,)
        ).fetchone()

        if not item:
            return jsonify({"error": "Item not found"}), 404

        result = db.execute("""
            INSERT INTO claims
            (item_id, user_id, identifying_details)
            VALUES (?, ?, ?)
        """, (item_id, session["user_id"], details))

        db.commit()

        return jsonify({
            "message": "Claim submitted successfully",
            "claim_id": result.lastrowid,
            "status": "Pending"
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
        claims = db.execute(
            "SELECT * FROM claims ORDER BY created_at DESC"
        ).fetchall()

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

    status = data.get("status")
    remarks = data.get("remarks", "")

    if status not in ["Approved", "Rejected"]:
        return jsonify({"error": "Invalid status"}), 400

    db = get_db()

    try:
        claim = db.execute(
            "SELECT * FROM claims WHERE id = ?",
            (claim_id,)
        ).fetchone()

        if not claim:
            return jsonify({"error": "Claim not found"}), 404

        if claim["status"] != "Pending":
            return jsonify({"error": "Claim already reviewed"}), 409

        db.execute("""
            UPDATE claims
            SET status = ?, admin_remarks = ?
            WHERE id = ?
        """, (status, remarks, claim_id))

        message = f"Your claim has been {status.lower()}."

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

        return jsonify({"message": "Notification marked as read"})

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

        if claim["status"] != "Approved":
            return jsonify({
                "error": "Claim must be approved first"
            }), 400

        db.execute("""
            INSERT INTO recovery_history
            (item_id, claimant_id, admin_id, recovery_status)
            VALUES (?, ?, ?, 'Recovered')
        """, (
            claim["item_id"],
            claim["user_id"],
            session["user_id"]
        ))

        db.execute("""
            UPDATE items
            SET status = 'Recovered'
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

        return jsonify({"message": "Item recovered successfully"})

    finally:
        db.close()
