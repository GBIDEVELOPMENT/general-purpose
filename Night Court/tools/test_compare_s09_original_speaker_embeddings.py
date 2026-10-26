#!/usr/bin/env python3
"""Offline S09 original audiobook-source alignment to provisional actor-role QA."""
from __future__ import annotations
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from compare_s09_original_speaker_embeddings import (
    SCHEMA, ALIGNMENT_REPORT_SHA, VIDEO_SHA, PCM_SHA,
    MIN_QUERY_MS, prepare_eligible, read_alignment,
)


def aligned(n,seconds=2400,coverage=.93,words=6):
    return {
        "original_paragraph_id":n,
        "candidate_original_audio_window_ms":[n*5000,n*5000+seconds],
        "global_audio_alignment_lexical_coverage":coverage,
        "exact_source_words_globally_matched":words,
        "original_paragraph_timecode_ms":None,
        "original_film_audio_timing_independently_verified":False,
        "spoken_character_identity_verified":False,
    }


def reading(n,role):
    return {
        "original_source_part_refs":[f"C{n:03d}.1"],
        "candidate_role":role,
        "source_reading_ref":f"C{n:03d}.1",
        "speaker_turn_boundary_verified":False,
        "actor_face_or_voice_independently_verified":False,
    }


class OriginalS09VoicePlanTests(unittest.TestCase):
    def test_known_role_samples_and_original_unknowns_without_fake_timestamps(self):
        rows=[aligned(n) for n in (1,2,3,4,5,6,7,8,9,10,11,12,102,13)]
        source={x["original_paragraph_id"]:[reading(
            x["original_paragraph_id"],
            "HARRY STONE" if x["original_paragraph_id"]<=4 else (
                "CHRISTINE SULLIVAN" if x["original_paragraph_id"]<=8 else (
                None if x["original_paragraph_id"]<=13 else None))
        )] for x in rows}
        plan=prepare_eligible({"matches":rows},source)
        self.assertEqual(plan["schema"],SCHEMA)
        self.assertEqual(plan["original_video_sha256_required"],VIDEO_SHA)
        self.assertEqual(plan["input_audio_alignment_report_sha256"],ALIGNMENT_REPORT_SHA)
        self.assertEqual(plan["candidate_reference_role_counts"],{
            "CHRISTINE SULLIVAN":4,"HARRY STONE":4
        })
        self.assertEqual(len(plan["previously_unidentified_audio_windows"]),5)
        self.assertIn(102,[x["original_paragraph_id"] for x in rows])
        self.assertNotIn(102,[x["original_source_paragraph"] for x in
                              plan["previously_unidentified_audio_windows"]])
        self.assertTrue(plan["original_paragraphs_remain_untimed"])
        self.assertFalse(plan["original_speech_identity_human_verified"])

    def test_low_alignment_and_short_or_multi_voice_audio_abstain(self):
        values=[aligned(1,seconds=1450),aligned(2,coverage=.49),
                aligned(3,words=2),aligned(4)]
        sources={n:[reading(n,None)] for n in range(1,5)}
        sources[4].append(reading(4,"HARRY STONE"))
        plan=prepare_eligible({"matches":values},sources)
        self.assertEqual(plan["source_aligned_audio_windows_eligible_for_single_voice_comparison"],0)
        self.assertEqual(plan["potentially_multivoice_or_weak_alignment_rejected_count"],4)

    def test_newer_source_names_extend_audio_seed_pool_but_do_not_invent_names(self):
        seen=[aligned(i) for i in range(1,17)]
        # The old reader only knew two named characters in these windows,
        # while the v8 role proposal view includes another character.
        old={i:[reading(i,"CHRISTINE SULLIVAN" if i<=4
                           else ("ROZ RUSSELL" if i<=8 else None))]
             for i in range(1,17)}
        current=copy.deepcopy(old)
        for i in range(9,13):
            current[i][0]["candidate_role"]="DAN FIELDING"
        previous=prepare_eligible({"matches":seen},old)
        updated=prepare_eligible({"matches":seen},current)
        self.assertEqual(len(previous["candidate_reference_role_counts"]),2)
        self.assertEqual(len(updated["candidate_reference_role_counts"]),3)
        self.assertEqual(updated["candidate_reference_role_counts"]["DAN FIELDING"],4)
        self.assertEqual(len(updated["previously_unidentified_audio_windows"]),4)
        self.assertTrue(all(x["candidate_role"] is None
                            for x in updated["previously_unidentified_audio_windows"]))
        # Sensitivity sweep changes candidate pool size, not audio identity
        # acceptance rules or original subtitle timing.
        marginal=aligned(17,coverage=.61)
        relaxed=prepare_eligible({"matches":seen+[marginal]},
            {**current,17:[reading(17,None)]},minimum_coverage=.60)
        self.assertEqual(len(relaxed["previously_unidentified_audio_windows"]),5)
        self.assertTrue(relaxed["original_paragraphs_remain_untimed"])
        with self.assertRaises(ValueError):
            prepare_eligible({"matches":seen},current,minimum_coverage=.10)

    def test_exact_original_report_sha_and_source_status_fail_closed(self):
        fake={
            "schema":"night-court-s09-original-film-untimed-paragraph-audio-locator/1",
            "original_video_sha256":VIDEO_SHA,
            "original_untimed_source_sha256":
                "659beb9c50fabdd1028aac9570999d9a16b36e6d582938e10809cc0c664530b2",
            "original_audio_pcm_sha256":PCM_SHA,
            "source_paragraphs":347,
            "source_exact_sequence_word_matches":1803,
            "candidate_source_paragraphs_given_audio_window":231,
            "original_speaker_identities_verified":0,
            "exact_subtitle_timecode_recovered":0,
            "matches":[aligned(i+1) for i in range(231)]
        }
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/"source-audio.json"
            path.write_text(json.dumps(fake),"utf-8")
            with self.assertRaisesRegex(ValueError,"SHA mismatch"):
                read_alignment(path)
            with patch("compare_s09_original_speaker_embeddings.digest",
                       return_value=ALIGNMENT_REPORT_SHA):
                data=read_alignment(path)
                self.assertEqual(len(data["matches"]),231)
                fake["matches"][0]["original_paragraph_timecode_ms"]=5000
                path.write_text(json.dumps(fake),"utf-8")
                with self.assertRaisesRegex(ValueError,"malformed"):
                    read_alignment(path)


if __name__=="__main__":
    unittest.main()
