import os
import requests
from flask import Blueprint, request, jsonify
from db import get_db

cards_bp = Blueprint("cards", __name__, url_prefix="/api/cards")

YGOPRODECK_URL = "https://db.ygoprodeck.com/api/v7/cardinfo.php"

# Where to store downloaded card images locally
IMAGE_DIR = os.path.join(os.path.dirname(__file__), "..", "static", "images", "cards")
os.makedirs(IMAGE_DIR, exist_ok=True)


def download_card_image(image_url, ygoprodeck_id):
    """Download a card image and save it locally. Returns the local path."""
    if not image_url:
        return None

    # Check if we already downloaded it
    filename = f"{ygoprodeck_id}.jpg"
    local_path = os.path.join(IMAGE_DIR, filename)

    if os.path.exists(local_path):
        return f"/static/images/cards/{filename}"

    try:
        resp = requests.get(image_url, timeout=15)
        resp.raise_for_status()
        with open(local_path, "wb") as f:
            f.write(resp.content)
        return f"/static/images/cards/{filename}"
    except requests.RequestException:
        # If download fails, return None — we won't hotlink
        return None


@cards_bp.route("/search", methods=["GET"])
def search_cards():
    """Search for cards — checks local DB first, then falls back to the API."""
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "Search query is required"}), 400

    # Step 1: Check local database first
    db = get_db()
    cur = db.cursor()
    cur.execute(
        """SELECT card_id, ygoprodeck_id, name, card_type, description,
                  atk, defense, level, race, attribute, image_url
           FROM cards
           WHERE LOWER(name) LIKE LOWER(%s)
           LIMIT 20""",
        (f"%{query}%",),
    )
    local_results = cur.fetchall()

    # If we have local results, return them without hitting the API
    if local_results:
        cards = []
        for card in local_results:
            cards.append({
                "ygoprodeck_id": card["ygoprodeck_id"],
                "name": card["name"],
                "card_type": card["card_type"],
                "description": card["description"],
                "atk": card["atk"],
                "defense": card["defense"],
                "level": card["level"],
                "race": card["race"],
                "attribute": card["attribute"],
                "image_url": card["image_url"],
                "image_url_small": card["image_url"],
                "from_cache": True,
            })
        return jsonify({"cards": cards, "total": len(cards)})

    # Step 2: Not in local DB — call the YGOPRODeck API
    try:
        resp = requests.get(YGOPRODECK_URL, params={"fname": query}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to fetch cards: {str(e)}"}), 502

    cards = []
    for card in data.get("data", [])[:20]:
        ygoprodeck_id = card.get("id")
        original_image_url = card.get("card_images", [{}])[0].get("image_url", "")

        # Download the image locally instead of hotlinking
        local_image = download_card_image(original_image_url, ygoprodeck_id)

        card_data = {
            "ygoprodeck_id": ygoprodeck_id,
            "name": card.get("name"),
            "card_type": card.get("type"),
            "description": card.get("desc"),
            "atk": card.get("atk"),
            "defense": card.get("def"),
            "level": card.get("level"),
            "race": card.get("race"),
            "attribute": card.get("attribute"),
            "image_url": local_image,
            "image_url_small": local_image,
        }

        # Step 3: Cache in local DB for future searches
        _save_card_to_db(card_data)

        cards.append(card_data)

    return jsonify({"cards": cards, "total": len(cards)})


def _save_card_to_db(card_data):
    """Save a card to the local database (skip if already exists)."""
    db = get_db()
    cur = db.cursor()
    cur.execute(
        """INSERT INTO cards (ygoprodeck_id, name, card_type, description,
                              atk, defense, level, race, attribute, image_url)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
           ON CONFLICT (ygoprodeck_id) DO NOTHING""",
        (
            card_data["ygoprodeck_id"],
            card_data["name"],
            card_data["card_type"],
            card_data.get("description"),
            card_data.get("atk"),
            card_data.get("defense"),
            card_data.get("level"),
            card_data.get("race"),
            card_data.get("attribute"),
            card_data.get("image_url"),
        ),
    )
    db.commit()


def ensure_card_in_db(card_data):
    """Insert a card into the local DB if it doesn't exist. Returns card_id."""
    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT card_id FROM cards WHERE ygoprodeck_id = %s", (card_data["ygoprodeck_id"],))
    existing = cur.fetchone()
    if existing:
        return existing["card_id"]

    # Download image before saving if it's still an external URL
    original_image = card_data.get("image_url", "")
    if original_image and not original_image.startswith("/static"):
        local_image = download_card_image(original_image, card_data["ygoprodeck_id"])
        card_data["image_url"] = local_image

    cur.execute(
        """INSERT INTO cards (ygoprodeck_id, name, card_type, description,
                              atk, defense, level, race, attribute, image_url)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
           RETURNING card_id""",
        (
            card_data["ygoprodeck_id"],
            card_data["name"],
            card_data["card_type"],
            card_data.get("description"),
            card_data.get("atk"),
            card_data.get("defense"),
            card_data.get("level"),
            card_data.get("race"),
            card_data.get("attribute"),
            card_data.get("image_url"),
        ),
    )
    result = cur.fetchone()
    db.commit()
    return result["card_id"]