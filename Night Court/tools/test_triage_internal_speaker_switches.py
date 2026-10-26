#!/usr/bin/env python3
"""Synthetic fail-closed QA for original internal subtitle speaker switches."""
import copy
import unittest
from unittest.mock import patch
from triage_internal_speaker_switches import SCHEMA, OUTPUT, validate, SOURCES


def fixture():
    seeds={
        "schema":SCHEMA,
        "no_source_cue_automatically_changed":True,
        "no_character_assigned":True,
        "independently_original_audio_reviewed":False,
        "cues":[
            {"episode_id":"S01E01","original_cue":1,
             "split_before":"Yeah.","reason":"internal dash reply"},
            {"episode_id":"S09E19","original_cue":1,
             "split_before":"No, really.","reason":"internal reply"}
        ]
    }
    def witness(root,ep):
        if ep=="S01E01":
            return {"sha256":SOURCES[ep],"timecoded":True},[
                {"cue":1,"text":"How'd that go? - Yeah.","start_ms":3000,"end_ms":5000}
            ]
        return {"sha256":SOURCES[ep],"timecoded":False},[
            {"cue":1,"text":"Here, take this. No, really.","start_ms":None,"end_ms":None}
        ]
    return seeds,witness


class InternalSpeakerTurnTests(unittest.TestCase):
    def test_exact_source_lossless_conservation_and_unverified_names(self):
        seed,witness=fixture()
        with patch("triage_internal_speaker_switches.load_witness",side_effect=witness):
            packets,report=validate(None,seed,strict=False)
        self.assertEqual(len(packets),2)
        self.assertEqual(report["actually_verified_new_speaker_switches"],0)
        self.assertEqual(report["new_original_soundtrack_accepted_speaker_names"],0)
        self.assertEqual(report["original_caption_speaking_unit_denominator_unchanged"],751)
        for row in packets:
            self.assertEqual(row["first_candidate_voice_text"]+
                             row["second_candidate_voice_text"],
                             row["original_complete_source_cue_text"])
            self.assertIsNone(row["first_speaker_character_name"])
            self.assertIsNone(row["second_speaker_character_name"])
            self.assertFalse(row["source_switch_verified_by_original_soundtrack"])
        self.assertIsNone(packets[1]["source_original_timings_ms"])
        self.assertEqual(packets[0]["source_original_timings_ms"],{"start_ms":3000,"end_ms":5000})

    def test_original_text_change_causes_refusal(self):
        seed,witness=fixture()
        altered=copy.deepcopy(seed)
        altered["cues"][1]["split_before"]="An invented voice"
        with patch("triage_internal_speaker_switches.load_witness",side_effect=witness):
            with self.assertRaisesRegex(ValueError,"no unique split phrase"):
                validate(None,altered,strict=False)

    def test_no_duplicate_or_false_acceptance(self):
        seed,witness=fixture()
        altered=copy.deepcopy(seed)
        altered["cues"].append(copy.deepcopy(altered["cues"][0]))
        with patch("triage_internal_speaker_switches.load_witness",side_effect=witness):
            with self.assertRaisesRegex(ValueError,"duplicative"):
                validate(None,altered,strict=False)
        altered=copy.deepcopy(seed)
        altered["no_character_assigned"]=False
        with patch("triage_internal_speaker_switches.load_witness",side_effect=witness):
            with self.assertRaisesRegex(ValueError,"Untrusted"):
                validate(None,altered,strict=False)


if __name__=="__main__":
    unittest.main()
