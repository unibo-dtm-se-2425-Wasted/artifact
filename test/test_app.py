import unittest
import pandas as pd
from my_project.app import calculate_statistics

class TestAppLogic(unittest.TestCase):
    def test_calculate_statistics(self):
        # Creiamo un DataFrame di prova
        data = {
            "ID": [1, 2, 3, 4],
            "Status": ["✅ OK", "❌ Expired", "⚠️ Expiring Soon", "✅ OK"]
        }
        df = pd.DataFrame(data)

        # Chiamiamo la funzione da testare
        total, expired, ok_items = calculate_statistics(df)
        
        # Verifichiamo che i valori restituiti siano quelli attesi
        self.assertEqual(total, 4)
        self.assertEqual(expired, 1)
        self.assertEqual(ok_items, 3)

if __name__ == '__main__':
    unittest.main()






