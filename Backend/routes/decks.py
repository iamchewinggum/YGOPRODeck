from flask import Blueprint, request, jsonify
from Backend.models.cards import Card
from config.db import get_db_connection

from models.cards import Card

decks_bp = Blueprint('decks', __name__)

@decks_bp.route('/', methods=['POST'])
def create_deck():
    data = request.get_json()
    user_id = data.get('user_id')
    deck_name = data.get('deck_name')
    #validate the input data
    if not user_id or not deck_name:
        return jsonify({"error": "Missing required fields"}), 400
    
    #creating new connection to the database and cursor
    conn = get_db_connection()
    cursor = conn.cursor()

    #sql query to insert a new deck 
    cursor.execute("INSERT INTO decks (user_id, deck_name) VALUES (%s, %s) RETURNING deck_id", (user_id, deck_name))


    deck_id = cursor.fetchone()[0]
    conn.commit()

    #closing the cursor and connection
    cursor.close()
    conn.close()

    return jsonify({
        "message": "Deck created successfully",
        "deck_id": deck_id,
        "user_id": user_id,
        "deck_name": deck_name
    }), 201




















@decks_bp.route('/<int:deck_id>/cards', methods=['POST'])
def add_card_to_deck(deck_id):

    data = request.get_json()
    card_id = data.get('card_id')

    if not card_id:
        return jsonify({"error": "Missing required fields"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT deck_id FROM decks WHERE deck_id = %s", (deck_id,))
    existing_deck = cursor.fetchone()

    if not existing_deck:
        cursor.close()
        conn.close()
        return jsonify({"error": "Deck not found"}), 404


    #inserting into deck
    cursor.execute("SELECT card_id FROM cards WHERE card_id = %s", (card_id,))
    existing_card = cursor.fetchone()

    if not existing_card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404
    
    cursor.execute("SELECT * FROM deck_card WHERE deck_id = %s AND card_id = %s", (deck_id, card_id))
    existing = cursor.fetchone()

    if existing:
        cursor.close()
        conn.close()
        return jsonify({"message": "Card already in deck"}), 200

    cursor.execute("INSERT INTO deck_card (deck_id, card_id) VALUES (%s, %s)", (deck_id, card_id))


    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "Card added to deck successfully"}), 200















@decks_bp.route('<int:deck_id>/cards', methods=['GET'])
def get_cards_in_deck(deck_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT deck_id FROM decks WHERE deck_id = %s", (deck_id,))
    existing_deck = cursor.fetchone()

    if not existing_deck:
        cursor.close()
        conn.close()
        return jsonify({"error": "Deck not found"}), 404
    
    cursor.execute("""SELECT c.card_id, c.ygoprodeck_id, c.name, c.card_type, c.description, c.atk, c.defense, c.level, c.race, c.attribute, c.image_url
                      FROM cards c
                      JOIN deck_card dc ON c.card_id = dc.card_id
                      WHERE dc.deck_id = %s""", (deck_id,))
    cards = cursor.fetchall()

    cards_list = []

    for row in cards:
        card = Card(row[0], row[1], row[2], row[3], row[4], row[5],
                     row[6], row[7], row[8], row[9], row[10])

        cards_list.append(card.to_dict())

    cursor.close()
    conn.close()

    return jsonify({"deck_id": deck_id, 
                    "cards": cards_list}), 200    


















@decks_bp.route('/<int:deck_id>/cards/<int:card_id>', methods=['DELETE'])
def remove_card_from_deck(deck_id, card_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT deck_id FROM decks WHERE deck_id = %s", (deck_id,))
    existing_deck = cursor.fetchone()

    if not existing_deck:
        cursor.close()
        conn.close()
        return jsonify({"error": "Deck not found"}), 404
    
    cursor.execute("SELECT card_id FROM cards WHERE card_id = %s", (card_id,))
    existing_card = cursor.fetchone()
    if not existing_card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404

    cursor.execute(
        "SELECT * FROM deck_card WHERE deck_id = %s AND card_id = %s", (deck_id, card_id))
    existing = cursor.fetchone()

    if not existing:
        cursor.close()
        conn.close()
        return jsonify({"message": "Card not found in deck"}), 404
    
    cursor.execute(
        "DELETE FROM deck_card WHERE deck_id = %s AND card_id = %s", (deck_id, card_id))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "Card removed from deck successfully"}), 200



@decks_bp.route('/user/<int:user_id>', methods=['GET'])
def get_decks_by_user(user_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
    existing_user = cursor.fetchone()

    if not existing_user:
        cursor.close()
        conn.close()
        return jsonify({"error": "User not found"}), 404
    
    cursor.execute("SELECT deck_id, deck_name FROM decks WHERE user_id = %s", (user_id,))
    decks = cursor.fetchall()

    decks_list = []

    for deck in decks:
        decks_list.append ({
            "deck_id": deck[0],
            "user_id": deck[1],
            "deck_name": deck[2]
        })
        
    cursor.close()
    conn.close()

    return jsonify({
        "user_id": user_id, 
        "decks": decks_list}), 200