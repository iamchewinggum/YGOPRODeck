from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not username or not email or not password:
        return jsonify({"error": "Username, email, and password are required"}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    db = get_db()
    cur = db.cursor()

    # Check if username or email already exists
    cur.execute(
        "SELECT user_id FROM users WHERE username = %s OR email = %s",
        (username, email),
    )
    if cur.fetchone():
        return jsonify({"error": "Username or email already taken"}), 409

    password_hash = generate_password_hash(password)
    cur.execute(
        "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s) RETURNING user_id",
        (username, email, password_hash),
    )
    user = cur.fetchone()
    db.commit()

    session["user_id"] = user["user_id"]
    return jsonify({"message": "Registered successfully", "user_id": user["user_id"]}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cur.fetchone()

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid credentials"}), 401

    session["user_id"] = user["user_id"]
    return jsonify({
        "message": "Logged in",
        "user_id": user["user_id"],
        "username": user["username"],
    })


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})


@auth_bp.route("/me", methods=["GET"])
def me():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT user_id, username, email, profile_image, created_at FROM users WHERE user_id = %s",
        (user_id,),
    )
    user = cur.fetchone()
    if not user:
        session.clear()
        return jsonify({"error": "User not found"}), 404

    return jsonify(dict(user))