from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
import re
import sqlite3

from database.db import get_db_connection


auth = Blueprint("auth", __name__, url_prefix="/api/auth")


# =====================================
# 1. USER REGISTRATION
# =====================================

@auth.route("/register", methods=["POST"])
def register():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid request data"}), 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not all(isinstance(value, str) for value in [name, email, password]):
        return jsonify({"error": "All fields are required"}), 400

    name = name.strip()
    email = email.strip().lower()

    if not name or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    if len(name) > 100:
        return jsonify({"error": "Name is too long"}), 400

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return jsonify({"error": "Invalid email address"}), 400

    if len(password) < 8:
        return jsonify({
            "error": "Password must contain at least 8 characters"
        }), 400

    password_hash = generate_password_hash(password)

    try:
        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO users (name, email, password_hash)
                VALUES (?, ?, ?)
                """,
                (name, email, password_hash)
            )

        return jsonify({
            "message": "User registered successfully!"
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "Email already registered"
        }), 409

    except sqlite3.Error:
        return jsonify({
            "error": "Registration failed"
        }), 500


# =====================================
# 2. USER LOGIN
# =====================================

@auth.route("/login", methods=["POST"])
def login():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid request data"}), 400

    email = data.get("email")
    password = data.get("password")

    if not isinstance(email, str) or not isinstance(password, str):
        return jsonify({
            "error": "Email and password are required"
        }), 400

    email = email.strip().lower()

    if not email or not password:
        return jsonify({
            "error": "Email and password are required"
        }), 400

    try:
        with get_db_connection() as conn:
            user = conn.execute(
                """
                SELECT id, name, email, password_hash, role
                FROM users
                WHERE email = ?
                """,
                (email,)
            ).fetchone()

        if user is None or not check_password_hash(
            user["password_hash"], password
        ):
            return jsonify({
                "error": "Invalid email or password"
            }), 401

        session.clear()
        session.permanent = True
        session["user_id"] = user["id"]
        session["role"] = user["role"]

        return jsonify({
            "message": "Login successful!",
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"]
            }
        }), 200

    except sqlite3.Error:
        return jsonify({
            "error": "Login failed"
        }), 500


# =====================================
# 3. USER LOGOUT
# =====================================

@auth.route("/logout", methods=["POST"])
def logout():

    if "user_id" not in session:
        return jsonify({
            "error": "You are not logged in"
        }), 401

    session.clear()

    return jsonify({
        "message": "Logout successful!"
    }), 200


# =====================================
# 4. CHECK CURRENT USER SESSION
# =====================================

@auth.route("/me", methods=["GET"])
def get_current_user():

    if "user_id" not in session:
        return jsonify({
            "error": "Authentication required"
        }), 401

    try:
        with get_db_connection() as conn:
            user = conn.execute(
                """
                SELECT id, name, email, role
                FROM users
                WHERE id = ?
                """,
                (session["user_id"],)
            ).fetchone()

        if user is None:
            session.clear()
            return jsonify({
                "error": "User not found"
            }), 404

        return jsonify({
            "logged_in": True,
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"]
            }
        }), 200

    except sqlite3.Error:
        return jsonify({
            "error": "Could not retrieve user"
        }), 500