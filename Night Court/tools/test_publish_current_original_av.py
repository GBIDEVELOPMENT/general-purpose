"""No fake source AV acceptance: exercise stable final-script promotion gates."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from publish_current_original_av import (
    process,independent_sample,sha,SCHEMA,INDEPENDENT_SCHEMA,ROOT,
)


class ReviewedPublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root=Path(self.temp.name)
        self.review=root/"review"
        self.destination=root/"output"
        self.review.mkdir()
        self.snapshot=ROOT/"saved-private/pilot-current"

    def put(self,ep,content):
        (self.review/(ep+"-original-av-decisions.json")).write_text(
            json.dumps(content),encoding="utf-8")

    def test_missing_and_partial_edits_are_not_published(self):
        self.assertEqual(process("S01E01",self.snapshot,self.review,self.destination,True)["status"],
                         "no_original_av_decisions")
        self.put("S01E01",{
            "episode_id":"S01E01",
            "original_source_full_episode_complete":False,
            "boundaries":{"B0001":{"result":"new_speaker"}},
        })
        result=process("S01E01",self.snapshot,self.review,self.destination,True)
        self.assertEqual(result["status"],"partial_unaccepted_review")
        self.assertFalse(result["published"])
        self.assertFalse(self.destination.exists())

    def test_claimed_complete_without_original_film_is_rejected(self):
        self.put("S01E01",{
            "episode_id":"S01E01",
            "original_source_full_episode_complete":True,
            "reviewer":"Unverified placeholder",
        })
        with self.assertRaisesRegex(ValueError,"Missing reviewer, source media SHA|matching packet"):
            process("S01E01",self.snapshot,self.review,self.destination,True)
        self.assertFalse(self.destination.exists())

    def test_cross_episode_ledger_does_not_publish(self):
        self.put("S01E01",{"episode_id":"S09E19","original_source_full_episode_complete":True})
        with self.assertRaisesRegex(ValueError,"Wrong original source episode"):
            process("S01E01",self.snapshot,self.review,self.destination,True)

    def test_validated_gate_renders_one_stable_name_with_no_independent_claim(self):
        mockpacket={"episode_id":"S01E01","original_video_sha256_expected":"a"*64,
          "source_original_dialogue_sha256":"b"*64,
          "canonical_manuscript_sha256":"c"*64,
          "packet_sha256":"d"*64,
          "source_reader_blocks":2,"original_source_speaking_part_refs":2,
          "sequential_one_pass_batches":[{"reader_blocks":[
            {"id":"S01E01:1"},{"id":"S01E01:2"}]}]}
        self.put("S01E01",{"episode_id":"S01E01",
             "original_source_full_episode_complete":True,"reviewer":"Original-viewer"})
        script=("Original immutable dialogue SHA-256: "+"b"*64+"\n").encode()
        with mock.patch("publish_current_original_av.make_packet",return_value=mockpacket),\
             mock.patch("publish_current_original_av.verify_decisions",return_value={
               "editorial_decisions_complete":True,
               "original_film_playback_coverage":{"source_playback_coverage_fraction":1.0}}),\
             mock.patch("publish_current_original_av.render_reviewed_screenplay",
                         return_value=script.decode()):
            result=process("S01E01",self.snapshot,self.review,self.destination,True)
        self.assertTrue(result["published"])
        self.assertEqual(result["independent_sample"],"pending_independent_editorial_spotcheck")
        manuscript=self.destination/"S01E01-original-av-reviewed-screenplay.md"
        metadata=json.loads((self.destination/"S01E01-original-av-reviewed-manifest.json").read_text())
        self.assertEqual(manuscript.read_bytes(),script)
        self.assertEqual(metadata["reviewed_manuscript_sha256"],sha(script))
        self.assertEqual(metadata["schema"],SCHEMA)
        self.assertTrue(metadata["software_does_not_prove_human_attention"])
        self.assertTrue(metadata["canonical_provisional_pilot_current_not_overwritten"])

    def test_independent_sample_requires_a_second_real_editor(self):
        packet={"episode_id":"S01E01","original_video_sha256_expected":"a"*64,
                "packet_sha256":"b"*64,
                "sequential_one_pass_batches":[{"reader_blocks":[
                   {"id":f"source-{i}"} for i in range(15)]}]}
        ledger={"reviewer":"Lead editor"}
        sample={"schema":INDEPENDENT_SCHEMA,"episode_id":"S01E01",
                "source_video_sha256":"a"*64,"source_packet_sha256":"b"*64,
                "decision_ledger_sha256":sha(json.dumps(
                  ledger,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()),
                "source_exact_rendered_screenplay_sha256":sha(b"script"),
                "independent_editor":"Lead editor",
                "original_audio_and_picture_spotchecked":True,
                "P0_P1_contradictions_remaining":0,
                "accepted":True,
                "sampled_original_reading_block_ids":[f"source-{i}" for i in (0,1,2,5,6,7,10,11,12)]}
        report=self.review/"sample.json"
        report.write_text(json.dumps(sample))
        with self.assertRaisesRegex(ValueError,"not independent"):
            independent_sample(packet,ledger,b"script",report)
        sample["independent_editor"]="Separate sample editor"
        report.write_text(json.dumps(sample))
        result=independent_sample(packet,ledger,b"script",report)
        self.assertEqual(result["status"],"independent_editor_spotcheck_attested")


if __name__=="__main__":
    unittest.main()
