import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from delete_debris import category,assess,validate
class DebrisTests(unittest.TestCase):
    def test_nfo(self):self.assertEqual(category("/downloads/Movie/info.nfo"),"nfo")
    def test_screens(self):self.assertEqual(category("/downloads/Movie/Screens/mpv-shot0001.jpg"),"screenshot")
    def test_named_screenshot_file_outside_screens_dir(self):
        self.assertEqual(category("/downloads/S60/DVD/Studio 60 - 01 - SCREENSHOTS.jpg"),"screenshot")
    def test_explicit_release_sample_and_trailer(self):
        self.assertEqual(category("/downloads/Film.2025/Sample.mkv"),"sample")
        self.assertEqual(category("/downloads/Film.2025/Sample/film-sample.mkv"),"sample")
        self.assertEqual(category("/downloads/Film.2025/Film-trailer.mp4"),"trailer")
        self.assertEqual(category("/downloads/Film.2025/teaser.mov"),"trailer")
    def test_never_treat_normal_episode_as_clip(self):
        for p in ("/downloads/S01E01.sample.mkv",
                  "/downloads/S01E01.trailer.mp4",
                  "/downloads/Film.2025.mkv",
                  "/downloads/sample.srt",
                  "/downloads/Film.Sampler.2024.mp4"):
            self.assertIsNone(category(p),p)
    def test_manifest_accepts_exact_sample_and_rejects_fabricated_identity(self):
        x={"root":"/downloads","batch_id":"sample_001",
           "description":"Exact owner-approved movie release sample",
           "entries":[{"from":"/downloads/Film.2025/Sample.mkv",
                       "size":800,"modify":"20261023000000","category":"sample"}]}
        self.assertEqual(len(validate(x)),1)
        x["entries"][0]["category"]="trailer"
        with self.assertRaises(ValueError):validate(x)
    def test_keep_artwork(self):
        for x in ("poster.jpg","fanart.jpg","cover.png","Photoshop.png","folder.jpg"):
            self.assertIsNone(category("/downloads/Movie/"+x))
    def test_keep_archives_unapproved(self):
        inv={"files":[{"path":"/downloads/Movie/release.r00","size":100},{"path":"/downloads/Movie/Movie.mkv","size":1000}]}
        a=assess(inv)
        self.assertEqual(len(a["archive_review"]),1)
        self.assertEqual(a["debris_candidates"],[])
    def test_refuse_archive(self):
        m={"root":"/downloads","batch_id":"delete_01","description":"Verified cleanup small trial","entries":[{"from":"/downloads/a.rar","size":2,"modify":None,"category":"nfo"}]}
        with self.assertRaises(ValueError):validate(m)
if __name__=="__main__":unittest.main()
