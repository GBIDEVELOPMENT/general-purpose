"""Regression tests for one-command source-exact private screenplay delivery."""
import json
import tempfile
import unittest
from pathlib import Path

from script_factory import (
    ROOT, PILOTS, construct, multi_voice_typography, run,
    source_index, source_role, source_rows, sha, contextual_role_overlay, structural_speaker_parts,
    source_syntactic_continuation,
)


class ScriptFactoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = source_index(ROOT)

    def test_grammar_p0_is_timing_limited_and_abstains_on_dashed_cues(self):
        paired = "matched_ellipsis_source_continuation_unverified"
        lower = "lowercase_unfinished_sentence_continuation_unverified"
        self.assertEqual(source_syntactic_continuation(
            "Nobody knows...", "...in the court.", 174), paired)
        self.assertEqual(source_syntactic_continuation(
            "you must turn to the", "other side.", 210), lower)
        self.assertIsNone(source_syntactic_continuation(
            "Nobody knows...", "...in the court.", None))  # untimed S09
        self.assertIsNone(source_syntactic_continuation(
            "Nobody knows...", "...in the court.", 1601))
        self.assertIsNone(source_syntactic_continuation(
            "you must turn to the", "other side.", 901))
        self.assertIsNone(source_syntactic_continuation(
            "That's right.", "other side.", 200))
        self.assertIsNone(source_syntactic_continuation(
            "You're sure...", "...some explanation.\n- I doubt it.", 200))
        self.assertIsNone(source_syntactic_continuation(
            "- This is one voice.\n- This is another...", "...the next.", 200))
        self.assertIsNone(source_syntactic_continuation(
            "And he said,", "- Yes, yes.", 50))
        self.assertIsNone(source_syntactic_continuation(
            "I tell you the", "rest.", -1001))

    def test_grammar_p0_agrees_with_existing_original_pilot_turns_and_s05_context(self):
        # Ground truth here is the provisional *independently edited*
        # reference reading, not original soundtrack verified truth.
        # Calibrate proposals, never claim an accepted performed turn.
        import re
        reference = [
            json.loads(line) for line in
            (ROOT / "saved-private/pilot-current/pilot-current-editorial-reader.jsonl")
            .read_text("utf-8").splitlines() if line.strip()
        ]
        source_roles = {}
        for block in reference:
            if block["episode_id"] != "S01E01":
                continue
            for ref in block["original_source_part_refs"]:
                m = re.fullmatch(r"C(\d+)\.(\d+)", ref)
                if m:
                    source_roles.setdefault(int(m.group(1)), []).append(
                        (int(m.group(2)), block["candidate_role"]))
        _, _, captions = source_rows(ROOT, self.index["S01E01"])
        matched = 0
        for prev, nxt in zip(captions, captions[1:]):
            basis = source_syntactic_continuation(
                prev["text"], nxt["text"], nxt["start_ms"] - prev["end_ms"])
            if not basis:
                continue
            left = sorted(source_roles[prev["cue"]])[-1][1]
            right = sorted(source_roles[nxt["cue"]])[0][1]
            self.assertTrue(left and right)
            self.assertEqual(left, right, (prev["cue"], nxt["cue"], basis))
            matched += 1
        self.assertEqual(matched, 34)  # 34/34 safe explicit S01 source pairs

        _, _, captions = source_rows(ROOT, self.index["S05E05"])
        source = json.loads((ROOT / "seasons/S05/S05E05/derived" /
                             "text-only-speaker-proposals-v2.json").read_text("utf-8"))
        names = {x["source_unit_index"]: x.get("proposed_speaker")
                 for x in source["records"]}
        confirmed, observed = 0, 0
        for prev, nxt in zip(captions, captions[1:]):
            basis = source_syntactic_continuation(
                prev["text"], nxt["text"], nxt["start_ms"] - prev["end_ms"])
            if not basis:
                continue
            observed += 1
            left, right = names.get(prev["cue"]), names.get(nxt["cue"])
            if left and right:
                confirmed += 1
                self.assertEqual(left, right, (prev["cue"], nxt["cue"], basis))
        self.assertEqual(confirmed, 22)
        self.assertGreaterEqual(observed, confirmed)

    def test_s01e03_contextual_script_covers_all_385_exact_original_cues(self):
        ep = "S01E03"
        witness, _, cues = source_rows(ROOT, self.index[ep])
        files, manifest = construct(ROOT, ep, self.index[ep])
        report = manifest["contextual_overlay"]
        self.assertEqual(manifest["evidence_tier"], "contextual_provisional_reading_draft")
        self.assertEqual(manifest["source_units"], 385)
        self.assertEqual(report["high_medium_single_role_hypotheses"], 307)
        self.assertEqual(report["mixed_voice_internal_review_cues"], 76)
        self.assertEqual(report["weak_or_abstained_cues"], 2)
        self.assertEqual(report["exact_contextual_internal_handoffs"], 76)
        self.assertEqual(report["unlocated_contextual_internal_handoffs"], 0)
        self.assertEqual(report["text_only_performance_tone_hypotheses"], 88)
        self.assertEqual(manifest["unknown_label_cues"], 78)
        self.assertEqual(manifest["source_contextual_exact_p0_boundaries"], 76)
        self.assertEqual(manifest["contextual_provisional_named_parts"], 152)
        self.assertEqual(manifest["text_only_contextual_delivery_proposals"], 88)
        self.assertFalse(manifest["original_audio_performed_delivery_accepted"])
        self.assertFalse(manifest["actual_av_verified"])
        rows = [json.loads(s) for s in files["provenance.jsonl"].splitlines()]
        queue = json.loads(files["review-queue.json"])
        self.assertEqual(len(rows), len(cues))
        self.assertEqual([row["source_text"] for row in rows], [x["text"] for x in cues])
        self.assertEqual([row["source_start_ms"] for row in rows], [x["start_ms"] for x in cues])
        self.assertEqual([row["source_end_ms"] for row in rows], [x["end_ms"] for x in cues])
        self.assertTrue(all(row["original_dialogue_sha256"] == witness["sha256"]
                            for row in rows))
        self.assertEqual(len(queue["boundary_review_questions"]), 384)
        self.assertEqual(len(queue["textual_delivery_p2_review"]), 88)
        self.assertEqual(len(queue["contextual_role_review"]), 385)
        self.assertEqual(sum(r["contextual_confidence"] == "abstain" for r in rows), 2)
        for n, role in ((43, "Al Craven"), (44, "Dan Fielding"),
                        (45, "Lana Wagner"), (61, "Liz Williams"),
                        (72, "Harry Stone"), (249, "Harry Stone"),
                        (74, None), (77, "Lana Wagner"),
                        (177, "Harry Stone"), (178, "Dan Fielding"),
                        (180, "Dan Fielding"), (221, "Dan Fielding"),
                        (222, "Dan Fielding"), (223, "Harry Stone"),
                        (225, "Harry Stone"), (226, "Dan Fielding"),
                        (228, "Dan Fielding"), (385, "Harry Stone")):
            with self.subTest(cue=n):
                self.assertEqual(rows[n-1]["candidate_display_role"], role)
                self.assertFalse(rows[n-1]["candidate_role_original_soundtrack_verified"])
        for n, roles in ((67, ["Harry Stone", "Dan Fielding"]),
                         (68, ["Harry Stone", "Dan Fielding"]),
                         (74, ["Harry Stone", "Lana Wagner"]),
                         (75, ["Harry Stone", "Ronald McKenzie"]),
                         (76, ["Vickie Guyer", "Harry Stone"]),
                         (232, ["Harry Stone", "Lana Wagner"]),
                         (237, ["Al Craven", "Harry Stone"]),
                         (314, ["Ronald McKenzie", "Harry Stone"])):
            row = rows[n-1]
            with self.subTest(handoff=n):
                self.assertEqual([p["provisional_part_role"] for p in
                                  row["source_speaker_parts"]], roles)
                self.assertEqual(row["contextual_unicode_split_offsets"],
                                 [row["source_text"].index("\n- ") + 1])
                self.assertTrue(all(not p["original_audio_boundary_verified"]
                                    and p["original_audio_subcue_time_ms"] is None
                                    for p in row["source_speaker_parts"]))
                self.assertEqual("".join(
                    row["source_text"][p["source_character_start"]:p["source_character_end"]]
                    for p in row["source_speaker_parts"]), row["source_text"])
        self.assertTrue(all(not t["original_audio_tone_verified"]
                            and not t["eligible_for_performed_stage_direction"]
                            for t in queue["textual_delivery_p2_review"]))
        self.assertEqual(files["screenplay.md"].count("Textual delivery hypothesis:"), 88)
        self.assertIn("NOT AV-CERTIFIED", files["screenplay.md"])

    def test_s01e02_full_contextual_reader_source_exact_and_no_false_av(self):
        ep = "S01E02"
        witness, _, captions = source_rows(ROOT, self.index[ep])
        files, manifest = construct(ROOT, ep, self.index[ep])
        report = manifest["contextual_overlay"]
        self.assertEqual(manifest["evidence_tier"], "contextual_provisional_reading_draft")
        self.assertEqual(manifest["source_units"], 380)
        self.assertEqual(report["high_medium_single_role_hypotheses"], 293)
        self.assertEqual(report["mixed_voice_internal_review_cues"], 72)
        self.assertEqual(report["weak_or_abstained_cues"], 15)
        self.assertEqual(report["exact_contextual_internal_handoffs"], 72)
        self.assertEqual(report["unlocated_contextual_internal_handoffs"], 0)
        self.assertEqual(manifest["unknown_label_cues"], 87)  # 72 mixed + 15 abstain
        self.assertEqual(manifest["contextual_provisional_named_parts"], 144)
        self.assertFalse(manifest["actual_av_verified"])
        rows = [json.loads(s) for s in files["provenance.jsonl"].splitlines()]
        queue = json.loads(files["review-queue.json"])
        self.assertEqual(len(rows), len(captions))
        self.assertEqual([x["source_text"] for x in rows], [x["text"] for x in captions])
        self.assertEqual([x["source_start_ms"] for x in rows],
                         [x["start_ms"] for x in captions])
        self.assertEqual([x["source_end_ms"] for x in rows],
                         [x["end_ms"] for x in captions])
        self.assertTrue(all(x["original_dialogue_sha256"] == witness["sha256"]
                            for x in rows))
        self.assertEqual(len(queue["contextual_role_review"]), 380)
        self.assertEqual(len(queue["boundary_review_questions"]), 379)
        self.assertEqual(len(queue["within_cue_structural_turn_questions"]),
                         manifest["source_dash_candidate_p0_boundaries"] + 72)
        for cue, speaker in ((112, "Eddie Simms"), (113, "Dan Fielding"),
                             (180, "Harry Stone"), (234, "Dan Fielding"),
                             (331, "Santa / John Stevens"), (364, "Lana Wagner"),
                             (367, "Liz Williams"), (371, "Bull Shannon"),
                             (372, "Dan Fielding")):
            with self.subTest(cue=cue):
                self.assertEqual(rows[cue-1]["candidate_display_role"], speaker)
                self.assertFalse(rows[cue-1]["candidate_role_original_soundtrack_verified"])
        for cue, expected in (
            (1, ["Dan Fielding", "Liz Williams"]),
            (198, ["Lana Wagner", "Harry Stone"]),
            (285, ["Eddie Simms", "Doctor Peter Green"]),
            (313, ["Eddie Simms", "Bull Shannon"]),
            (319, ["Eddie Simms", "Harry Stone"]),
            (349, ["Eddie Simms", "Santa / John Stevens"]),
        ):
            row = rows[cue-1]
            parts = row["source_speaker_parts"]
            with self.subTest(mixed_cue=cue):
                self.assertEqual([p["provisional_part_role"] for p in parts], expected)
                self.assertEqual([p["source_character_start"] for p in parts[1:]],
                                 row["contextual_unicode_split_offsets"])
                self.assertTrue(all(not p["original_audio_boundary_verified"]
                                    and p["original_audio_subcue_time_ms"] is None
                                    for p in parts))
                self.assertEqual(
                    "".join(row["source_text"][p["source_character_start"]:
                                                p["source_character_end"]] for p in parts),
                    row["source_text"])
        # C349 has only ONE dash in the second voice. A literal source-exact
        # editorial offset detects the real P0 risk that basic multiple-dash
        # typography alone cannot detect.
        self.assertEqual(rows[348]["contextual_unicode_split_offsets"], [29])
        self.assertIsNone(rows[348]["candidate_display_role"])
        self.assertIn("NOT AV-CERTIFIED", files["screenplay.md"])

    def test_s01e02_source_text_only_p2_delivery_is_reviewable_not_acting_truth(self):
        ep = "S01E02"
        files, manifest = construct(ROOT, ep, self.index[ep])
        rows = [json.loads(s) for s in files["provenance.jsonl"].splitlines()]
        queue = json.loads(files["review-queue.json"])
        self.assertEqual(manifest["contextual_overlay"]["text_only_performance_tone_hypotheses"], 64)
        self.assertFalse(manifest["contextual_overlay"]["any_performed_tone_original_audio_verified"])
        self.assertEqual(manifest["text_only_contextual_delivery_proposals"], 64)
        self.assertFalse(manifest["original_audio_performed_delivery_accepted"])
        proposed = [r for r in rows if r["contextual_textual_tone"]]
        self.assertEqual(len(proposed), 64)
        self.assertEqual(len(queue["textual_delivery_p2_review"]), 64)
        for row in proposed:
            self.assertIsNotNone(row["candidate_display_role"])
            self.assertEqual(len(row["source_speaker_parts"]), 1)
            self.assertFalse(row["performed_tone_original_soundtrack_verified"])
            self.assertTrue(len(row["contextual_textual_tone_basis"]) >= 12)
        self.assertTrue(all(not r["original_audio_tone_verified"]
                            and not r["eligible_for_performed_stage_direction"]
                            for r in queue["textual_delivery_p2_review"]))
        for cue, expected in ((4, "playful"), (15, "exasperated"),
                              (113, "sarcastic"), (286, "hesitant"),
                              (330, "contrite"), (380, "exasperated")):
            self.assertEqual(rows[cue-1]["contextual_textual_tone"], expected)
        self.assertEqual(files["screenplay.md"].count("Textual delivery hypothesis:"), 64)
        self.assertIn("original performance unverified", files["screenplay.md"])
        self.assertFalse(manifest["actual_av_verified"])

    def test_source_textual_tone_rejects_forged_performed_truth_and_mixed_voice(self):
        from script_factory import contextual_role_overlay
        ep = "S01E02"
        manifest, _, captions = source_rows(ROOT, self.index[ep])
        original = json.loads((ROOT / "seasons/S01/S01E02/derived" /
                               "text-only-speaker-proposals-v1.json").read_text("utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "seasons/S01/S01E02/derived"
            folder.mkdir(parents=True)
            dest = folder / "text-only-speaker-proposals-v1.json"
            for change in (
                {"original_soundtrack_verified": True},
                {"tone": "film-confirmed-crying"},
                {"basis": ""},
            ):
                with self.subTest(change=change):
                    forged = json.loads(json.dumps(original))
                    forged["records"][3]["provisional_delivery"].update(change)
                    dest.write_text(json.dumps(forged), encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, "contextual delivery"):
                        contextual_role_overlay(Path(tmp), ep, manifest, captions)
            forged = json.loads(json.dumps(original))
            forged["records"][0]["provisional_delivery"] = {
                "tone": "sarcastic", "basis": "Two distinct source speakers cannot share cue tone.",
                "original_soundtrack_verified": False,
            }
            dest.write_text(json.dumps(forged), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "contextual delivery"):
                contextual_role_overlay(Path(tmp), ep, manifest, captions)

    def test_syntax_role_conflicts_are_source_bound_review_not_auto_renaming(self):
        from unittest.mock import patch
        ep = "S01E02"
        source, _, cues = source_rows(ROOT, self.index[ep])
        actual_overlay, report = contextual_role_overlay(ROOT, ep, source, cues)
        # Independent source text contains C32 -> C33:
        # "Security guards at Redfield's department store..." ->
        # "...found him and a couple of other derelicts..."
        # Both originally have Dan as the provisional speaker.
        self.assertEqual(actual_overlay[32]["provisional_role"], "Dan Fielding")
        self.assertEqual(actual_overlay[33]["provisional_role"], "Dan Fielding")
        fake = {cue: dict(hint) for cue, hint in actual_overlay.items()}
        fake[33]["provisional_role"] = "Harry Stone"
        fake[33]["basis"] = "Deliberately forged conflicting P1 reader for regression"
        with patch("script_factory.contextual_role_overlay", return_value=(fake, report)):
            files, manifest = construct(ROOT, ep, self.index[ep])
        queue = json.loads(files["review-queue.json"])
        rows = [json.loads(x) for x in files["provenance.jsonl"].splitlines()]
        conflicts = queue["source_syntactic_role_conflict_focus"]
        self.assertEqual(manifest["source_syntactic_p0_role_conflicts"], 1)
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0]["between_cues"], [32, 33])
        self.assertEqual(conflicts[0]["left_provisional_role"], "Dan Fielding")
        self.assertEqual(conflicts[0]["right_provisional_role"], "Harry Stone")
        self.assertEqual(conflicts[0]["review_priority"], "P0_P1_GRAMMAR_ROLE_CONFLICT")
        self.assertFalse(conflicts[0]["original_audio_performed_boundary_verified"])
        self.assertFalse(rows[32]["provisional_continuation_of_previous"])
        self.assertTrue(rows[32]["source_syntactic_role_conflict_before_cue"])
        self.assertEqual([r["source_text"] for r in rows], [c["text"] for c in cues])
        self.assertFalse(manifest["actual_av_verified"])

        # Ordinary real editorial data is not silently rewritten or accepted.
        originals, accepted = construct(ROOT, ep, self.index[ep])
        self.assertEqual(accepted["source_syntactic_p0_role_conflicts"], 0)
        self.assertEqual(json.loads(originals["review-queue.json"])[
            "source_syntactic_role_conflict_focus"], [])

    def test_s01e04_contextual_speaker_p0_and_p2_source_exact(self):
        episode = "S01E04"
        files, meta = construct(ROOT, episode, self.index[episode])
        source_manifest, _, source = source_rows(ROOT, self.index[episode])
        self.assertEqual(meta["evidence_tier"], "contextual_provisional_reading_draft")
        self.assertEqual(meta["source_units"], 354)
        ctx = meta["contextual_overlay"]
        self.assertEqual(ctx["high_medium_single_role_hypotheses"], 301)
        self.assertEqual(ctx["mixed_voice_internal_review_cues"], 45)
        self.assertEqual(ctx["exact_contextual_internal_handoffs"], 45)
        self.assertEqual(ctx["unlocated_contextual_internal_handoffs"], 0)
        self.assertEqual(ctx["weak_or_abstained_cues"], 8)
        self.assertEqual(ctx["text_only_performance_tone_hypotheses"], 86)
        self.assertEqual(meta["text_only_contextual_delivery_proposals"], 86)
        self.assertEqual(meta["unknown_label_cues"], 53)
        self.assertFalse(meta["actual_av_verified"])
        self.assertFalse(meta["independent_editorial_acceptance"])
        rows = [json.loads(line) for line in files["provenance.jsonl"].splitlines()]
        queue = json.loads(files["review-queue.json"])
        self.assertEqual(len(rows), 354)
        self.assertEqual([r["source_text"] for r in rows], [x["text"] for x in source])
        self.assertEqual([r["source_start_ms"] for r in rows],
                         [x["start_ms"] for x in source])
        self.assertEqual([r["source_end_ms"] for r in rows],
                         [x["end_ms"] for x in source])
        self.assertTrue(all(r["original_dialogue_sha256"] == source_manifest["sha256"]
                            and not r["candidate_role_original_soundtrack_verified"]
                            for r in rows))
        self.assertEqual(len(queue["contextual_role_review"]), 354)
        self.assertEqual(len(queue["boundary_review_questions"]), 353)
        self.assertEqual(len(queue["textual_delivery_p2_review"]), 86)
        self.assertTrue(all(
            not q["original_audio_tone_verified"]
            and not q["eligible_for_performed_stage_direction"]
            for q in queue["textual_delivery_p2_review"]))
        for n, role in ((52, "Lana Wagner"), (58, "Dan Fielding"), (68, "Lana Wagner"),
                        (69, "Eleanor Brandon"), (72, "Dan Fielding"),
                        (140, "Liz Williams"), (147, "Liz Williams"),
                        (206, "Selma Hacker"), (319, "Eleanor Brandon"),
                        (348, "Harry Stone"), (353, "Leonard Brandon")):
            with self.subTest(cue=n):
                self.assertEqual(rows[n-1]["candidate_display_role"], role)
        for n, pair in ((14, ["Harry Stone", "Dan Fielding"]),
                        (66, ["Harry Stone", "Eleanor Brandon"]),
                        (129, ["Lana Wagner", "Harry Stone"]),
                        (146, ["Harry Stone", "Liz Williams"]),
                        (194, ["Selma Hacker", "Harry Stone"]),
                        (205, ["Selma Hacker", "Harry Stone"]),
                        (218, ["Barbara 'Buffy' (Miss USA)", "Dan Fielding"]),
                        (284, ["Leonard Brandon", "Eleanor Brandon"]),
                        (290, ["Eleanor Brandon", "Leonard Brandon"]),
                        (340, ["Eleanor Brandon", "Harry Stone"])):
            with self.subTest(internal_cue=n):
                row = rows[n-1]
                p = row["source_speaker_parts"]
                self.assertEqual(len(p), 2)
                self.assertEqual([x["provisional_part_role"] for x in p], pair)
                self.assertEqual([x["source_character_start"] for x in p[1:]],
                                 row["contextual_unicode_split_offsets"])
                self.assertEqual("".join(
                    row["source_text"][part["source_character_start"]:
                                       part["source_character_end"]] for part in p),
                    row["source_text"])
                self.assertTrue(all(part["original_audio_subcue_time_ms"] is None
                                    and not part["original_audio_boundary_verified"]
                                    for part in p))
        for n in (109, 111, 113, 181, 192, 193, 196, 251):
            self.assertIsNone(rows[n-1]["candidate_display_role"])
        self.assertEqual(files["screenplay.md"].count("Textual delivery hypothesis:"), 86)
        self.assertIn("NOT AV-CERTIFIED", files["screenplay.md"])

    def test_s01e05_bull_foley_full_context_source_and_delivery_are_unverified(self):
        ep = "S01E05"
        source_meta, _, captions = source_rows(ROOT, self.index[ep])
        files, manifest = construct(ROOT, ep, self.index[ep])
        context = manifest["contextual_overlay"]
        self.assertEqual(manifest["evidence_tier"],
                         "contextual_provisional_reading_draft")
        self.assertEqual(manifest["source_units"], 410)
        self.assertEqual(context["high_medium_single_role_hypotheses"], 343)
        self.assertEqual(context["mixed_voice_internal_review_cues"], 52)
        self.assertEqual(context["exact_contextual_internal_handoffs"], 52)
        self.assertEqual(context["unlocated_contextual_internal_handoffs"], 0)
        self.assertEqual(context["weak_or_abstained_cues"], 15)
        self.assertEqual(context["text_only_performance_tone_hypotheses"], 232)
        self.assertEqual(manifest["unknown_label_cues"], 67)
        self.assertEqual(manifest["text_only_contextual_delivery_proposals"], 232)
        self.assertFalse(manifest["actual_av_verified"])
        self.assertFalse(manifest["original_audio_performed_delivery_accepted"])
        rows = [json.loads(x) for x in files["provenance.jsonl"].splitlines()]
        review = json.loads(files["review-queue.json"])
        self.assertEqual(len(rows), len(captions))
        self.assertEqual([x["source_text"] for x in rows],
                         [x["text"] for x in captions])
        self.assertEqual([x["source_start_ms"] for x in rows],
                         [x["start_ms"] for x in captions])
        self.assertEqual([x["source_end_ms"] for x in rows],
                         [x["end_ms"] for x in captions])
        self.assertTrue(all(x["original_dialogue_sha256"] == source_meta["sha256"]
                            and not x["candidate_role_original_soundtrack_verified"]
                            for x in rows))
        self.assertEqual(len(review["contextual_role_review"]), 410)
        self.assertEqual(len(review["boundary_review_questions"]), 409)
        self.assertEqual(len(review["textual_delivery_p2_review"]), 232)
        self.assertTrue(all(not x["original_audio_tone_verified"]
                            and not x["eligible_for_performed_stage_direction"]
                            for x in review["textual_delivery_p2_review"]))
        self.assertEqual(files["screenplay.md"].count("Textual delivery hypothesis:"), 232)
        for n, role in ((94, "Harry Stone"), (95, "Lana Wagner"),
                        (96, "Dan Fielding"), (97, "Liz Williams"),
                        (99, "Leonard Bloom (credited Blum)"),
                        (100, "Dan Fielding"), (101, "Leonard Bloom (credited Blum)"),
                        (150, "Vincent Frago"), (180, "Lana Wagner"),
                        (181, "Dan Fielding"), (315, "Ralph Foley"),
                        (348, "Bull Shannon"), (407, "Selma Hacker")):
            with self.subTest(source_cue=n):
                self.assertEqual(rows[n-1]["candidate_display_role"], role)
        for n, speakers in (
            (23, ["Dan Fielding", "Harry Stone"]),
            (93, ["Vincent Frago", "Iris Keller"]),
            (98, ["Liz Williams", "Leonard Bloom (credited Blum)"]),
            (104, ["Liz Williams", "Harry Stone"]),
            (154, ["Vincent Frago", "Leonard Bloom (credited Blum)"]),
            (170, ["Harry Stone", "Bull Shannon"]),
            (235, ["Lana Wagner", "Harry Stone"]),
            (325, ["Ralph Foley", "Harry Stone"]),
            (409, ["Bull Shannon", "Selma Hacker"]),
        ):
            with self.subTest(internal=n):
                row = rows[n-1]
                parts = row["source_speaker_parts"]
                self.assertEqual(len(parts), 2)
                self.assertEqual([p["provisional_part_role"] for p in parts],
                                 speakers)
                self.assertEqual(row["contextual_unicode_split_offsets"],
                                 [parts[1]["source_character_start"]])
                self.assertEqual("".join(
                    row["source_text"][p["source_character_start"]:
                                       p["source_character_end"]] for p in parts),
                    row["source_text"])
                self.assertTrue(all(not p["original_audio_boundary_verified"]
                                    and p["original_audio_subcue_time_ms"] is None
                                    for p in parts))
        # C93 is an exact conversational handoff without any source dash.
        self.assertNotIn("\\n- ", rows[92]["source_text"])
        self.assertIsNone(rows[92]["candidate_display_role"])
        for n in (18, 21, 59, 88, 89, 123, 146, 163, 192, 327,
                  385, 386, 392, 393, 394):
            self.assertIsNone(rows[n-1]["candidate_display_role"])

    def test_s01e06_source_exact_377_cues_with_context_p0_p1_p2(self):
        ep = "S01E06"
        meta, _, captions = source_rows(ROOT, self.index[ep])
        files, manifest = construct(ROOT, ep, self.index[ep])
        overlay = manifest["contextual_overlay"]
        self.assertEqual(manifest["source_units"], 377)
        self.assertEqual(manifest["evidence_tier"], "contextual_provisional_reading_draft")
        self.assertEqual(overlay["high_medium_single_role_hypotheses"], 298)
        self.assertEqual(overlay["mixed_voice_internal_review_cues"], 75)
        self.assertEqual(overlay["weak_or_abstained_cues"], 4)
        self.assertEqual(overlay["exact_contextual_internal_handoffs"], 75)
        self.assertEqual(overlay["unlocated_contextual_internal_handoffs"], 0)
        self.assertEqual(overlay["text_only_performance_tone_hypotheses"], 52)
        self.assertEqual(manifest["unknown_label_cues"], 79)
        self.assertEqual(manifest["contextual_provisional_named_parts"], 150)
        self.assertEqual(manifest["source_contextual_exact_p0_boundaries"], 75)
        self.assertEqual(manifest["text_only_contextual_delivery_proposals"], 52)
        self.assertFalse(manifest["actual_av_verified"])
        self.assertFalse(manifest["independent_editorial_acceptance"])
        self.assertFalse(manifest["original_audio_performed_delivery_accepted"])
        rows = [json.loads(line) for line in files["provenance.jsonl"].splitlines()]
        review = json.loads(files["review-queue.json"])
        self.assertEqual([x["source_text"] for x in rows], [x["text"] for x in captions])
        self.assertEqual([x["source_start_ms"] for x in rows],
                         [x["start_ms"] for x in captions])
        self.assertEqual([x["source_end_ms"] for x in rows],
                         [x["end_ms"] for x in captions])
        self.assertTrue(all(x["original_dialogue_sha256"] == meta["sha256"]
                            and not x["candidate_role_original_soundtrack_verified"]
                            for x in rows))
        self.assertEqual(len(review["contextual_role_review"]), 377)
        self.assertEqual(len(review["boundary_review_questions"]), 376)
        self.assertEqual(len(review["textual_delivery_p2_review"]), 52)
        self.assertTrue(all(not x["original_audio_tone_verified"] and
                            not x["eligible_for_performed_stage_direction"]
                            for x in review["textual_delivery_p2_review"]))
        self.assertEqual(files["screenplay.md"].count("Textual delivery hypothesis:"), 52)
        for n, role in ((1, "Harry Stone"), (5, "Anthony Rodriguez"),
                        (9, "Harry Stone"), (30, "God (self-identified defendant)"),
                        (50, "Liz Williams"), (65, "Detective Womack"),
                        (83, "Bull Shannon"), (112, "Lana Wagner"),
                        (143, "Anthony Rodriguez"),
                        (161, "Lou (bomb-disposal technician)"),
                        (202, "Harry Stone"), (265, "Bull Shannon"),
                        (315, "Harry Stone"), (366, "Bull Shannon"),
                        (377, "Bull Shannon")):
            with self.subTest(cue=n):
                self.assertEqual(rows[n - 1]["candidate_display_role"], role)
        for n, roles in (
            (2, ["Harry Stone", "Anthony Rodriguez"]),
            (28, ["Liz Williams", "God (self-identified defendant)"]),
            (75, ["Bull Shannon", "Harry Stone"]),
            (108, ["Harry Stone", "Detective Womack"]),
            (172, ["Detective Womack", "Lou (bomb-disposal technician)"]),
            (201, ["Lana Wagner", "Harry Stone"]),
            (207, ["Lana Wagner", "Harry Stone"]),
            (268, ["Unidentified courtroom attendee", "Harry Stone"]),
            (299, ["Lana Wagner", "Harry Stone"]),
            (349, ["Harry Stone", "Lana Wagner"]),
        ):
            with self.subTest(mixed=n):
                row = rows[n - 1]
                parts = row["source_speaker_parts"]
                self.assertEqual([x["provisional_part_role"] for x in parts], roles)
                self.assertEqual(row["contextual_unicode_split_offsets"],
                                 [parts[1]["source_character_start"]])
                self.assertEqual("".join(row["source_text"][
                    p["source_character_start"]:p["source_character_end"]]
                    for p in parts), row["source_text"])
                self.assertTrue(all(not p["original_audio_boundary_verified"]
                                    and p["original_audio_subcue_time_ms"] is None
                                    for p in parts))
        self.assertEqual(rows[206]["contextual_unicode_split_offsets"], [30])
        self.assertTrue(rows[206]["source_text"][30:].startswith("- Thanks."))
        self.assertTrue(all(rows[n - 1]["candidate_display_role"] is None
                            for n in (240, 292, 358, 359)))

    def test_contextual_p0_rejects_off_by_one_explicit_speaker_dash(self):
        from script_factory import contextual_role_overlay
        episode = "S01E06"
        manifest, _, cues = source_rows(ROOT, self.index[episode])
        source = json.loads((ROOT / "seasons/S01/S01E06/derived" /
                             "text-only-speaker-proposals-v1.json").read_text("utf-8"))
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            dest = root / "seasons/S01/S01E06/derived/text-only-speaker-proposals-v1.json"
            dest.parent.mkdir(parents=True)
            for forged_offset in (29, 31):
                with self.subTest(forced_offset=forged_offset):
                    tampered = json.loads(json.dumps(source))
                    tampered["records"][206]["utf8_or_unicode_split_offsets"] = [
                        forged_offset]
                    dest.write_text(json.dumps(tampered), encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, "misaligned with source speaker dash"):
                        contextual_role_overlay(root, episode, manifest, cues)

    def test_s01e07_original_366_source_cues_and_character_handoffs(self):
        ep = "S01E07"
        original, _, cues = source_rows(ROOT, self.index[ep])
        files, manifest = construct(ROOT, ep, self.index[ep])
        overlay = manifest["contextual_overlay"]
        self.assertEqual(manifest["source_units"], 366)
        self.assertEqual(manifest["evidence_tier"], "contextual_provisional_reading_draft")
        self.assertEqual(overlay["high_medium_single_role_hypotheses"], 281)
        self.assertEqual(overlay["mixed_voice_internal_review_cues"], 73)
        self.assertEqual(overlay["weak_or_abstained_cues"], 12)
        self.assertEqual(overlay["exact_contextual_internal_handoffs"], 73)
        self.assertEqual(overlay["unlocated_contextual_internal_handoffs"], 0)
        self.assertEqual(overlay["text_only_performance_tone_hypotheses"], 53)
        self.assertEqual(manifest["text_only_contextual_delivery_proposals"], 53)
        self.assertEqual(manifest["source_contextual_exact_p0_boundaries"], 73)
        self.assertEqual(manifest["contextual_provisional_named_parts"], 146)
        self.assertEqual(manifest["unknown_label_cues"], 85)  # 73 mixed + 12 unassigned
        self.assertFalse(manifest["actual_av_verified"])
        self.assertFalse(manifest["original_audio_performed_delivery_accepted"])
        readers = [json.loads(x) for x in files["provenance.jsonl"].splitlines()]
        queue = json.loads(files["review-queue.json"])
        self.assertEqual([x["source_text"] for x in readers], [x["text"] for x in cues])
        self.assertEqual([x["source_start_ms"] for x in readers],
                         [x["start_ms"] for x in cues])
        self.assertEqual([x["source_end_ms"] for x in readers],
                         [x["end_ms"] for x in cues])
        self.assertTrue(all(x["original_dialogue_sha256"] == original["sha256"]
                            and not x["candidate_role_original_soundtrack_verified"]
                            and not x["performed_tone_original_soundtrack_verified"]
                            for x in readers))
        self.assertEqual(len(queue["contextual_role_review"]), 366)
        self.assertEqual(len(queue["boundary_review_questions"]), 365)
        self.assertEqual(len(queue["textual_delivery_p2_review"]), 53)
        self.assertTrue(all(not x["original_audio_tone_verified"]
                            for x in queue["textual_delivery_p2_review"]))
        for n, expected in ((31, "Disheveled Man"), (33, "Cafeteria Cashier"),
                            (70, "Harry Stone"), (86, "Harry Stone"),
                            (87, "Liz Williams"), (159, "Judge Robert T. Willard"),
                            (191, "Harry Stone"), (192, "Harry Stone"),
                            (264, "Carla B."), (283, "Dan Fielding"),
                            (332, "Judge Robert T. Willard"),
                            (345, "Unidentified television election announcer"),
                            (366, "Dan Fielding")):
            with self.subTest(cue=n):
                self.assertEqual(readers[n-1]["candidate_display_role"], expected)
        for n, roles in (
            (8, ["Carla B.", "Harry Stone"]),
            (99, ["Liz Williams", "Harry Stone"]),
            (158, ["Judge Robert T. Willard", "Harry Stone"]),
            (216, ["Dan Fielding", "Harry Stone"]),
            (261, ["Carla B.", "Liz Williams"]),
            (328, ["Judge Robert T. Willard", "Harry Stone"]),
        ):
            with self.subTest(mixed=n):
                line = readers[n-1]
                parts = line["source_speaker_parts"]
                self.assertEqual(len(parts), 2)
                self.assertEqual([p["provisional_part_role"] for p in parts], roles)
                self.assertEqual([parts[1]["source_character_start"]],
                                 line["contextual_unicode_split_offsets"])
                self.assertEqual("".join(line["source_text"][
                    p["source_character_start"]:p["source_character_end"]]
                    for p in parts), line["source_text"])
                self.assertFalse(any(p["original_audio_boundary_verified"] for p in parts))
        # There are genuine two-speaker subtitle cues that text alone
        # cannot attribute: protect them as P0 structural unknowns.
        for n in (280, 281):
            self.assertIsNone(readers[n-1]["candidate_display_role"])
            self.assertEqual(len(readers[n-1]["source_speaker_parts"]), 2)
            self.assertTrue(all(not part["original_audio_boundary_verified"]
                                for part in readers[n-1]["source_speaker_parts"]))
        self.assertFalse(manifest["independent_editorial_acceptance"])

    def test_source_only_factory_uses_grammar_p0_without_name_or_time_fabrication(self):
        episode = "S01E08"  # first six S01 episodes now have contextual overlays
        files, manifest = construct(ROOT, episode, self.index[episode])
        self.assertEqual(manifest["evidence_tier"], "source_only_reading_draft")
        self.assertGreaterEqual(manifest["source_syntactic_p0_provisional_continuations"], 20)
        rows = [json.loads(s) for s in files["provenance.jsonl"].splitlines()]
        review = json.loads(files["review-queue.json"])
        grammar = [(i, row) for i, row in enumerate(rows)
                   if row["source_syntactic_continuation_hypothesis"]]
        self.assertEqual(len(grammar),
                         manifest["source_syntactic_p0_provisional_continuations"])
        self.assertTrue(all(i > 0 and r["provisional_continuation_of_previous"]
                            and r["candidate_display_role"] is None
                            and r["source_end_ms"] is not None
                            and not r["candidate_role_original_soundtrack_verified"]
                            and review["boundary_review_questions"][i - 1]["decision"]
                            == "source_syntactic_provisional_same_voice"
                            and not review["boundary_review_questions"][i - 1]["source_audio_verified"]
                            for i, r in grammar))
        self.assertEqual(len(review["boundary_review_questions"]), len(rows) - 1)

    def test_factory_edits_do_not_wake_legacy_multi_stage_pilot_rebuilder(self):
        # That historical rebuild executes ~13 serial manuscript generators
        # and can race the source-exact one-click factory's private publisher.
        # Keep it for actual S01E01 and S09E19 editorial changes only.
        workflow = (ROOT.parent / ".github/workflows/night-court-private-working-drafts.yml").read_text(
            "utf-8")
        self.assertEqual(workflow.count("      - 'Night Court/seasons/S01/S01E01/**'"), 2)
        self.assertEqual(workflow.count("      - 'Night Court/seasons/S09/S09E19/**'"), 2)
        self.assertNotIn("      - 'Night Court/seasons/**'", workflow)
        for filename in (
            "script_factory.py", "test_script_factory.py",
            "preserve_original_qwen_model_reports.py",
            "test_preserve_original_qwen_model_reports.py",
            "owner_qwen_original_video_pilot.py",
            "test_owner_qwen_original_video_pilot.py",
        ):
            self.assertEqual(
                workflow.count("      - '!Night Court/tools/" + filename + "'"),
                2, filename)
        # Independent factory workflow must remain the sole code owner of
        # building and saving ordinary original-series screenplay packages.
        factory = (ROOT.parent / ".github/workflows/night-court-script-factory.yml").read_text(
            "utf-8")
        self.assertIn("Night Court/tools/script_factory.py", factory)

    def test_explicit_speaker_only_never_converts_addressee_to_voice(self):
        self.assertEqual(source_role("HARRY: Hello, Dan"), "HARRY")
        self.assertEqual(source_role("<v Roz>Hey, Harry"), "Roz")
        self.assertIsNone(source_role("Hey, Harry, come over here"))
        self.assertIsNone(source_role("MUSIC: trumpet riff"))
        self.assertTrue(multi_voice_typography("- Hello\n- What's new?"))
        self.assertFalse(multi_voice_typography("- Hello\nAre you there?"))

    def test_multi_dash_voice_segments_preserve_exact_source_unicode(self):
        samples = [
            ("- Hello, Dan.\n- Hello, Harry.", 2),
            ("- First speaker\nwraps onto another line\n– Second speaker", 2),
            ("A previous voice speaks.\n- A second voice\n- A third voice", 3),
            ("First voice continues a sentence.\n- Second voice interrupts.", 2),
            ("...Santa has over there.\n- Yeah.", 2),
            ("...about what I said before.\n- Oh, don't worry.", 2),
            ("- Only one leading dash; continuation is unmarked", 1),
            ("An ordinary hyphen - in a sentence", 1),
            ("— Bonjour, café.\n— Voilà, niño.", 2),
            ("- Hello\n- There\n- Friend", 3),
        ]
        for raw, expected in samples:
            with self.subTest(source=raw):
                parts = structural_speaker_parts(raw)
                self.assertEqual(len(parts), expected)
                self.assertEqual("".join(p["text"] for p in parts), raw)
                self.assertEqual(parts[0]["start"], 0)
                self.assertEqual(parts[-1]["end"], len(raw))
                self.assertEqual([p["start"] for p in parts[1:]],
                                 [p["end"] for p in parts[:-1]])
                self.assertTrue(all(sha(p["text"].encode("utf-8")) ==
                                    p["source_text_sha256"] for p in parts))
                self.assertTrue(all(not p["actual_speaker_boundary_verified"] for p in parts))

    def test_unaccepted_visual_model_proposals_never_enter_script_text(self):
        from unittest.mock import patch
        specimen = {
            "status": "original_source_model_proposals_unverified",
            "sampled_windows": 1, "human_film_reviewer_accepted": False,
            "whole_episode_video_covered": False,
        }
        snippet = {
            "unverified_description": {"actions": "MODEL TEST: person leans in"},
            "source_window_ms": [846000, 848000],
            "original_video_human_verified": False,
            "original_stage_direction_accepted": False,
        }
        with patch("script_factory.original_film_visual_model_review",
                   return_value=(specimen, [snippet])):
            files, manifest = construct(ROOT, "S01E01", self.index["S01E01"])
        self.assertEqual(manifest["original_film_visual_model_evidence"], specimen)
        self.assertEqual(json.loads(files["review-queue.json"])[
            "original_film_visual_model_only_review"], [snippet])
        self.assertNotIn("MODEL TEST: person leans in", files["screenplay.md"])
        self.assertFalse(manifest["actual_av_verified"])

    def test_single_late_dash_matches_known_pilot_and_protects_s01e02_unknown(self):
        # S01E01 pilot C219 has two canonical editor character voices,
        # Harry Stone and Phil Kerr, though source transcription marks only
        # the *second* voice with a dash. This checks the proposed structure,
        # NOT independent audio/video approval or sub-cue time.
        witness, _, cues = source_rows(ROOT, self.index["S01E01"])
        original = cues[218]
        self.assertEqual(original["cue"], 219)
        self.assertEqual(len(structural_speaker_parts(original["text"])), 2)
        self.assertEqual("".join(x["text"] for x in structural_speaker_parts(original["text"])),
                         original["text"])
        source_readers = [
            json.loads(line) for line in
            (ROOT / "saved-private/pilot-current/pilot-current-editorial-reader.jsonl")
            .read_text("utf-8").splitlines() if line.strip()
        ]
        expected_roles = {
            row["candidate_role"] for row in source_readers
            if row["episode_id"] == "S01E01"
            and "C219.1" in row["original_source_part_refs"]
        }
        self.assertEqual(expected_roles, {"HARRY STONE", "PHIL KERR"})

        # Generic cue C67 has an unknown identity but exactly TWO voices.
        # C349 has a source-exact contextual overlay providing role names;
        # the shared splitter independently detects that same P0 handoff.
        ep = "S01E02"
        files, report = construct(ROOT, ep, self.index[ep])
        rows = [json.loads(line) for line in files["provenance.jsonl"].splitlines()]
        unknown = rows[66]
        self.assertEqual(unknown["cue"], 67)
        self.assertIsNone(unknown["candidate_display_role"])
        self.assertEqual(len(unknown["source_speaker_parts"]), 2)
        self.assertTrue(all(part["provisional_part_role"] is None
                            and not part["original_audio_boundary_verified"]
                            for part in unknown["source_speaker_parts"]))
        self.assertEqual(len(rows[348]["source_speaker_parts"]), 2)
        self.assertEqual(rows[348]["contextual_unicode_split_offsets"], [29])
        self.assertEqual([part["provisional_part_role"] for part in
                          rows[348]["source_speaker_parts"]],
                         ["Eddie Simms", "Santa / John Stevens"])
        self.assertGreaterEqual(report["source_dash_candidate_p0_boundaries"], 1)
        self.assertFalse(report["actual_av_verified"])

    def test_pilots_reuse_source_checked_canonical_manuscripts(self):
        for ep in PILOTS:
            with self.subTest(ep=ep):
                files, data = construct(ROOT, ep, self.index[ep])
                raw = (ROOT / "saved-private/pilot-current" /
                       (ep + "-working-screenplay.md")).read_bytes()
                self.assertEqual(sha(files["screenplay.md"].encode()), sha(raw))
                self.assertEqual(data["evidence_tier"], "canonical_provisional_editorial_script")
                self.assertFalse(data["actual_av_verified"])
                self.assertFalse(data["independent_editorial_acceptance"])
                rows = [json.loads(x) for x in files["provenance.jsonl"].splitlines()]
                self.assertEqual(len(rows), data["provisional_reader_blocks"])
                self.assertEqual(len(json.loads(files["review-queue.json"])["boundary_review_questions"]),
                                 len(rows) - 1)
                self.assertTrue(all(sha(x["source_text"].encode()) == x["source_text_sha256"]
                                    for x in rows))

    def test_pilots_reuse_existing_original_soundtrack_without_claiming_av_truth(self):
        for ep, expected in (("S01E01", 194), ("S09E19", 30)):
            with self.subTest(ep=ep):
                files, manifest = construct(ROOT, ep, self.index[ep])
                report = manifest["original_audio_p0_triage"]
                self.assertEqual(report["status"], "canonical_source_audio_model_linked")
                self.assertEqual(report["model_measured_adjacent_pairs"], expected)
                self.assertEqual(report["matched_p0_pairs"], expected)
                self.assertFalse(report["speaker_or_turn_audio_accepted"])
                self.assertFalse(manifest["actual_av_verified"])
                queue = json.loads(files["review-queue.json"])
                scored = [x for x in queue["boundary_review_questions"]
                          if "original_soundtrack_machine_similarity" in x]
                self.assertEqual(len(scored), expected)
                self.assertTrue(all(not x["original_audio_performed_boundary_verified"]
                                    for x in scored))
                focus = queue["original_audio_model_priority_p0"]
                self.assertEqual(len(focus), report["priority_original_audio_p0_conflicts"])
                self.assertTrue(len(focus) > 0)
                self.assertTrue(all(not f["film_heard_turn_confirmed"] for f in focus))
                rows = [json.loads(s) for s in files["provenance.jsonl"].splitlines()]
                p1 = queue["original_audio_model_p1_unknown_voice_review"]
                self.assertEqual(len(p1), 6 if ep == "S01E01" else 16)
                self.assertEqual(report["previously_unknown_original_voice_windows"], len(p1))
                self.assertEqual(report["unknown_voice_model_automatically_promoted"], 0)
                self.assertEqual(len(set(x["reading_block_id"] for x in p1)), len(p1))
                self.assertTrue(all(
                    not x["original_soundtrack_heard_by_editor"]
                    and not x["actual_character_voice_verified"]
                    and not x["eligible_for_automatic_role_promotion"]
                    and x["source_video_sha256"] == report["original_video_sha256"]
                    and x["model_source_report_sha256"] == report["sha256"]
                    and x["uncertified_machine_nearest_role"]
                    for x in p1))
                if ep == "S09E19":
                    self.assertTrue(all(
                        x["source_caption_time_ms"] is None and
                        isinstance(x["unverified_original_movie_seek_hint_ms"], list)
                        for x in p1))
                else:
                    self.assertTrue(all(
                        isinstance(x["source_caption_time_ms"], list) and
                        x["unverified_original_movie_seek_hint_ms"] is None
                        for x in p1))
                self.assertFalse(any(x["provisional_role"] is not None for x in rows
                                     if x["reading_block_id"] in
                                     {y["reading_block_id"] for y in p1}))
                self.assertEqual(
                    len([x for x in scored
                         if x["review_priority"] == "P0_FOCUS_MODEL_CONTRADICTION"]),
                    len(focus))

    def test_source_audio_p1_rejects_forged_calibration_and_false_av_acceptance(self):
        import shutil
        from script_factory import apply_existing_original_audio_p0
        ep = "S09E19"
        files, report = construct(ROOT, ep, self.index[ep])
        rows = [json.loads(s) for s in files["provenance.jsonl"].splitlines()]
        edges = json.loads(files["review-queue.json"])["boundary_review_questions"]
        path = ROOT / "saved-private/episode-finish-current" / (
            ep + "-original-audio-p0p1-evidence.json")
        current = json.loads(path.read_text("utf-8"))
        original = (ROOT / "saved-private/pilot-current" /
                    (ep + "-working-screenplay.md")).read_text("utf-8")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            target = root / "saved-private/episode-finish-current" / path.name
            target.parent.mkdir(parents=True)
            for field, forged in (
                ("actor_voice_original_soundtrack_independently_verified", True),
                ("global_and_role_holdout_pass", True),
                ("source_original_timecode_ms", [100, 150]),
                ("source_ref", "C99999.1"),
                ("uncertified_best_role", ""),
            ):
                with self.subTest(field=field):
                    tampered = json.loads(json.dumps(current))
                    tampered["unknown_original_soundtrack_proposals"][0][field] = forged
                    target.write_text(json.dumps(tampered), encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, "P1 source voice"):
                        apply_existing_original_audio_p0(
                            root, ep, self.index[ep]["sha256"], original, edges, rows)

    def test_generic_maintains_all_actual_original_cues_and_never_invents_time(self):
        for ep in ("S05E05", "S09E18"):
            with self.subTest(ep=ep):
                manifest, _, cues = source_rows(ROOT, self.index[ep])
                files, data = construct(ROOT, ep, self.index[ep])
                self.assertEqual(data["evidence_tier"],
                                 "contextual_provisional_reading_draft" if ep == "S05E05"
                                 else "source_only_reading_draft")
                self.assertEqual(data["source_units"], manifest["cue_count"])
                rows = [json.loads(x) for x in files["provenance.jsonl"].splitlines()]
                self.assertEqual([x["source_text"] for x in rows], [x["text"] for x in cues])
                self.assertEqual([x["source_start_ms"] for x in rows],
                                 [x["start_ms"] for x in cues])
                self.assertEqual([x["source_end_ms"] for x in rows],
                                 [x["end_ms"] for x in cues])
                self.assertTrue(all(x["original_dialogue_sha256"] == manifest["sha256"]
                                    for x in rows))
                self.assertFalse(data["actual_av_verified"])

    def test_s05_contextual_review_is_used_without_fake_audio_witness(self):
        ep = "S05E05"
        files, data = construct(ROOT, ep, self.index[ep])
        overlay = data["contextual_overlay"]
        self.assertEqual(overlay["high_medium_single_role_hypotheses"], 265)
        self.assertEqual(overlay["mixed_voice_internal_review_cues"], 7)
        self.assertEqual(overlay["weak_or_abstained_cues"], 28)
        self.assertEqual(overlay["exact_contextual_internal_handoffs"], 7)
        self.assertEqual(overlay["unlocated_contextual_internal_handoffs"], 0)
        self.assertEqual(data["source_contextual_exact_p0_boundaries"], 7)
        self.assertEqual(data["contextual_provisional_named_parts"], 14)
        self.assertFalse(overlay["original_audio_verified"])
        self.assertEqual(data["unknown_label_cues"], 35)
        rows = [json.loads(x) for x in files["provenance.jsonl"].splitlines()]
        self.assertEqual(rows[34]["candidate_display_role"], "Dan Fielding")
        self.assertTrue(rows[34]["provisional_continuation_of_previous"])
        self.assertIsNone(rows[35]["candidate_display_role"])
        self.assertEqual(rows[35]["contextual_intra_cue_voice_roles"],
                         ["Dan Fielding", "Harry Stone"])
        self.assertEqual(rows[35]["contextual_unicode_split_offsets"], [32])
        # Preserve the lead-in/out voice even when two voices share a cue:
        # Christine's line C10->C11, Harry C11->C12; Dan C35->C36,
        # Harry C36->C37; Dan C70->C71 and Devil C71->C72.
        for left, right in ((10, 11), (11, 12), (35, 36),
                            (36, 37), (70, 71), (71, 72)):
            edge = json.loads(files["review-queue.json"])["boundary_review_questions"][right - 2]
            self.assertEqual(edge["between_cues"], [left, right])
            self.assertTrue(rows[right - 1]["provisional_continuation_of_previous"])
            self.assertEqual(edge["left_provisional_exit_role"],
                             edge["right_provisional_entry_role"])
            self.assertFalse(edge["source_audio_verified"])
        self.assertFalse(rows[176]["provisional_continuation_of_previous"])  # 5.3s C176->177
        self.assertEqual([p["provisional_part_role"] for p in rows[35]["source_speaker_parts"]],
                         ["Dan Fielding", "Harry Stone"])
        self.assertTrue(all(not p["original_audio_boundary_verified"]
                            for p in rows[35]["source_speaker_parts"]))
        self.assertIsNone(rows[148]["candidate_display_role"])  # LOW confidence abstains
        self.assertTrue(all(not r["candidate_role_original_soundtrack_verified"] for r in rows))
        review = json.loads(files["review-queue.json"])
        self.assertEqual(len(review["contextual_role_review"]), 300)
        for cue, person in ((196, "Christine Sullivan"), (199, "Christine Sullivan"),
                            (202, "Christine Sullivan"), (207, "Christine Sullivan"),
                            (243, "Dave (safe technician)"), (253, "Roz Russell")):
            with self.subTest(cue=cue):
                self.assertEqual(rows[cue - 1]["candidate_display_role"], person)
                self.assertEqual(rows[cue - 1]["contextual_confidence"], "medium")
                self.assertFalse(rows[cue - 1]["candidate_role_original_soundtrack_verified"])
        self.assertIn(36, review["review_internal_voice_changes"])
        self.assertIn("contextual hypothesis, unverified", files["screenplay.md"])
        self.assertIn("contextual lexical turn hypothesis; audio unverified", files["screenplay.md"])
        self.assertIn("Devil / Stu Blumberg (contextual lexical turn hypothesis",
                      files["screenplay.md"])
        witness, _, captions = source_rows(ROOT, self.index[ep])
        with self.assertRaisesRegex(ValueError, "stale/malformed contextual role"):
            contextual_role_overlay(ROOT, ep, {**witness, "sha256": "0" * 64}, captions)

    def test_current_private_fan_retrieval_uses_strongest_five_episode_readers(self):
        from export_fan_retrieval_chunks import export
        factory = ROOT / "saved-private/script-factory-current"
        # Owners may add fully researched packages or explicitly publish all.
        # The exporter must match the actual SOURCE-VALIDATED committed package
        # population, not an obsolete fixed episode count.
        researched = {
            folder.name for folder in factory.iterdir()
            if folder.is_dir() and (folder / "manifest.json").is_file()
        }
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder) / "private-fan-retrieval"
            manifest = export(ROOT, out, factory_root=factory)
            self.assertEqual(manifest["episode_count"], 193)
            by_ep = {x["episode_id"]: x for x in manifest["episodes"]}
            self.assertEqual(len(by_ep), 193)
            self.assertEqual(sum(
                row["script_path"].startswith("saved-private/script-factory-current/")
                for row in by_ep.values()), len(researched))
            for ep in researched:
                with self.subTest(ep=ep):
                    draft = factory / ep / "screenplay.md"
                    self.assertEqual(by_ep[ep]["script_sha256"], sha(draft.read_bytes()))
                    self.assertTrue(by_ep[ep]["script_path"].endswith(
                        ep + "/screenplay.md"))
                    self.assertNotEqual(by_ep[ep]["evidence_tier"],
                                        "source_only_dialogue_scaffold")
            self.assertEqual(sum(x["evidence_tier"] == "source_only_dialogue_scaffold"
                                 for x in by_ep.values()), 193 - len(researched))
            self.assertEqual(by_ep["S01E03"]["evidence_tier"],
                             "contextual_provisional_reading_draft")
            self.assertGreater(by_ep["S01E03"]["chunks"], 0)
            self.assertTrue((out / "fan-retrieval-chunks.jsonl").is_file())
            self.assertTrue((out / "fan-retrieval-manifest.json").is_file())

    def test_all_193_episodes_generate_and_second_run_is_idempotent(self):
        with tempfile.TemporaryDirectory() as d:
            output = Path(d)
            first = run(ROOT, output, "all")
            self.assertEqual(len(first), 193)
            self.assertEqual(sum(x["changed_files"] for x in first), 193 * 4)
            again = run(ROOT, output, "all")
            self.assertTrue(all(x["changed_files"] == 0 for x in again))
            for ep in self.index:
                with self.subTest(ep=ep):
                    folder = output / ep
                    manifest = json.loads((folder / "manifest.json").read_text("utf-8"))
                    script = (folder / "screenplay.md").read_bytes()
                    provenance = (folder / "provenance.jsonl").read_bytes()
                    queue = (folder / "review-queue.json").read_bytes()
                    self.assertEqual(manifest["script_sha256"], sha(script))
                    self.assertEqual(manifest["source_provenance_sha256"], sha(provenance))
                    self.assertEqual(manifest["p0_review_queue_sha256"], sha(queue))
                    self.assertTrue(manifest["source_only_claims_never_promoted_to_av_truth"])
                    if ep not in PILOTS:
                        rows = [json.loads(s) for s in provenance.decode("utf-8").splitlines()]
                        cut_count = 0
                        for row in rows:
                            parts = row["source_speaker_parts"]
                            self.assertGreaterEqual(len(parts), 1)
                            self.assertEqual(parts[0]["source_character_start"], 0)
                            self.assertEqual(parts[-1]["source_character_end"], len(row["source_text"]))
                            self.assertEqual(
                                "".join(row["source_text"][p["source_character_start"]:
                                                            p["source_character_end"]] for p in parts),
                                row["source_text"])
                            for p in parts:
                                self.assertIsNone(p["original_audio_subcue_time_ms"])
                                self.assertFalse(p["original_audio_boundary_verified"])
                                self.assertEqual(sha(row["source_text"][
                                    p["source_character_start"]:p["source_character_end"]
                                ].encode("utf-8")), p["source_text_sha256"])
                            cut_count += len(parts) - 1
                        self.assertEqual(
                            manifest["source_dash_candidate_p0_boundaries"] +
                            manifest["source_contextual_exact_p0_boundaries"], cut_count)
                        review = json.loads(queue)
                        self.assertEqual(len(review["within_cue_structural_turn_questions"]), cut_count)
                        self.assertTrue(all(not q["source_audio_performed_turn_verified"]
                                            for q in review["within_cue_structural_turn_questions"]))
                        for row in rows:
                            if row["contextual_unicode_split_offsets"]:
                                self.assertEqual(
                                    row["contextual_unicode_split_offsets"],
                                    [p["source_character_start"] for p in
                                     row["source_speaker_parts"][1:]])
                                self.assertTrue(all(
                                    p["provisional_part_role"] is not None
                                    for p in row["source_speaker_parts"]))

    def test_cannot_silently_mutate_original_transcript(self):
        import shutil
        ep = "S05E05"
        index = self.index[ep]
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            folder = ROOT / "seasons/S05/S05E05"
            dest = root / "seasons/S05/S05E05"
            source_manifest = ROOT / index["manifest"]
            new_manifest = root / index["manifest"]
            new_manifest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_manifest, new_manifest)
            manifest = json.loads(source_manifest.read_text("utf-8"))
            for part in ("episode.json", manifest["original_path"], manifest["segments_path"]):
                src = folder / part
                target = dest / part
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, target)
            original = dest / manifest["original_path"]
            original.write_bytes(original.read_bytes() + b"\nsource damage")
            with self.assertRaisesRegex(ValueError, "immutable original transcript"):
                source_rows(root, index)


if __name__ == "__main__":
    unittest.main()
