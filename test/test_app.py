import unittest
import pandas as pd
from app import calculate_statistics

class TestAppLogic(unittest.TestCase):
    def test_calculate_statistics(self):
        data = {
            "ID": [1, 2, 3, 4],
            "Status": ["✅ OK", "❌ Expired", "⚠️ Expiring Soon", "✅ OK"],
            "quantity": [1, 2, 0.5, 3],
            "price_per_unit": [2.0, 1.25, 3.0, 1.0]
        }
        df = pd.DataFrame(data)

        total, expired, ok_items, lost_value = calculate_statistics(df)

        self.assertEqual(total, 4)
        self.assertEqual(expired, 1)
        self.assertEqual(ok_items, 3)
        self.assertAlmostEqual(lost_value, 2.5)  # 2 * 1.25 = 2.5 €

if __name__ == '__main__':
    unittest.main()
