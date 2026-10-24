#!/usr/bin/env python3
"""Synthetic original-listening calibration and correlated-model-error tests."""
import copy
import unittest
from calibrate_original_asr_truth import calibrate,edits,words


def fixture():
    original="a"*64
    cases=[("C1",[1000,2200],"Did you say mercurial?"),
           ("C2",[2500,4800],"A flying pickle!"),
           ("C3",[5200,7800],"Where is Harry?")]
    gold={"schema":"night-court-original-source-listened-dialogue-gold/1",
          "original_video_sha256":original,
          "cases":[{"case_id":case,"source_interval_ms":interval,
                    "verified_original_text":text,
                    "original_audio_independently_listened":True,
                    "reviewer_attested_original_words":True}
                    for case,interval,text in cases]}
    models={"schema":"night-court-original-model-calibration-proposals/1",
            "original_video_sha256":original,"models":[]}
    for name,family,statements in [
        ("model_a","whisper",["Did you say mercurial?","A flying nickel!","Where is Harry?"]),
        ("model_b","kaldi_hmm_wfst",["Did you say mercurial?","A flying nickel!","Where was Harry?"])]:
        models["models"].append({
          "model_id":name,"architecture_family":family,
          "original_subtitle_or_other_decoder_prompt_used":False,
          "cases":[{"case_id":case,"source_interval_ms":interval,
                    "model_hypothesis_text":text}
                    for (case,interval,_),text in zip(cases,statements)]})
    return gold,models


class ASRCalibration(unittest.TestCase):
    def test_word_error_and_shared_wrong_agreement(self):
        gold,proposals=fixture()
        output=calibrate(gold,proposals)
        self.assertEqual(output["independently_listened_windows"],3)
        self.assertEqual(output["first_two_models_agree_windows"],2)
        self.assertEqual(output["two_models_jointly_wrong_when_agree_windows"],1)
        self.assertEqual(output["agreement_joint_error_fraction"],.5)
        self.assertEqual(output["models"][0]["word_edit_errors"],1)
        self.assertEqual(output["models"][1]["word_edit_errors"],2)
        self.assertFalse(output["whole_episode_or_speaker_identity_accepted"])

    def test_alignment_and_tokenization(self):
        self.assertEqual(words("Mercurial!  Isn't it?"),["mercurial","isn't","it"])
        self.assertEqual(edits(["a","b","c"],["a","d"]),2)

    def test_model_prompt_or_false_original_review_is_rejected(self):
        for fault in ("unheard","prompted","sha","wrong_interval","same_family","duplicate"):
            gold,models=fixture()
            if fault=="unheard":gold["cases"][0]["original_audio_independently_listened"]=False
            if fault=="prompted":models["models"][0]["original_subtitle_or_other_decoder_prompt_used"]=True
            if fault=="sha":models["original_video_sha256"]="f"*64
            if fault=="wrong_interval":models["models"][0]["cases"][0]["source_interval_ms"]=[999,2200]
            if fault=="same_family":models["models"][1]["architecture_family"]="whisper"
            if fault=="duplicate":models["models"][0]["cases"][1]["case_id"]="C1"
            with self.subTest(fault=fault),self.assertRaises(ValueError):
                calibrate(gold,models)


if __name__=="__main__":
    unittest.main()
