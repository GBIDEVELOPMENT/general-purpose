import tempfile
import unittest
from pathlib import Path
from openpyxl import Workbook

from presence.build import integer, is_country, extract

class PresenceTest(unittest.TestCase):
    def test_numbers(self):
        self.assertEqual(integer("1,234"), 1234)
        self.assertIsNone(integer(".."))
        self.assertTrue(is_country(840))
        self.assertFalse(is_country(900))

    def test_fail_closed_on_incomplete_table(self):
        wb = Workbook()
        ws = wb.active
        ws.title = "Table 1"
        for _ in range(11):
            ws.append(["header"])
        row = [None] * 15
        row[1], row[4], row[5], row[6], row[14] = "World", 900, "World", 900, 304021813
        ws.append(row)
        with tempfile.TemporaryDirectory() as td:
            file = Path(td) / "sample.xlsx"
            wb.save(file)
            with self.assertRaisesRegex(ValueError, "Data too sparse"):
                extract(file)

if __name__ == "__main__":
    unittest.main()
