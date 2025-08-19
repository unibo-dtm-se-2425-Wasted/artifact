import sqlite3
import os
import hashlib

# ---------------------- PATH DB ----------------------
def create_connection():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    db_path = os.path.join(data_dir, "food_items.db")
    conn = sqlite3.connect(db_path)
    return conn

# ---------------------- INIT DB ----------------------
def initialize_db():
    conn = create_connection()
    c = conn.cursor()

    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')

    # Food items table
    c.execute('''
        CREATE TABLE IF NOT EXISTS food_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            category TEXT,
            purchase_date TEXT,
            expiration_date TEXT,
            quantity REAL,
            unit TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # Create test user if not exists
    test_username = "prova"
    test_password = "1234"
    c.execute("SELECT * FROM users WHERE username = ?", (test_username,))
    if not c.fetchone():
        password_hash = hashlib.sha256(test_password.encode()).hexdigest()
        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                  (test_username, password_hash))

    conn.commit()
    conn.close()

# ---------------------- USER FUNCTIONS ----------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    conn = create_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                  (username, hash_password(password)))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return False
    conn.close()
    return True

def login_user(username, password):
    conn = create_connection()
    c = conn.cursor()
    c.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    if row and row[1] == hash_password(password):
        return row[0]  # user_id
    return None

# ---------------------- FOOD ITEM FUNCTIONS ----------------------
def insert_food_item(user_id, name, category, purchase_date, expiration_date, quantity, unit):
    conn = create_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO food_items (user_id, name, category, purchase_date, expiration_date, quantity, unit)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, name, category, purchase_date, expiration_date, quantity, unit))
    conn.commit()
    conn.close()

def get_all_food_items(user_id):
    conn = create_connection()
    c = conn.cursor()
    c.execute("""
        SELECT id, name, category, purchase_date, expiration_date, quantity, unit
        FROM food_items WHERE user_id = ?
    """, (user_id,))
    rows = c.fetchall()
    conn.close()

    items = []
    for row in rows:
        items.append({
            "ID": row[0],
            "Name": row[1],
            "Category": row[2],
            "Purchase Date": row[3],
            "Expiration Date": row[4],
            "Quantity": row[5],
            "Unit": row[6]
        })
    return items

def delete_food_item(user_id, item_id):
    conn = create_connection()
    c = conn.cursor()
    c.execute("DELETE FROM food_items WHERE user_id = ? AND id = ?", (user_id, item_id))
    conn.commit()
    conn.close()
