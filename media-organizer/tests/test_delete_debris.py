import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from delete_debris import category,assess,validate
class DebrisTests(unittest.TestCase):
    def test_nfo(self):self.assertEqual(category("/downloads/Movie/info.nfo"),"nfo")
    def test_screens(self):self.assertEqual(category("/downloads/Movie/Screens/mpv-shot0001.jpg"),"screenshot")
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
