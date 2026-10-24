import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from plex_filename_audit import scan_inventory,markdown

def scan(*paths,truncated=None):
    data={"root":"/downloads","files":[{"path":p,"size":99,"modify":None} for p in paths],"truncated":truncated or [],"failures":[]}
    return scan_inventory(data)
class PlexFilenameAuditTests(unittest.TestCase):
    def test_old_style_night_court_episode_is_flagged(self):
        r=scan("/downloads/Night Court S01/Night Court - 1x01 - Pilot.avi")
        self.assertEqual(r["summary"]["legacy_1x_episode"],1)
        self.assertIn("S01E01",r["issues"][0]["suggestion"])
    def test_multi_episode_preserves_second_code(self):
        r=scan("/downloads/Show/Show.S01E01E02.mkv")
        self.assertEqual(r["summary"]["multiple_episodes"],1)
    def test_cross_season_is_not_normal_multi_episode(self):
        r=scan("/downloads/TNG/TNG.S03E26S04E01.mkv")
        self.assertEqual(r["summary"]["cross_season_episode"],1)
        self.assertNotIn("multiple_episodes",r["summary"])
    def test_sample_is_high_risk(self):
        r=scan("/downloads/Movie 2025/Sample.mkv")
        self.assertEqual(r["summary"]["sample_or_proof_video"],1)
    def test_year_after_episode_is_flagged(self):
        r=scan("/downloads/Bait/Bait.S01E02.2026.1080p.mkv")
        self.assertEqual(r["summary"]["year_after_episode_code"],1)
    def test_clean_tv_name_not_flagged(self):
        r=scan("/downloads/Joey/Season 01/Joey - S01E01 - Pilot.mkv")
        self.assertEqual(r["issues"],[])
    def test_truncation_never_claims_complete(self):
        r=scan("/downloads/Test/Test.S01E01.mkv",truncated=["/downloads/Other"])
        self.assertFalse(r["inventory_complete"])
        self.assertIn("no; scan was truncated",markdown(r))
if __name__=="__main__":unittest.main()
