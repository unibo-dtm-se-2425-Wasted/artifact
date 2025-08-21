import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "food_items.db")

def create_connection():
    conn = sqlite3.connect(db_path)
    return conn

def initialize_db():
    conn = create_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS food_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL COLLATE NOCASE,   -- 🔑 qui NOCASE
            name TEXT NOT NULL,
            category TEXT,
            purchase_date TEXT,
            expiration_date TEXT,
            quantity REAL,
            unit TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_food_item(user, name, category, purchase_date, expiration_date, quantity, unit):
    conn = create_connection()
    c = conn.cursor()
    # 🔑 NON normalizziamo più → salvi esattamente come arriva
    c.execute("""
        INSERT INTO food_items (user, name, category, purchase_date, expiration_date, quantity, unit)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user, name, category, purchase_date, expiration_date, quantity, unit))
    conn.commit()
    conn.close()

def get_all_food_items(user):
    conn = create_connection()
    c = conn.cursor()
    # 🔑 il confronto è case-insensitive grazie a COLLATE NOCASE
    c.execute("SELECT * FROM food_items WHERE user = ? COLLATE NOCASE", (user,))
    rows = c.fetchall()
    conn.close()
    return rows

def delete_food_item(item_id, user):
    conn = create_connection()
    c = conn.cursor()
    c.execute("DELETE FROM food_items WHERE id = ? AND user = ? COLLATE NOCASE", (item_id, user))
    conn.commit()
    conn.close()

def get_unique_users():
    conn = create_connection()
    c = conn.cursor()
    # DISTINCT case-insensitive (collate applicato alla colonna, non alla tabella)
    c.execute("SELECT DISTINCT user COLLATE NOCASE FROM food_items")
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]

