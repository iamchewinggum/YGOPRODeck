CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    profile_image_url TEXT
);

CREATE TABLE cards (
    card_id SERIAL PRIMARY KEY,
    ygoprodeck_id INTEGER NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    card_type VARCHAR(100),
    description TEXT,
    atk INTEGER NULL,
    defense INTEGER NULL,
    level INTEGER NULL,
    race VARCHAR(100) NULL,
    attribute VARCHAR(100) NULL,
    image_url TEXT
);

CREATE TABLE wishlist(
    wishlist_id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE decks(
    deck_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    deck_name VARCHAR(100) NOT NULL
);

CREATE TABLE wishlist_card(
    wishlist_id INTEGER REFERENCES wishlist(wishlist_id) ON DELETE CASCADE,
    card_id INTEGER REFERENCES cards(card_id) ON DELETE CASCADE,
    PRIMARY KEY (wishlist_id, card_id)
);

CREATE TABLE deck_card(
    deck_id INTEGER REFERENCES decks(deck_id) ON DELETE CASCADE,
    card_id INTEGER REFERENCES cards(card_id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (deck_id, card_id)
);