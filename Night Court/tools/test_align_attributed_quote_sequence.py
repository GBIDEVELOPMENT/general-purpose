import unittest
from align_attributed_quote_sequence import sequence_proposals
M={"episode_id":"S01E01","version_id":"v1","sha256":"hash"}
C=[{"cue":1,"text":"- Are you finished painting?\n- Yeah.","start_ms":0,"end_ms":1000},
{"cue":2,"text":"Then what are you doing?","start_ms":1001,"end_ms":1900}]
S={"episode_id":"S01E01","source_caption_sha256":"hash","source_url":"https://www.imdb.com/title/example/quotes/",
"anchors":[{"cue":1,"part":1,"character":"LANA","distinctive_fragment":"finished painting"},
{"cue":1,"part":2,"character":"PAINTER","distinctive_fragment":"Yeah"},
{"cue":2,"part":1,"character":"LANA","distinctive_fragment":"what are you doing"}]}
class TestSequence(unittest.TestCase):
 def test_source_part_and_speaker_switch(self):
  out=sequence_proposals(M,C,S)
  self.assertEqual(out["lexically_supported"],3)
  self.assertEqual([x["proposed_relationship"] for x in out["adjacent_anchor_edges"]],["speaker_change","speaker_change"])
  self.assertFalse(out["independently_verified"])
  self.assertTrue(all(not x["speaker_identity_accepted"] for x in out["anchors"]))
 def test_wrong_hash_or_order_rejected(self):
  from copy import deepcopy
  x=deepcopy(S);x["source_caption_sha256"]="other"
  with self.assertRaises(ValueError):sequence_proposals(M,C,x)
  x=deepcopy(S);x["anchors"].reverse()
  with self.assertRaises(ValueError):sequence_proposals(M,C,x)
 def test_missing_part_rejected(self):
  from copy import deepcopy
  x=deepcopy(S);x["anchors"][0]["part"]=3
  with self.assertRaises(ValueError):sequence_proposals(M,C,x)
if __name__=="__main__":unittest.main()
