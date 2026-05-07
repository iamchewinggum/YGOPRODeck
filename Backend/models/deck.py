class Deck:
    def __init__(self, deck_id, user_id, deck_name):
        self.deck_id = deck_id
        self.user_id = user_id
        self.deck_name = deck_name

    def to_dict(self):
        return {
            'deck_id': self.deck_id,
            'user_id': self.user_id,
            'deck_name': self.deck_name
        }
    
