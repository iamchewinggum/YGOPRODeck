from flask import Blueprint, render_template

pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/")
def index():
    return render_template("index.html")


@pages_bp.route("/login")
def login_page():
    return render_template("login.html")


@pages_bp.route("/register")
def register_page():
    return render_template("register.html")


@pages_bp.route("/search")
def search_page():
    return render_template("search.html")


@pages_bp.route("/collection")
def collection_page():
    return render_template("collection.html")


@pages_bp.route("/wishlist")
def wishlist_page():
    return render_template("wishlist.html")


@pages_bp.route("/dashboard")
def dashboard_page():
    return render_template("dashboard.html")


@pages_bp.route("/user/<int:user_id>")
def public_profile_page(user_id):
    return render_template("public_profile.html", user_id=user_id)