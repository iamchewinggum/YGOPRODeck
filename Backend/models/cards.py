class Card:
    def __init__(self, ygoprodeck_id,name,card_type,description,atk = none, defense = none, level = none, race = none, attribute = none, image_url = none):
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