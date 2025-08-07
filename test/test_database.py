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
        database.insert_food_item("Milk", "Dairy", "2025-08-01", "2025-08-10", 1.0, "L")
        items = database.get_all_food_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0][1], "Milk")
    
    def test_insert_zero_quantity(self):
        database.insert_food_item("Yogurt", "Dairy", "2025-08-01", "2025-08-05", 0.0, "pack")
        items = database.get_all_food_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0][1], "Yogurt")
    
if __name__ == '__main__':
    unittest.main()

