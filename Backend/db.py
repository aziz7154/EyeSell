import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

def init_db():
    """Create users table if it doesn't exist."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def find_user_by_username(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, password_hash FROM users WHERE username = %s", (username,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row  

def create_user(username, email, password_hash):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s) RETURNING id",
        (username, email, password_hash)
    )
    user_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return user_id

def find_user_by_email(email):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, email FROM users WHERE email = %s", (email,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

def create_oauth_user(username, email):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s) RETURNING id",
        (username, email, "OAUTH")  # placeholder since no password is needed with OAuth
    )
    user_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return user_id

def init_listings_table():
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS listings (
            id           SERIAL PRIMARY KEY,
            user_id      INTEGER REFERENCES users(id) ON DELETE CASCADE,
            image_id     TEXT,
            product_name TEXT    NOT NULL,
            description  TEXT    DEFAULT '',
            tags         TEXT    DEFAULT '',
            price_low    FLOAT   DEFAULT 0,
            price_high   FLOAT   DEFAULT 0,
            price_final  FLOAT   DEFAULT 0,
            status       VARCHAR(20) DEFAULT 'saved',
            created_at   TIMESTAMP   DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def create_listing(user_id, image_id, product_name, description, tags, price_low, price_high, price_final):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(
        """
        INSERT INTO listings
            (user_id, image_id, product_name, description, tags, price_low, price_high, price_final)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (user_id, image_id, product_name, description, tags, price_low, price_high, price_final)
    )
    listing_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return listing_id

def get_listings_by_user(user_id):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(
        """
        SELECT id, image_id, product_name, description, tags,
               price_low, price_high, price_final, status, created_at
        FROM listings
        WHERE user_id = %s
        ORDER BY created_at DESC
        """,
        (user_id,)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {
            "id":           row[0],
            "image_id":     row[1],
            "product_name": row[2],
            "description":  row[3],
            "tags":         row[4],
            "price_low":    row[5],
            "price_high":   row[6],
            "price_final":  row[7],
            "status":       row[8],
            "created_at":   row[9].isoformat() if row[9] else "",
        }
        for row in rows
    ]