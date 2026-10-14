import csv
import tempfile
import unittest
from pathlib import Path

from presence.physical import project


def put(directory, filename, columns, records):
    with (directory / filename).open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(columns)
        w.writerows(records)


class PhysicalPresenceTests(unittest.TestCase):
    def test_birthplace_departs_host_and_arrives_destination(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            countries = [(124, "Canada", "", 0), (484, "Mexico", "", 0),
                         (840, "United States", "", 300)]
            put(d, "country_totals_2024.csv",
                ["m49", "country", "UN_emigrants", "UN_immigrants"],
                countries)
            rows = [(a, b, c, e, 300 if a == 484 and c == 840 else 0,
                     "UN_reported") for a, b in [(124, "Canada"), (484, "Mexico"), (840, "United States")]
                    for c, e in [(124, "Canada"), (484, "Mexico"), (840, "United States")] if a != c]
            put(d, "pairs_2024.csv",
                ["origin_m49", "origin", "destination_m49", "destination",
                 "resident_estimate", "evidence"], rows)
            put(d, "origin_population_2024.csv",
                ["iso3", "m49", "country", "2024_population"],
                [("CAN", 124, "Canada", 1000), ("MEX", 484, "Mexico", 1000),
                 ("USA", 840, "United States", 1000)])
            put(d, "visitors_average_day_2024.csv",
                ["origin_residence_iso3", "destination_iso3", "overnight_visitors_avg_day"],
                [("USA", "CAN", 100)])
            info = project(d)
            with (d / "physical_presence_by_birth_2024.csv").open() as f:
                matrix = {(int(r["birth_origin_m49"]), int(r["physical_destination_m49"])):
                          int(r["average_day_physical_estimate"]) for r in csv.DictReader(f)}
            self.assertEqual(matrix[484, 840], 270)
            self.assertEqual(matrix[484, 124], 30)
            self.assertEqual(matrix[840, 124], 70)
            self.assertEqual(info["total_estimated_born_abroad_physically"], 370)


if __name__ == "__main__":
    unittest.main()
