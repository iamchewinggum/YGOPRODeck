from flask import Blueprint, request, jsonify, session
from db import get_db
from routes.cards import ensure_card_in_db

collection_bp = Blueprint("collection", __name__, url_prefix="/api/collection")


def require_login():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return user_id


@collection_bp.route("", methods=["GET"])
def get_collection():
    user_id = require_login()
    if not user_id:
        return jsonify({"error": "Login required"}), 401

    db = get_db()
    cur = db.cursor()
    cur.execute(
        """SELECT c.entry_id, c.quantity, c.condition, c.added_at,
                  k.card_id, k.name, k.card_type, k.atk, k.defense, k.level,
                  k.race, k.attribute, k.image_url, k.ygoprodeck_id
           FROM collection c
           JOIN cards k ON c.card_id = k.card_id
           WHERE c.user_id = %s
           ORDER BY c.added_at DESC""",
        (user_id,),
    )
    entries = [dict(row) for row in cur.fetchall()]
    return jsonify({"collection": entries})


@collection_bp.route("", methods=["POST"])
def add_to_collection():
    user_id = require_login()
    if not user_id:
        return jsonify({"error": "Login required"}), 401

    data = request.get_json()
    if not data.get("ygoprodeck_id") or not data.get("name"):
        return jsonify({"error": "Card data is required"}), 400

    card_id = ensure_card_in_db(data)
    quantity = data.get("quantity", 1)
    condition = data.get("condition", "near_mint")

    db = get_db()
    cur = db.cursor()

    # Upsert: if card already in collection, update quantity
    cur.execute(
        """INSERT INTO collection (user_id, card_id, quantity, condition)
           VALUES (%s, %s, %s, %s)
           ON CONFLICT (user_id, card_id)
           DO UPDATE SET quantity = collection.quantity + EXCLUDED.quantity
           RETURNING entry_id""",
        (user_id, card_id, quantity, condition),
    )
    entry = cur.fetchone()
    db.commit()

    return jsonify({"message": "Card added to collection", "entry_id": entry["entry_id"]}), 201


@collection_bp.route("/<int:entry_id>", methods=["PUT"])
def update_collection_entry(entry_id):
    user_id = require_login()
    if not user_id:
        return jsonify({"error": "Login required"}), 401

    data = request.get_json()
    quantity = data.get("quantity")
    condition = data.get("condition")

    if quantity is None and condition is None:
        return jsonify({"error": "Provide quantity or condition to update"}), 400

    db = get_db()
    cur = db.cursor()

    # Verify ownership
    cur.execute("SELECT entry_id FROM collection WHERE entry_id = %s AND user_id = %s", (entry_id, user_id))
    if not cur.fetchone():
        return jsonify({"error": "Entry not found"}), 404

    updates = []
    values = []
    if quantity is not None:
        updates.append("quantity = %s")
        values.append(quantity)
    if condition is not None:
        updates.append("condition = %s")
        values.append(condition)

    values.extend([entry_id, user_id])
    cur.execute(
        f"UPDATE collection SET {', '.join(updates)} WHERE entry_id = %s AND user_id = %s",
        values,
    )
    db.commit()

    return jsonify({"message": "Updated"})


@collection_bp.route("/<int:entry_id>", methods=["DELETE"])
def delete_collection_entry(entry_id):
    user_id = require_login()
    if not user_id:
        return jsonify({"error": "Login required"}), 401

    db = get_db()
    cur = db.cursor()
    cur.execute(
        "DELETE FROM collection WHERE entry_id = %s AND user_id = %s RETURNING entry_id",
        (entry_id, user_id),
    )
    deleted = cur.fetchone()
    db.commit()

    if not deleted:
        return jsonify({"error": "Entry not found"}), 404

    return jsonify({"message": "Deleted"})