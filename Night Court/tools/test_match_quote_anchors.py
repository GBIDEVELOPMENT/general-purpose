import unittest
from match_quote_anchors import align, SCHEMA
C=[{"cue":1,"text":"How did you get appointed to the bench?"},
{"cue":2,"text":"I was home."},{"cue":3,"text":"I was home."}]
I={"sha256":"testhash","version_id":"testversion"}
def source(excerpt):
 return {"quote_id":"test","episode_id":"S01E01","excerpt":excerpt,
 "source_character":"DAN","source_url":"https://en.wikiquote.org/wiki/Night_Court_(season_1)"}
class QuoteTests(unittest.TestCase):
 def test_distinct_quote_yields_provisional_candidate(self):
  r=align({"schema":SCHEMA,"quotes":[source("How did you get appointed to the bench?")]},"S01E01",I,C)
  self.assertEqual(r["candidates"][0]["candidate_cue_ids"],[1])
  self.assertFalse(r["candidates"][0]["speaker_identity_accepted"])
 def test_repeated_quote_ambiguous(self):
  r=align({"schema":SCHEMA,"quotes":[source("I was home.")]},"S01E01",I,C)
  self.assertEqual(r["candidates"][0]["candidate_cue_ids"],[])
 def test_cross_episode_rejected(self):
  q=source("How did you get appointed to the bench?");q["episode_id"]="S09E19"
  with self.assertRaises(ValueError):align({"schema":SCHEMA,"quotes":[q]},"S01E01",I,C)
 def test_source_unchanged(self):
  original=[x.copy() for x in C]
  align({"schema":SCHEMA,"quotes":[source("How did you get appointed to the bench?")]},"S01E01",I,C)
  self.assertEqual(C,original)
if __name__=="__main__":unittest.main()
