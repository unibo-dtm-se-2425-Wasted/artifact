# database.py

import sqlite3
import os
import uuid                # NEW: per generare session_id unici
import streamlit as st     # NEW: per memorizzare session_id nello stato

# --- SESSIONE UTENTE --- #
def get_session_id():       # NEW
    """Crea o recupera un session_id unico per l'utente."""
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = str(uuid.uuid4())
    return st.session_state["session_id"]

def get_db_path():          # NEW
    """Costruisce il percorso del DB per questa sessione utente."""
    session_id = get_session_id()
    db_path = os.path.join("/tmp", f"food_items_{session_id}.db")  # NEW: DB temporaneo per sessione
    return db_path

# --- DATABASE FUNCTIONS --- #
def create_connection():
    """Connessione al DB specifico per l’utente corrente."""
    db_path = get_db_path()   # NEW
    conn = sqlite3.connect(db_path)
    return conn

def initialize_db():
    """Crea la tabella food_items se non esiste."""
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
    """Inserisce un nuovo item nel DB della sessione."""
    conn = create_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO food_items (name, category, purchase_date, expiration_date, quantity, unit)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, category, purchase_date, expiration_date, quantity, unit))
    conn.commit()
    conn.close()

def get_all_food_items():
    """Restituisce tutti gli item dal DB della sessione."""
    conn = create_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM food_items")
    rows = c.fetchall()
    conn.close()
    return rows

def delete_food_item(item_id):
    """Elimina un item dal DB della sessione usando l'id."""
    conn = create_connection()
    c = conn.cursor()
    c.execute("DELETE FROM food_items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
