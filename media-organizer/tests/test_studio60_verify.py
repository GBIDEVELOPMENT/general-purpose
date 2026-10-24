import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from studio60_verify import analyze
class Studio60VerificationTests(unittest.TestCase):
    def sample(self):
        names=[]
        for i in range(1,23):
            stem=f"Studio 60 on the Sunset Strip (2006) - S01E{i:02} - Example Episode"
            names += [stem+" - "+v for v in
                      ("1080p.mp4","720p.mp4","XviD DVDRip.avi","DVD.avi","DVD.idx","DVD.sub")]
        return names
    def test_22_episode_four_edition_complete(self):
        r=analyze(self.sample())
        self.assertFalse(r["failures"])
        self.assertEqual(r["files_recognized"],132)
        self.assertEqual(r["edition_counts"]["DVD.sub"],22)
    def test_no_silent_loss_of_dvd_subtitles(self):
        files=[x for x in self.sample() if not ("S01E04" in x and x.endswith(".sub"))]
        r=analyze(files)
        self.assertEqual([x["episode"] for x in r["failures"]],[4])
        self.assertEqual(r["failures"][0]["missing"],["DVD.sub"])
    def test_title_mismatch_is_detected(self):
        f=self.sample()
        f[0]=f[0].replace("Example Episode","Conflicting Episode")
        self.assertEqual([r["episode"] for r in analyze(f)["failures"]],[1])
if __name__=="__main__":unittest.main()
