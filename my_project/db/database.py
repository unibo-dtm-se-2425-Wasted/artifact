import sqlite3

DB_NAME = "food.db"

def initialize_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS food_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            purchase_date DATE NOT NULL,
            expiration_date DATE NOT NULL,
            quantity REAL,
            unit TEXT
        );
    """)
    conn.commit()
    conn.close()

def insert_food_item(user, name, category, purchase_date, expiration_date, quantity, unit):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO food_items (user, name, category, purchase_date, expiration_date, quantity, unit)
        VALUES (?,?,?,?,?,?,?)
    """, (user, name, category, purchase_date, expiration_date, quantity, unit))
    conn.commit()
    conn.close()

def get_all_food_items(user):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        SELECT id, user, name, category, purchase_date, expiration_date, quantity, unit
        FROM food_items WHERE user=?
    """, (user,))
    rows = c.fetchall()
    conn.close()
    return rows
