import unittest
import pandas as pd
from app import calculate_statistics

class TestAppLogic(unittest.TestCase):
    def test_calculate_statistics(self):
        # Create a sample DataFrame with quantity and price_per_unit
        data = {
            "ID": [1, 2, 3, 4],
            "Status": ["✅ OK", "❌ Expired", "⚠️ Expiring Soon", "✅ OK"],
            "Quantity": [1, 2, 0.5, 3],
            "Price per Unit": [2.0, 1.25, 3.0, 1.0]
        }
        df = pd.DataFrame(data)

        # Call the function to test
        total, expired, ok_items, lost_value = calculate_statistics(df)
        
        # Check that the returned values are as expected
        self.assertEqual(total, 4)
        self.assertEqual(expired, 1)
        self.assertEqual(ok_items, 3)
        self.assertAlmostEqual(lost_value, 2.5)  # 2 units * 1.25€ = 2.5€

if __name__ == '__main__':
    unittest.main()







