"""Synthetic, no-source-media regressions for the single-pass episode finisher."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from episode_finish import make_packet, verify_decisions, verified_s09_candidate_locator, VIDEO_SHA, render_reviewed_screenplay, block_turn_segments, attach_source_audio_hints


class OnePassEpisodeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source_sha = "b" * 64
        script = self.root / "S01E01-working-screenplay.md"
        script.write_text("# S01E01\nSource SHA " + self.source_sha + "\n", encoding="utf-8")
        def row(i, group, name, t):
            return {
                "reading_block_id": "S01E01:speaker-evidence:%04d" % i,
                "original_source_part_refs": ["C%03d.1" % i],
                "source_sha256": self.source_sha,
                "display_group_id": group,
                "candidate_role": name,
                "actual_original_av_reviewer_accepted": False,
                "exact_rendered_caption_sha256": ("%064d" % i),
                "source_cue_times_not_subturn_times_ms": t,
            }
        self.rows = [row(1, 1, "LANA", [1000, 2000]),
                     row(2, 1, "LANA", [2100, 3000]),
                     row(3, 2, None, [3300, 4900])]
        self.provenance = self.root / "S01E01-working-screenplay-provenance.jsonl"
        self.save_rows()
        reader = self.root / "pilot-current-editorial-reader.jsonl"
        self.caption_text = ["one", "two", "three"]
        for i, row in enumerate(self.rows):
            row["exact_rendered_caption_sha256"] = hashlib.sha256(
                self.caption_text[i].encode("utf-8")).hexdigest()
        self.save_rows()
        reader.write_text("".join(json.dumps({
            "episode_id": "S01E01", "reading_block_id": row["reading_block_id"],
            "caption_text": self.caption_text[i],
            "original_source_sha256": self.source_sha,
            "original_source_part_refs": row["original_source_part_refs"]
        }) + "\n" for i, row in enumerate(self.rows)), encoding="utf-8")
        self.manifest = {
            "manuscript_sha256": {
                "S01E01": hashlib.sha256(script.read_bytes()).hexdigest()},
            "episode_editorial_integrations": {"S01E01": "single-current"},
            "episodes": {"S01E01": {"source_units": 3, "source_blocks": 3,
                                    "display_groups": 2}},
        }
        self.save_manifest()

    def save_rows(self):
        self.provenance.write_text(
            "".join(json.dumps(x) + "\n" for x in self.rows), encoding="utf-8")

    def save_manifest(self):
        (self.root / "working-screenplay-layout-manifest.json").write_text(
            json.dumps(self.manifest), encoding="utf-8")

    def test_review_once_all_source_parts_boundaries_and_roles(self):
        p = make_packet(self.root, "S01E01")
        self.assertEqual(p["source_reader_blocks"], 3)
        self.assertEqual(p["sequential_one_pass_batches"][0]["reader_blocks"][0]["source_exact_dialogue"], "one")
        self.assertEqual(p["original_source_speaking_part_refs"], 3)
        self.assertEqual(len(p["all_adjacent_boundary_questions"]), 2)
        self.assertEqual(p["all_adjacent_boundary_questions"][0]["priority"],
                         "P0_UNVERIFIED_JOIN")
        self.assertEqual(p["all_adjacent_boundary_questions"][1]["priority"],
                         "P0_UNVERIFIED_BREAK")
        self.assertEqual(p["review_passes_required"], 1)
        self.assertEqual(p["sequential_one_pass_batches"][0]["source_window_candidate_ms"],
                         [0, 6100])
        self.assertFalse(p["script_final_or_full_episode_accepted"])

    def test_provenance_and_original_audio_claims_cannot_be_forged(self):
        self.rows[0]["actual_original_av_reviewer_accepted"] = True
        self.save_rows()
        with self.assertRaisesRegex(ValueError, "Unproven previous"):
            make_packet(self.root, "S01E01")
        self.rows[0]["actual_original_av_reviewer_accepted"] = False
        self.rows[0]["source_sha256"] = "0" * 64
        self.save_rows()
        with self.assertRaisesRegex(ValueError, "source witness"):
            make_packet(self.root, "S01E01")

    def test_canonical_drift_fails_closed(self):
        self.manifest["episodes"]["S01E01"]["source_blocks"] = 2
        self.save_manifest()
        with self.assertRaisesRegex(ValueError, "row count"):
            make_packet(self.root, "S01E01")

    def test_no_blanket_audio_acceptance(self):
        p = make_packet(self.root, "S01E01")
        d = {
            "packet_sha256": p["packet_sha256"],
            "episode_id": "S01E01",
            "original_video_sha256": p["original_video_sha256_expected"],
            "review_method": "continuous_original_synchronized_av",
            "original_source_film_sha256_verified_in_browser": True,
            "original_media_sha256_computed_locally": p["original_video_sha256_expected"],
            "playback_edition_kind": "same_original_file",
            "reviewer": "Test fixture person",
            "boundaries": {},
            "roles": {},
            "batches": {},
        }
        with self.assertRaisesRegex(ValueError, "not fully reviewed"):
            verify_decisions(p, d)
        d["boundaries"] = {e["id"]: {"result": "same_speaker_continuation",
                                   "heard_on_original_audio": True}
                          for e in p["all_adjacent_boundary_questions"]}
        d["roles"] = {r["id"]: {"role": r["provisional_role"] or "UNIDENTIFIED VOICE",
                                  "original_audio_voice_reviewed": True,
                                  "intra_block_speaker_changes_reviewed": True}
                      for batch in p["sequential_one_pass_batches"]
                      for r in batch["reader_blocks"]}
        d["batches"] = {batch["id"]: {
            "synchronized_original_video_and_sound_reviewed": True,
            "observed_original_film_playback_seconds": 8.5,
            "performance_notes": [], "visible_props_and_wardrobe": [],
            "observed_actor_action_target": []}
                        for batch in p["sequential_one_pass_batches"]}
        self.assertTrue(verify_decisions(p, d)["editorial_decisions_complete"])
        d["boundaries"]["B0001"]["heard_on_original_audio"] = False
        with self.assertRaisesRegex(ValueError, "requires original sound"):
            verify_decisions(p, d)

    def test_no_av_acceptance_without_sha_verified_original_movie(self):
        p=make_packet(self.root,"S01E01")
        d={
            "packet_sha256":p["packet_sha256"],"episode_id":"S01E01",
            "original_video_sha256":p["original_video_sha256_expected"],
            "review_method":"continuous_original_synchronized_av","reviewer":"test fixture",
            "boundaries":{},"roles":{},"batches":{},
        }
        with self.assertRaisesRegex(ValueError,"source media SHA"):
            verify_decisions(p,d)
        d["original_source_film_sha256_verified_in_browser"]=True
        d["original_media_sha256_computed_locally"]="0"*64
        d["playback_edition_kind"]="viewer_supplied_proxy_source_equivalence_unverified"
        with self.assertRaisesRegex(ValueError,"source media SHA"):
            verify_decisions(p,d)

    def test_batch_playback_must_be_observed_not_merely_checked(self):
        p=make_packet(self.root,"S01E01")
        d={
            "packet_sha256":p["packet_sha256"],"episode_id":"S01E01",
            "original_video_sha256":p["original_video_sha256_expected"],
            "review_method":"continuous_original_synchronized_av",
            "original_source_film_sha256_verified_in_browser":True,
            "original_media_sha256_computed_locally":p["original_video_sha256_expected"],
            "playback_edition_kind":"same_original_file",
            "reviewer":"synthetic fixture",
            "boundaries":{e["id"]:{"result":"new_speaker","heard_on_original_audio":True}
                          for e in p["all_adjacent_boundary_questions"]},
            "roles":{row["id"]:{"role":row["provisional_role"] or "UNIDENTIFIED VOICE",
                                "original_audio_voice_reviewed":True,
                                "intra_block_speaker_changes_reviewed":True}
                      for group in p["sequential_one_pass_batches"] for row in group["reader_blocks"]},
            "batches":{p["sequential_one_pass_batches"][0]["id"]:{
               "synchronized_original_video_and_sound_reviewed":True,
               "observed_original_film_playback_seconds":0,
               "performance_notes":[],"visible_props_and_wardrobe":[],
               "observed_actor_action_target":[]
            }}
        }
        with self.assertRaisesRegex(ValueError,"picture coverage is incomplete"):
            verify_decisions(p,d)
        for value in d["batches"].values():value["observed_original_film_playback_seconds"]=8.1
        self.assertTrue(verify_decisions(p,d)["editorial_decisions_complete"])

    def test_source_exact_original_av_reviewed_script_render_after_all_decisions(self):
        p = make_packet(self.root, "S01E01")
        d = {
            "packet_sha256": p["packet_sha256"],
            "episode_id": "S01E01",
            "original_video_sha256": p["original_video_sha256_expected"],
            "review_method": "continuous_original_synchronized_av",
            "original_source_film_sha256_verified_in_browser": True,
            "original_media_sha256_computed_locally": p["original_video_sha256_expected"],
            "playback_edition_kind": "same_original_file",
            "reviewer": "synthetic fixture",
            "boundaries": {
                "B0001": {"result": "same_speaker_continuation",
                           "heard_on_original_audio": True},
                "B0002": {"result": "new_speaker",
                           "heard_on_original_audio": True}
            },
            "roles": {row["id"]: {
                "role": row["provisional_role"] or "UNIDENTIFIED VOICE",
                "original_audio_voice_reviewed": True,
                "intra_block_speaker_changes_reviewed": True
            } for batch in p["sequential_one_pass_batches"]
              for row in batch["reader_blocks"]},
            "batches": {p["sequential_one_pass_batches"][0]["id"]: {
                "synchronized_original_video_and_sound_reviewed": True,
            "observed_original_film_playback_seconds": 8.5,
                "performance_notes": ["test delivery"], "visible_props_and_wardrobe": [],
                "observed_actor_action_target": ["test observed action"]
            }}
        }
        script = render_reviewed_screenplay(p, d)
        self.assertEqual(script.count("### LANA"), 1)
        self.assertEqual(script.count("### UNIDENTIFIED VOICE"), 1)
        self.assertLess(script.index("    one"), script.index("    two"))
        self.assertLess(script.index("    two"), script.index("    three"))
        self.assertIn(self.source_sha, script)
        self.assertIn("test observed action", script)
        d["boundaries"]["B0002"]["result"] = "same_speaker_continuation"
        with self.assertRaisesRegex(ValueError, "conflicting P1"):
            render_reviewed_screenplay(p, d)

    def test_p0_inside_one_caption_real_character_switch(self):
        p = make_packet(self.root, "S01E01")
        d = {
            "packet_sha256": p["packet_sha256"], "episode_id": "S01E01",
            "original_video_sha256": p["original_video_sha256_expected"],
            "review_method": "continuous_original_synchronized_av",
            "original_source_film_sha256_verified_in_browser": True,
            "original_media_sha256_computed_locally": p["original_video_sha256_expected"],
            "playback_edition_kind": "same_original_file",
            "reviewer": "synthetic fixture",
            "boundaries": {
                "B0001": {"result": "same_speaker_continuation", "heard_on_original_audio": True},
                "B0002": {"result": "new_speaker", "heard_on_original_audio": True},
            },
            "roles": {row["id"]: {
                "role": row["provisional_role"] or "UNIDENTIFIED VOICE",
                "original_audio_voice_reviewed": True,
                "intra_block_speaker_changes_reviewed": True,
            } for b in p["sequential_one_pass_batches"] for row in b["reader_blocks"]},
            "batches": {p["sequential_one_pass_batches"][0]["id"]: {
                "synchronized_original_video_and_sound_reviewed": True,
            "observed_original_film_playback_seconds": 8.5,
                "performance_notes": [], "visible_props_and_wardrobe": [],
                "observed_actor_action_target": []
            }},
        }
        second = p["sequential_one_pass_batches"][0]["reader_blocks"][1]
        d["roles"][second["id"]]["segments"] = [
            {"start": 0, "end": 1, "role": "LANA"},
            {"start": 1, "end": 3, "role": "DAN"},
        ]
        self.assertTrue(verify_decisions(p, d)["editorial_decisions_complete"])
        output = render_reviewed_screenplay(p, d)
        self.assertEqual(output.count("### LANA"), 1)
        self.assertEqual(output.count("### DAN"), 1)
        self.assertIn("    t\n", output)
        self.assertIn("    wo\n", output)
        self.assertLess(output.index("    t\n"), output.index("    wo\n"))
        d["roles"][second["id"]]["segments"][1]["start"] = 2
        with self.assertRaisesRegex(ValueError, "lost, overlapped"):
            verify_decisions(p, d)
        d["roles"][second["id"]]["segments"][1]["start"] = 1
        d["roles"][second["id"]]["segments"][1]["role"] = "LANA"
        with self.assertRaisesRegex(ValueError, "redundant split"):
            verify_decisions(p, d)
        d["roles"][second["id"]].pop("segments")
        d["roles"][second["id"]].pop("intra_block_speaker_changes_reviewed")
        with self.assertRaisesRegex(ValueError, "within-caption"):
            verify_decisions(p, d)

    def test_unicode_codepoint_slices_do_not_mutate_source(self):
        original = "Hey🙂 there!\nYeah."
        row = {"source_exact_dialogue": original,
               "source_dialogue_sha256": hashlib.sha256(original.encode()).hexdigest()}
        initial = {"role": "LANA", "intra_block_speaker_changes_reviewed": True,
                   "segments": [
                       {"start": 0, "end": 12, "role": "LANA"},
                       {"start": 12, "end": len(original), "role": "DAN"}
                   ]}
        pieces = block_turn_segments(row, initial)
        self.assertEqual("".join(original[v["start"]:v["end"]] for v in pieces), original)
        self.assertEqual(pieces[0]["end"], 12)
        initial["segments"][1]["end"] -= 1
        with self.assertRaisesRegex(ValueError, "incomplete"):
            block_turn_segments(row, initial)


    def test_original_film_acoustic_hint_is_unverified_and_source_pinned(self):
        packet=make_packet(self.root,"S01E01")
        report={
            "schema":"night-court-canonical-original-audio-p0-p1-evidence/1",
            "episode_id":"S01E01",
            "original_video_sha256":packet["original_video_sha256_expected"],
            "immutable_original_dialogue_sha256":packet["source_original_dialogue_sha256"],
            "canonical_manuscript_sha256":packet["canonical_manuscript_sha256"],
            "source_pcm_sha256":"a"*64,
            "voice_embedding_windows_usable":15,
            "original_video_watched_by_human":False,
            "independent_original_actor_voice_accepted":0,
            "independent_performed_turns_accepted":0,
            "model_diary_not_film_truth":True,
            "media_audio_pcm_embedding_vectors_or_credentials_preserved":False,
            "unknown_original_soundtrack_proposals":[{
                "source_reading_block_id":"S01E01:speaker-evidence:0003",
                "source_ref":"C003.1",
                "actor_voice_original_soundtrack_independently_verified":False,
                "acoustic_candidate":"LANA",
                "uncertified_best_role":"LANA",
                "speaker_similarity":0.83,
                "global_and_role_holdout_pass":True
            }],
            "adjacent_P0_original_audio_voice_similarity":[{
                "source_left":"S01E01:speaker-evidence:0001",
                "source_right":"S01E01:speaker-evidence:0002",
                "machine_acoustic_voice_similarity":.91,
                "source_audio_p0_performed_boundary_independently_verified":False,
                "provisional_display_join":True
            }]
        }
        report["adjacent_P0_original_audio_voice_similarity"].append({
            "source_left":"S01E01:speaker-evidence:0002",
            "source_right":"S01E01:speaker-evidence:0003",
            "machine_acoustic_voice_similarity":0.86,
            "source_audio_p0_performed_boundary_independently_verified":False,
            "provisional_display_join":False
        })
        report["provisional_named_voice_holdout"]={
            "provisional_role_holdout_counts":{
                "LANA":{"correct_held_out":2,"evaluated":6}
            }
        }
        path=self.root/"acoustic.json"
        path.write_text(json.dumps(report),encoding="utf-8")
        attach_source_audio_hints(packet,path)
        rows=packet["sequential_one_pass_batches"][0]["reader_blocks"]
        self.assertIsNone(rows[-1]["provisional_role"])
        self.assertEqual(rows[-1]["original_audio_model_uncertified_role_hint"]["role_candidate"],"LANA")
        self.assertFalse(packet["all_adjacent_boundary_questions"][0]["machine_audio_p0_boundary_verified"])
        self.assertEqual(packet["machine_audio_hints_attached"]["p0_adjacent_audio_pairs"],2)
        self.assertEqual(packet["machine_audio_hints_attached"]["p0_acoustic_replay_priority_count"],1)
        self.assertEqual(packet["machine_audio_hints_attached"]["p1_low_holdout_provisional_roles"],1)
        self.assertEqual(packet["machine_audio_review_priorities"][0]["boundary_id"],"B0002")
        self.assertEqual(packet["all_adjacent_boundary_questions"][1]["original_audio_machine_review_priority"],
                         "strong_acoustic_similarity_across_proposed_break")
        self.assertEqual(rows[0]["original_audio_provisional_role_holdout_warning"]["correct_held_out"],2)
        report["independent_original_actor_voice_accepted"]=1
        path.write_text(json.dumps(report),encoding="utf-8")
        with self.assertRaisesRegex(ValueError,"nonacceptance"):
            attach_source_audio_hints(make_packet(self.root,"S01E01"),path)
        report["independent_original_actor_voice_accepted"]=0
        report["canonical_manuscript_sha256"]="f"*64
        path.write_text(json.dumps(report),encoding="utf-8")
        with self.assertRaisesRegex(ValueError,"source"):
            attach_source_audio_hints(make_packet(self.root,"S01E01"),path)

    def test_s09_original_machine_locator_has_no_faked_subtitle_times(self):
        path = self.root / "s09-source-audio.json"
        rows = [{
            "original_paragraph_id": n,
            "candidate_original_audio_window_ms": [n * 1000, n * 1000 + 900],
            "original_paragraph_timecode_ms": None,
            "original_film_audio_timing_independently_verified": False,
            "spoken_character_identity_verified": False
        } for n in range(1, 232)]
        data = {
            "schema": "night-court-s09-original-film-untimed-paragraph-audio-locator/1",
            "episode_id": "S09E19",
            "original_video_sha256": VIDEO_SHA["S09E19"],
            "original_untimed_source_sha256":
                "659beb9c50fabdd1028aac9570999d9a16b36e6d582938e10809cc0c664530b2",
            "original_source_untimed_paragraph_count": 347,
            "original_soundtrack_processed": True,
            "original_speaker_identities_verified": 0,
            "candidate_source_paragraphs_given_audio_window": 231,
            "matches": rows
        }
        path.write_text(json.dumps(data), encoding="utf-8")
        hints, digest = verified_s09_candidate_locator(path)
        self.assertEqual(len(hints), 231)
        self.assertEqual(hints[12], [12000, 12900])
        self.assertEqual(len(digest), 64)
        data["matches"][2]["original_paragraph_timecode_ms"] = 3000
        path.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Fake original S09 paragraph timing"):
            verified_s09_candidate_locator(path)



if __name__ == "__main__":
    unittest.main()
