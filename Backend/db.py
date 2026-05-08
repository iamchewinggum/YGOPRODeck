import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import g


load_dotenv()

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:YOUR_PASSWORD@localhost:5432/yugioh_deck",
)


def get_db():
    """Get a database connection for the current request."""
    if "db" not in g:
        g.db = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return g.db


def close_db(e=None):
    """Close the database connection at end of request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create tables if they don't exist."""
    from flask import current_app
    current_app.teardown_appcontext(close_db)

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(SCHEMA_SQL)
    conn.commit()
    cur.close()
    conn.close()


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    user_id     SERIAL PRIMARY KEY,
    username    VARCHAR(80) UNIQUE NOT NULL,
    email       VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    profile_image TEXT,
    is_public   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cards (
    card_id         SERIAL PRIMARY KEY,
    ygoprodeck_id   INTEGER UNIQUE,
    name            VARCHAR(255) NOT NULL,
    card_type       VARCHAR(100) NOT NULL,
    description     TEXT,
    atk             INTEGER,
    defense         INTEGER,
    level           INTEGER,
    race            VARCHAR(100),
    attribute       VARCHAR(50),
    image_url       TEXT
);

CREATE TABLE IF NOT EXISTS collection (
    entry_id    SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    card_id     INTEGER NOT NULL REFERENCES cards(card_id) ON DELETE CASCADE,
    quantity    INTEGER NOT NULL DEFAULT 1,
    condition   VARCHAR(20) DEFAULT 'near_mint',
    added_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, card_id)
);

CREATE TABLE IF NOT EXISTS decks (
    deck_id     SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    deck_name   VARCHAR(120) NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS deck_cards (
    deck_id     INTEGER NOT NULL REFERENCES decks(deck_id) ON DELETE CASCADE,
    card_id     INTEGER NOT NULL REFERENCES cards(card_id) ON DELETE CASCADE,
    quantity    INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (deck_id, card_id)
);
"""