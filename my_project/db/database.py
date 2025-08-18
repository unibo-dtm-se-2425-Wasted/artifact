import sqlite3
import os
import streamlit as st  # NEW

# --- SESSIONE UTENTE --- #
def get_user_db_path():  # NEW
    """Ritorna il percorso del DB specifico per l'utente."""
    if "user_id" not in st.session_state:
        import uuid
        st.session_state["user_id"] = str(uuid.uuid4())  # NEW
    user_id = st.session_state["user_id"]
    db_path = os.path.join("/tmp", f"food_items_{user_id}.db")  # NEW
    return db_path

# --- DATABASE FUNCTIONS --- #
def create_connection():
    db_path = get_user_db_path()  # NEW
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
