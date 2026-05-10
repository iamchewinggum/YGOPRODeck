import os
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from db import init_db, get_db
from Backend.routes.auth import auth_bp
from Backend.routes.collection import collection_bp
from Backend.routes.cards import cards_bp
from Backend.routes.public import public_bp
from Backend.routes.profile import profile_bp
from Backend.routes.pages import pages_bp
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    # --- Rate Limiter ---
    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://",
    )

    # Apply stricter limits to mutation endpoints
    limiter.limit("30 per minute")(auth_bp)
    limiter.limit("30 per minute")(collection_bp)

    # --- Register API Blueprints ---
    app.register_blueprint(auth_bp)
    app.register_blueprint(collection_bp)
    app.register_blueprint(cards_bp)
    app.register_blueprint(public_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(pages_bp)

    # --- Initialize Database ---
    with app.app_context():
        init_db()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)