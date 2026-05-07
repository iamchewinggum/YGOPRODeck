from flask import Blueprint, request, jsonify
from config.db import get_db_connection
cards_bp = Blueprint('cards', __name__)


@cards_bp.route('/', methods=['POST'])
def create_card():
    data = request.get_json()
    
    ygoprodeck_id = data.get('ygoprodeck_id')
    name = data.get('name')
    card_type = data.get('card_type')
    description = data.get('description')
    atk = data.get('atk')
    defense = data.get('defense')
    level = data.get('level')
    race = data.get('race')
    attribute = data.get('attribute')
    image_url = data.get('image_url')

    if not ygoprodeck_id or not name:
        return jsonify({"error": "Missing required fields"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""INSERT INTO cards (ygoprodeck_id, name, card_type, description, atk, defense, level, race, attribute, image_url)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING card_id""",
                       (ygoprodeck_id, name, card_type, description, atk, defense, level, race, attribute, image_url))

    card_id = cursor.fetchone()[0]
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "Card created successfully", "card_id": card_id, "ygoprodeck_id": ygoprodeck_id, "name": name}), 201



