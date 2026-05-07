class User:
    def __init__(self, user_id, google_id, username, email, profile_image_url=None):
        self.user_id = user_id
        self.google_id = google_id
        self.username = username
        self.email = email
        self.profile_image_url = profile_image_url
      
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'google_id': self.google_id,
            'username': self.username,
            'email': self.email,
            'profile_image_url': self.profile_image_url,
        }
    
