from functools import wraps
from flask import session, jsonify

from database.db import get_db_connection


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        user_id = session.get("user_id")

        if not user_id:
            return jsonify({
                "error": "Authentication required. Please log in."
            }), 401

        try:
            with get_db_connection() as conn:
                user = conn.execute(
                    "SELECT id FROM users WHERE id = ?",
                    (user_id,)
                ).fetchone()

            if user is None:
                session.clear()
                return jsonify({
                    "error": "User account not found."
                }), 401

        except Exception:
            return jsonify({
                "error": "Authentication check failed."
            }), 500

        return func(*args, **kwargs)

    return wrapper


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        user_id = session.get("user_id")

        if not user_id:
            return jsonify({
                "error": "Authentication required. Please log in."
            }), 401

        try:
            with get_db_connection() as conn:
                user = conn.execute(
                    "SELECT role FROM users WHERE id = ?",
                    (user_id,)
                ).fetchone()

            if user is None:
                session.clear()
                return jsonify({
                    "error": "User account not found."
                }), 401

            if user["role"] != "admin":
                return jsonify({
                    "error": "Access denied. Admin privileges required."
                }), 403

        except Exception:
            return jsonify({
                "error": "Authorization check failed."
            }), 500

        return func(*args, **kwargs)

    return wrapper