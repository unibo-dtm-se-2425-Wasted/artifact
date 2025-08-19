import sqlite3
import os
import hashlib

# ---------------------- PATH DB ----------------------
def create_connection():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)  # crea la cartella se non esiste
    db_path = os.path.join(data_dir, "food_items.db")
    conn = sqlite3.connect(db_path)
    return conn

# ---------------------- INIT DB ----------------------
def initialize_db():
    conn = create_connection()
    c = conn.cursor()

    # Creazione tabella users
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')

    # Creazione tabella food_items
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

    # Inserimento utente di prova se non esiste
    real_username = "prova"
    real_password = "1234"
    password_hash = hashlib.sha256(real_password.encode()).hexdigest()
    c.execute("SELECT id FROM users WHERE username = ?", (real_username,))
    if c.fetchone() is None:
        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                  (real_username, password_hash))
        print(f"Utente di prova creato: {real_username} / {real_password}")

    conn.commit()
    conn.close()

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
    c.execute("SELECT * FROM food_items WHERE user_id = ?", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def delete_food_item(user_id, item_id):
    conn = create_connection()
    c = conn.cursor()
    c.execute("DELETE FROM food_items WHERE user_id = ? AND id = ?", (user_id, item_id))
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
        return False  # Username già esistente
    conn.close()
    return True

def login_user(username, password):
    conn = create_connection()
    c = conn.cursor()
    c.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    if row and row[1] == hash_password(password):
        return row[0]  # ritorna user_id
    return None
