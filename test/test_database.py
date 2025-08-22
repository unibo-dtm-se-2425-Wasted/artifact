import unittest
from my_project.db import database
import os
import sqlite3

class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Usa un database di test in un file temporaneo
        self.test_db_path = "test_food_items.db"

        # Crea manualmente una connessione al DB di test
        def test_create_connection():
            return sqlite3.connect(self.test_db_path)

        # Monkey-patch della funzione create_connection
        database.create_connection = test_create_connection

        # Inizializza la struttura della tabella nel DB di test
        database.initialize_db()

    def tearDown(self):
        # Elimina il DB temporaneo
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_insert_and_get(self):
        database.insert_food_item("carlo", "Milk", "Dairy", "2025-08-01", "2025-08-10", 1.0, "L", 1.5 )
        items = database.get_all_food_items("carlo")
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0][2], "Milk") 

    def test_insert_zero_quantity(self):
        database.insert_food_item("carlo", "Yogurt", "Dairy", "2025-08-01", "2025-08-05", 0.0, "pack", 0.5)
        items = database.get_all_food_items("carlo")
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0][2], "Yogurt")  

    
    def setUp(self):
        # Usa un database temporaneo
        self.test_db_path = "test_users.db"

        # Monkey-patch della create_connection per puntare al DB di test
        def test_create_connection():
            return sqlite3.connect(self.test_db_path)

        database.create_connection = test_create_connection

        # Inizializza schema DB
        database.initialize_db()

    def tearDown(self):
        # Elimina DB temporaneo
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_add_and_login_user(self):
        # Aggiungo un nuovo utente
        database.add_user("alice", "password123")

        # Login con credenziali corrette
        self.assertTrue(database.check_user_credentials("alice", "password123"))

        # Login con password sbagliata
        self.assertFalse(database.check_user_credentials("alice", "wrongpass"))

        # Login con utente inesistente
        self.assertFalse(database.check_user_credentials("bob", "password123"))

    def test_duplicate_user(self):
        # Inserisco due volte lo stesso utente
        database.add_user("carlo", "secret")
        database.add_user("carlo", "secret")  # non deve generare errore

        # Login deve funzionare
        self.assertTrue(database.check_user_credentials("carlo", "secret"))

if __name__ == "__main__":
    unittest.main()


