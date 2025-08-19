import sqlite3
import os

def _users_dir():
    # cartella dove mantenere i DB per utente
    base_dir = os.path.dirname(os.path.abspath(__file__))
    user_dir = os.path.join(base_dir, "data", "users")
    os.makedirs(user_dir, exist_ok=True)
    return user_dir

def _db_path_for_user(user: str) -> str:
    safe_user = str(user).replace(os.sep, "_").replace("..", "_")
    return os.path.join(_users_dir(), f"{safe_user}_food_items.db")

def create_connection(user: str):
    """Connessione al DB del singolo utente."""
    path = _db_path_for_user(user)
    conn = sqlite3.connect(path, check_same_thread=False)
    return conn

def initialize_db(user: str):
    """Crea la tabella per l'utente se non esiste."""
    conn = create_connection(user)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS food_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            purchase_date TEXT,
            expiration_date TEXT,
            quantity REAL,
            unit TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_food_item(user: str, name: str, category: str,
                     purchase_date: str, expiration_date: str,
                     quantity: float, unit: str):
    conn = create_connection(user)
    c = conn.cursor()
    c.execute("""
        INSERT INTO food_items (name, category, purchase_date, expiration_date, quantity, unit)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, category, purchase_date, expiration_date, quantity, unit))
    conn.commit()
    conn.close()

def get_all_food_items(user: str):
    conn = create_connection(user)
    c = conn.cursor()
    c.execute("SELECT id, name, category, purchase_date, expiration_date, quantity, unit FROM food_items")
    rows = c.fetchall()
    conn.close()
    return rows

def delete_food_item(user: str, item_id: int):
    conn = create_connection(user)
    c = conn.cursor()
    c.execute("DELETE FROM food_items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
