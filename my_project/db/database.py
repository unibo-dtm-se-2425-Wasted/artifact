import sqlite3
import os
import hashlib

# ------------------- DATABASE PATH -------------------
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "food_items.db")

# ------------------- DATABASE CONNECTION -------------------
def create_connection():
    """Create a connection to the SQLite database."""
    conn = sqlite3.connect(db_path)
    return conn

# ------------------- INITIALIZE DATABASE -------------------
def initialize_db():
    """Create tables if they do not exist yet."""
    conn = create_connection()
    c = conn.cursor()

    # Food items table
    c.execute('''
    CREATE TABLE IF NOT EXISTS food_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT NOT NULL,
        name TEXT NOT NULL,
        category TEXT,
        purchase_date TEXT,
        expiration_date TEXT,
        quantity REAL,
        unit TEXT,
        price_per_unit REAL  -- NEW
    )
    ''')

    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

# ------------------- CRUD FOOD ITEMS -------------------
def insert_food_item(user, name, category, purchase_date, expiration_date, quantity, unit, price_per_unit):
    conn = create_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO food_items 
        (user, name, category, purchase_date, expiration_date, quantity, unit, price_per_unit)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user, name, category, purchase_date, expiration_date, quantity, unit, price_per_unit))
    conn.commit()
    conn.close()

def get_all_food_items(user):
    """Retrieve all food items for a given user."""
    conn = create_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM food_items WHERE user = ?", (user,))
    rows = c.fetchall()
    conn.close()
    return rows

def delete_food_item(item_id, user):
    """Delete a specific food item for a user."""
    conn = create_connection()
    c = conn.cursor()
    c.execute("DELETE FROM food_items WHERE id = ? AND user = ?", (item_id, user))
    conn.commit()
    conn.close()

# ------------------- USER MANAGEMENT -------------------
def add_user(username, password):
    """Add a new user with a hashed password."""
    conn = create_connection()
    c = conn.cursor()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    try:
        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Username already exists
    conn.close()

def check_user_credentials(username, password):
    """Check if the provided username and password are correct."""
    conn = create_connection()
    c = conn.cursor()
    c.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    if row:
        return row[0] == hashlib.sha256(password.encode()).hexdigest()
    return False