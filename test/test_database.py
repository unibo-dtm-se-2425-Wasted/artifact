import unittest
import os
import sqlite3
from my_project.db import database

class TestFoodItems(unittest.TestCase):
    def setUp(self):
        # Usa un database temporaneo per gli alimenti
        self.test_db_path = "test_food_items.db"

        def test_create_connection():
            return sqlite3.connect(self.test_db_path)

        # Monkey-patch della funzione create_connection
        database.create_connection = test_create_connection

        # Inizializza schema DB
        database.initialize_db()

    def tearDown(self):
        # Elimina DB temporaneo
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_insert_and_get(self):
        database.insert_food_item("carlo", "Milk", "Dairy", "2025-08-01", "2025-08-10", 1.0, "L", 1.5)
        items = database.get_all_food_items("carlo")
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0][2], "Milk")

    def test_insert_zero_quantity(self):
        database.insert_food_item("carlo", "Yogurt", "Dairy", "2025-08-01", "2025-08-05", 0.0, "pack", 0.5)
        items = database.get_all_food_items("carlo")
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0][2], "Yogurt")


class TestUsers(unittest.TestCase):
    def setUp(self):
        # Usa un database temporaneo per gli utenti
        self.test_db_path = "test_users.db"

        def test_create_connection():
            return sqlite3.connect(self.test_db_path)

        # Monkey-patch della funzione create_connection
        database.create_connection = test_create_connection

        # Inizializza schema DB
        database.initialize_db()

    def tearDown(self):
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_add_and_login_user(self):
        database.add_user("alice", "password123")

        # Login con credenziali corrette
        self.assertTrue(database.check_user_credentials("alice", "password123"))

        # Login con password sbagliata
        self.assertFalse(database.check_user_credentials("alice", "wrongpass"))

        # Login con utente inesistente
        self.assertFalse(database.check_user_credentials("bob", "password123"))

    def test_duplicate_user(self):
        database.add_user("carlo", "secret")
        database.add_user("carlo", "secret")  # non deve generare errore

        self.assertTrue(database.check_user_credentials("carlo", "secret"))


if __name__ == "__main__":
    unittest.main()
