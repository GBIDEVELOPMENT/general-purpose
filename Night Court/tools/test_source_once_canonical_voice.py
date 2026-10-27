"""Offline source-first checks for one-pass original-soundtrack P0/P1 proposals."""
import unittest
from unittest.mock import patch
from source_once_canonical_voice import (
    AUDIO_S09,ORIGINAL_SOURCE,VIDEO_SHA,build_descriptors,read_canonical,
    MAX_ANCHORS_PER_ROLE,source_cue_n,
)


class OriginalCanonicalAudioTests(unittest.TestCase):
    def test_real_current_pilot_source_rows_and_candidate_windows(self):
        manifest,rows,groups=read_canonical()
        self.assertEqual(manifest["source_unit_counts"],
            {"original_source_units":751,"named_provisional":663,"unknown":88})
        self.assertEqual(set(groups),{"S01E01","S09E19"})
        for ep in ("S01E01","S09E19"):
            descriptors,excluded=build_descriptors(ep,rows[ep],
                AUDIO_S09 if ep=="S09E19" else None)
            self.assertTrue(descriptors)
            self.assertGreater(len(descriptors),15)
            self.assertTrue(excluded)
            self.assertTrue(all(len(x["source_ref"])>=6 for x in descriptors))
            self.assertTrue(all(x["original_audio_lexical_window_unverified"]==(ep=="S09E19")
                for x in descriptors))
            selected={}
            for x in descriptors:
                if x["anchor_selected"]:
                    selected[x["role"]]=selected.get(x["role"],0)+1
                    self.assertTrue(x["reference_eligible"])
                if ep=="S09E19":
                    self.assertFalse(x["time_is_original_caption"])
                else:
                    self.assertTrue(x["time_is_original_caption"])
            self.assertTrue(all(v<=MAX_ANCHORS_PER_ROLE for v in selected.values()))

    def test_mixed_s01_source_caption_is_never_used_as_clean_role_bank(self):
        rows=[
            {"reading_block_id":"one","original_source_part_refs":["C001.1"],
             "source_original_times_ms":[{"start_ms":1000,"end_ms":4200}],
             "candidate_role":"LANA","caption_text":"Hello hello everyone yes"},
            {"reading_block_id":"two","original_source_part_refs":["C001.2"],
             "source_original_times_ms":[{"start_ms":1000,"end_ms":4200}],
             "candidate_role":"HARRY","caption_text":"Yes yes hello there"},
            {"reading_block_id":"three","original_source_part_refs":["C002.1"],
             "source_original_times_ms":[{"start_ms":4300,"end_ms":6400}],
             "candidate_role":None,"caption_text":"Who could this be"}
        ]
        plan,ex=build_descriptors("S01E01",rows)
        self.assertEqual([x["source_ref"] for x in plan],["C002.1"])
        self.assertEqual(ex["multiple_people_or_split_caption"],2)
        self.assertFalse(plan[0]["anchor_selected"])
        self.assertIsNone(plan[0]["role"])

    def test_s09_no_locator_no_fake_timestamps(self):
        with self.assertRaisesRegex(ValueError,"locator required"):
            build_descriptors("S09E19",[])
        self.assertEqual(source_cue_n("C291.1"),291)
        with self.assertRaises(ValueError):
            source_cue_n("not-cue")


if __name__=="__main__":
    unittest.main()
