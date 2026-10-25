import unittest
from auto_align_quote_sequence import propose
M={"episode_id":"S01E01","version_id":"v1","sha256":"abc"}
C=[{"cue":1,"text":"- Are you finished painting?\n- Yeah.","start_ms":0,"end_ms":2000},{"cue":2,"text":"Then what are you doing?","start_ms":2100,"end_ms":3000},{"cue":3,"text":"My wife won't do that.","start_ms":3100,"end_ms":4000}]
def seq(parts):
 return {"episode_id":"S01E01","source_caption_sha256":"abc","source_url":"https://example.org",
   "anchors":[{"character":name,"distinctive_fragment":fragment} for name,fragment in parts]}
class AutoAlignment(unittest.TestCase):
 def test_intra_cue_speaker_change_and_order(self):
  r=propose(M,C,seq([("LANA","finished painting"),("PAINTER","Yeah"),("LANA","what are you doing")]))
  self.assertEqual([(x["cue"],x["part"]) for x in r["anchors"]],[(1,1),(1,2),(2,1)])
  self.assertEqual(len(r["edges"]),2)
  self.assertFalse(r["independently_verified"])
 def test_missing_abstains(self):
  r=propose(M,C,seq([("LANA","unrelated unknown sentence")]))
  self.assertFalse(r["anchors"][0]["matched"])
 def test_wrong_source_rejected(self):
  s=seq([("LANA","finished painting")]);s["source_caption_sha256"]="else"
  with self.assertRaises(ValueError):propose(M,C,s)
 def test_same_cue_not_used_twice(self):
  r=propose(M,C,seq([("LANA","finished painting"),("LANA","finished painting")]))
  ids=[x["unit_id"] for x in r["anchors"] if x["matched"]]
  self.assertEqual(len(ids),len(set(ids)))
 def test_input_source_intact(self):
  before=[x.copy() for x in C]
  propose(M,C,seq([("LANA","finished painting")]))
  self.assertEqual(before,C)
if __name__=="__main__":unittest.main()
