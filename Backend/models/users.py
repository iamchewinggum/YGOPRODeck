class User:
    def __init__(self, id, username, email, password_hash, profile_image_url=None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.profile_image_url = profile_image_url
      