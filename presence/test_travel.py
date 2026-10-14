import unittest
from presence.travel import haversine, origin_weights

class VisitorTests(unittest.TestCase):
    def test_distance(self):
        self.assertAlmostEqual(haversine((0, 0), (0, 0)), 0)
        self.assertGreater(haversine((0, 0), (0, 10)), 1000)

    def test_origin_weights(self):
        w = origin_weights(
            ["AAA", "BBB", "CCC"], "CCC",
            {"AAA": 10_000_000, "BBB": 20_000_000},
            {"AAA": (0, 0), "BBB": (0, 90), "CCC": (0, 1)},
            {("AAA", "CCC"): 100_000})
        self.assertEqual(set(w), {"AAA", "BBB"})
        self.assertGreater(w["AAA"], w["BBB"])
        self.assertGreater(sum(w.values()), 0)

if __name__ == "__main__":
    unittest.main()
