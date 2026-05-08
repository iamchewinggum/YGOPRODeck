from flask import Blueprint, send_from_directory
import os

pages_bp = Blueprint("pages", __name__)

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "Frontend")

@pages_bp.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "login.html")

@pages_bp.route("/profile")
def profile_page():
    return send_from_directory(FRONTEND_DIR, "profile.html")

@pages_bp.route("/users")
def users_page():
    return send_from_directory(FRONTEND_DIR, "users.html")