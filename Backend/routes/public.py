from flask import Blueprint, jsonify
from db import get_db

public_bp = Blueprint("public", __name__, url_prefix="/api/users")


@public_bp.route("/<int:user_id>/collection", methods=["GET"])
def get_public_collection(user_id):
    db = get_db()
    cur = db.cursor()

    # Check user exists and is public
    cur.execute("SELECT user_id, username, is_public FROM users WHERE user_id = %s", (user_id,))
    user = cur.fetchone()
    if not user:
        return jsonify({"error": "User not found"}), 404
    if not user["is_public"]:
        return jsonify({"error": "This collection is private"}), 403

    cur.execute(
        """SELECT c.quantity, c.condition,
                  k.name, k.card_type, k.atk, k.defense, k.level,
                  k.race, k.attribute, k.image_url
           FROM collection c
           JOIN cards k ON c.card_id = k.card_id
           WHERE c.user_id = %s
           ORDER BY k.name""",
        (user_id,),
    )
    entries = [dict(row) for row in cur.fetchall()]

    return jsonify({
        "username": user["username"],
        "collection": entries,
        "total_cards": sum(e["quantity"] for e in entries),
    })