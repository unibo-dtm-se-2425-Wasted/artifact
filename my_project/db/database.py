import sqlite3
import os
import pandas as pd


db_path = "data/food_items.db"

def create_connection():
    base_dir = os.path.dirname(os.path.abspath(__file__))  # this file's dir
    db_path = os.path.join(base_dir, "data", "food_items.db")  # absolute path
    print("Connecting to:", db_path)  # optional debug
    conn = sqlite3.connect(db_path)
    return conn


def initialize_db():
    conn = create_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS food_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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

def insert_food_item(name, category, purchase_date, expiration_date, quantity, unit):
    conn = create_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO food_items (name, category, purchase_date, expiration_date, quantity, unit)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, category, purchase_date, expiration_date, quantity, unit))
    conn.commit()
    conn.close()

def get_all_food_items():
    conn = create_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM food_items")
    rows = c.fetchall()
    conn.close()
    return rows

def delete_food_item(item_id):
    conn = create_connection()
    c = conn.cursor()
    c.execute("DELETE FROM food_items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

