class Card:
    def __init__(self, card_id, ygoprodeck_id, name, card_type, description, atk=None, defense=None, level=None, race=None, attribute=None, image_url=None):
        self.card_id = card_id
        self.ygoprodeck_id = ygoprodeck_id
        self.name = name
        self.card_type = card_type
        self.description = description
        self.atk = atk
        self.defense = defense
        self.level = level
        self.race = race
        self.attribute = attribute  
        self.image_url = image_url

    def to_dict(self):
        return {
            "card_id": self.card_id,
            "ygoprodeck_id": self.ygoprodeck_id,
            "name": self.name,
            "card_type": self.card_type,
            "description": self.description,
            "atk": self.atk,
            "defense": self.defense,
            "level": self.level,
            "race": self.race,
            "attribute": self.attribute,
            "image_url": self.image_url
        }
    