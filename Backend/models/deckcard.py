class Deckcard:
    def __init__(self, deck_id, card_id, quantity):
        self.deck_id = deck_id
        self.card_id = card_id
        self.quantity = quantity

    def to_dict(self):
        return {
            'deck_id': self.deck_id,
            'card_id': self.card_id,
            'quantity': self.quantity
        }