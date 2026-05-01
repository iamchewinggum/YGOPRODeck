class wishlistcard:
    def __init__(self, wishlist_id, card_id):
        self.wishlist_id = wishlist_id
        self.card_id = card_id
    
    def to_dict(self):
        return {
            'wishlist_id': self.wishlist_id,
            'card_id': self.card_id
        }