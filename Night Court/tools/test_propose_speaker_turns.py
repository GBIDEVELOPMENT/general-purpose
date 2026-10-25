#!/usr/bin/env python3
"""P0 caption-turn proposal unit acceptance, fully synthetic."""
import unittest
from propose_speaker_turns import propose

def u(cue,part,label=None,start=None,end=None):
    return {"unit_id":f"C{cue}.{part}","cue":cue,"part":part,
      "speaker_label_from_source":label,"source_sha256":"source",
      "source_version_id":"v1","source_text":f"line-{cue}-{part}",
      "start_ms":start,"end_ms":end}

class Segmentation(unittest.TestCase):
    def test_merge_only_explicit_same_label(self):
        rows=[u(1,1,"HARRY",0,500),u(2,1,"HARRY",510,900),
              u(3,1,"DAN",910,1100)]
        turns,decisions=propose(rows)
        self.assertEqual([len(t["unit_ids"]) for t in turns],[2,1])
        self.assertEqual(decisions[0]["decision"],"merge_same_explicit_source_label_provisional")
        self.assertEqual(decisions[1]["decision"],"keep_separate_explicit_label_change")
        self.assertFalse(turns[0]["character_identity_verified"])

    def test_unknown_is_not_assumed_new_or_same_speaker(self):
        rows=[u(1,1,None,0,100),u(2,1,None,110,250)]
        turns,decisions=propose(rows)
        self.assertEqual(len(turns),2)
        self.assertEqual(decisions[0]["decision"],"unknown_speaker_boundary_review")

    def test_intra_caption_split_not_recombined(self):
        rows=[u(1,1,None,0,100),u(1,2,None,0,100)]
        turns,decisions=propose(rows)
        self.assertEqual(len(turns),2)
        self.assertEqual(decisions[0]["left_cue"],decisions[0]["right_cue"])

    def test_untimed_same_label_can_merge_but_not_verify(self):
        turns,decisions=propose([u(1,1,"HARRY"),u(2,1,"HARRY")])
        self.assertEqual(len(turns),1)
        self.assertFalse(turns[0]["boundary_verified"])
        self.assertIsNone(decisions[0]["gap_ms"])

    def test_long_pause_and_nonadjacent_not_merged(self):
        rows=[u(1,1,"HARRY",0,100),u(2,1,"HARRY",4000,4200),
              u(5,1,"HARRY",4300,4700)]
        turns,decisions=propose(rows)
        self.assertEqual(len(turns),3)
        self.assertEqual(decisions[0]["decision"],"keep_separate_long_pause_review")
        self.assertEqual(decisions[1]["decision"],"keep_separate_source_discontinuity")

    def test_every_source_part_survives_in_order(self):
        rows=[u(1,1,"HARRY"),u(2,1,"HARRY"),u(3,1,None),u(4,1,"DAN")]
        turns,_=propose(rows)
        self.assertEqual([part for t in turns for part in t["source_text_parts"]],
                         [r["source_text"] for r in rows])

if __name__=="__main__":unittest.main()
