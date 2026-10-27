"""Offline source-first checks for one-pass original-soundtrack P0/P1 proposals."""
import unittest
import os
import sys
from types import SimpleNamespace
from unittest.mock import patch
from source_once_canonical_voice import (
    AUDIO_S09,ORIGINAL_SOURCE,VIDEO_SHA,build_descriptors,read_canonical,
    MAX_ANCHORS_PER_ROLE,source_cue_n,acoustic_adjacent_pairs,original_media_login,source_ffmpeg_binary,
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

    def test_p0_opaque_reader_ids_and_no_skipping_source_rows(self):
        groups={
          "S01E01:speaker-evidence:0001":1,
          "S01E01:speaker-evidence:0179:speaker-p1":2,
          "S01E01:source-P0-C219:unverified-turn-1":3,
        }
        desc=[{"id":name,"window_ms":[n*3000,n*3000+2200]}
              for n,name in enumerate(groups)]
        vectors={x["id"]:[1.0,0.0] if i!=1 else [.9,.1]
                 for i,x in enumerate(desc)}
        pairs=acoustic_adjacent_pairs(desc,groups,vectors)
        self.assertEqual(len(pairs),2)
        self.assertEqual(pairs[0]["source_right"],"S01E01:speaker-evidence:0179:speaker-p1")
        self.assertTrue(all(x["source_audio_p0_performed_boundary_independently_verified"] is False
                            for x in pairs))
        vectors.pop("S01E01:speaker-evidence:0179:speaker-p1")
        self.assertEqual(acoustic_adjacent_pairs(desc,groups,vectors),[])

    def test_transient_ftp_early_eof_then_live_login(self):
        state={"tries":0}
        def fake(*args):
            state["tries"]+=1
            self.assertNotIn("password",str(args[:2]))
            if state["tries"]==1:
                raise EOFError("connection closed before 220")
            return object()
        with patch.dict(os.environ,{"FTP_PASSWORD":"test-pw","FTP_PROTOCOL":"ftps"},clear=False):
            with patch("source_once_canonical_voice.connect",side_effect=fake) as called:
                expected=original_media_login(sleep=lambda _:None)
                self.assertIsNotNone(expected)
                self.assertEqual(state["tries"],2)
                self.assertEqual(called.call_args.args[-1],"ftps")

    def test_bad_password_does_not_retry_or_log(self):
        with patch.dict(os.environ,{"FTP_PASSWORD":"secret-to-never-print"},clear=False):
            with patch("source_once_canonical_voice.connect",side_effect=__import__("ftplib").error_perm("530 forbidden")) as call:
                with self.assertRaises(__import__("ftplib").error_perm):
                    original_media_login(sleep=lambda _:None)
                self.assertEqual(call.call_count,1)

    def test_bounded_connection_retries_never_include_credentials(self):
        with patch.dict(os.environ,{"FTP_PASSWORD":"very-private-password","FTP_PROTOCOL":"ftp"},clear=False):
            with patch("source_once_canonical_voice.connect",side_effect=EOFError("bad welcome")) as call:
                with self.assertRaises(ConnectionError) as exc:
                    original_media_login(sleep=lambda _:None)
                self.assertEqual(call.call_count,3)
                self.assertNotIn("very-private-password",str(exc.exception))
                self.assertIn("EOFError",str(exc.exception))


    def test_audio_decoder_uses_packaged_pinned_ffmpeg_without_apt(self):
        mock=SimpleNamespace(get_ffmpeg_exe=lambda:"/private/venv/imageio_ffmpeg/bin/ffmpeg")
        with patch.dict(sys.modules,{"imageio_ffmpeg":mock}):
            self.assertEqual(source_ffmpeg_binary(),"/private/venv/imageio_ffmpeg/bin/ffmpeg")

    def test_s09_no_locator_no_fake_timestamps(self):
        with self.assertRaisesRegex(ValueError,"locator required"):
            build_descriptors("S09E19",[])
        self.assertEqual(source_cue_n("C291.1"),291)
        with self.assertRaises(ValueError):
            source_cue_n("not-cue")


if __name__=="__main__":
    unittest.main()
