import sqlite3
import os
import streamlit as st


def get_user_db_path():
    """
    Restituisce il percorso del DB personale dell'utente.
    Ogni utente ha un ID univoco salvato in st.session_state.
    """
    if "user_id" not in st.session_state:
        import uuid
        st.session_state["user_id"] = str(uuid.uuid4())[:8]  # genera ID random
    
    user_id = st.session_state["user_id"]

    # directory "data" accanto al file db.py
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

    return os.path.join(data_dir, f"food_items_{user_id}.db")


def create_connection():
    """Crea la connessione al DB dell'utente corrente."""
    db_path = get_user_db_path()
    conn = sqlite3.connect(db_path)
    return conn


def initialize_db():
    """Crea la tabella food_items se non esiste già."""
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
    """Inserisce un nuovo alimento nel DB utente."""
    conn = create_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO food_items (name, category, purchase_date, expiration_date, quantity, unit)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, category, str(purchase_date), str(expiration_date), quantity, unit))
    conn.commit()
    conn.close()


def get_all_food_items():
    """Ritorna tutti gli alimenti salvati nel DB utente."""
    conn = create_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM food_items")
    rows = c.fetchall()
    conn.close()
    return rows


def delete_food_item(item_id):
    """Cancella un alimento dal DB utente per ID."""
    conn = create_connection()
    c = conn.cursor()
    c.execute("DELETE FROM food_items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
