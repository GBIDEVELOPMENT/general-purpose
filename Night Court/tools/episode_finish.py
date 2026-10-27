#!/usr/bin/env python3
"""One-pass, source-guarded AV editorial queue for canonical Night Court pilots.

Does not run a recognizer, watch film, certify actors or publish another script
revision. All original dialogue remains in saved-private/pilot-current. Run it
once after each *canonical* publication; amend a stable decision file, not v23.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

EPISODES = ("S01E01", "S09E19")
# Verified full original AVI SHA digests from episode source evidence, not SRT.
VIDEO_SHA = {
    "S01E01": "5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962",
    "S09E19": "51f409c620245f9f3744b1b38e534122fd8c82cfadc2221bf5f6fc14eac93649",
}
BATCH_BLOCKS = 12
SCHEMA = "night-court-single-pass-source-av-editorial/1"


def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def digest(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()


def load_episode(snapshot: Path, episode: str):
    if episode not in EPISODES:
        raise ValueError("Unsupported pilot episode")
    manifest = json.loads((snapshot / "working-screenplay-layout-manifest.json").read_text("utf-8"))
    expected = manifest["episodes"][episode]
    source = snapshot / (episode + "-working-screenplay-provenance.jsonl")
    manuscript = snapshot / (episode + "-working-screenplay.md")
    script_sha = hashlib.sha256(manuscript.read_bytes()).hexdigest()
    if script_sha != manifest["manuscript_sha256"][episode]:
        raise ValueError("Canonical manuscript has drifted")
    rows = [json.loads(line) for line in source.read_text("utf-8").splitlines() if line.strip()]
    if len(rows) != expected["source_blocks"]:
        raise ValueError("Canonical provenance row count mismatch")
    source_refs, block_ids = set(), set()
    source_sha = None
    for r in rows:
        if r["reading_block_id"] in block_ids:
            raise ValueError("Duplicate source reading block ID")
        block_ids.add(r["reading_block_id"])
        refs = r.get("original_source_part_refs")
        if not isinstance(refs, list) or not refs:
            raise ValueError("Reading block lost original caption source")
        source_refs.update(refs)
        if source_sha is None:
            source_sha = r["source_sha256"]
        if source_sha != r["source_sha256"] or len(source_sha) != 64:
            raise ValueError("Inconsistent immutable source witness SHA")
        if r.get("actual_original_av_reviewer_accepted") is not False:
            raise ValueError("Unproven previous AV certification")
        if not isinstance(r.get("display_group_id"), int):
            raise ValueError("No stable displayed-turn proposal")
        if episode == "S09E19" and r["source_cue_times_not_subturn_times_ms"] is not None:
            raise ValueError("S09 source is untimed, cannot create fake offsets")
    if len(source_refs) != expected["source_units"]:
        raise ValueError("Source part union is not complete")
    if source_sha not in manuscript.read_text("utf-8"):
        raise ValueError("Manuscript lacks immutable original witness SHA")
    # Include the original dialogue in the PRIVATE, LOCAL reviewer worksheet,
    # so source-ordered audio playback can actually be compared to each turn.
    # Never infer or paraphrase dialogue from stage prose or a language model.
    evidence = snapshot / "pilot-current-editorial-reader.jsonl"
    if not evidence.is_file():
        raise ValueError("Canonical original source reader needed for AV playback")
    by_id = {}
    for line in evidence.read_text("utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("episode_id") == episode:
            key = row["reading_block_id"]
            if key in by_id:
                raise ValueError("Duplicate canonical original-dialogue reading block")
            by_id[key] = row
    if set(by_id) != block_ids:
        raise ValueError("Original dialogue reader does not match provenance IDs")
    for r in rows:
        source_row = by_id[r["reading_block_id"]]
        caption = source_row.get("caption_text")
        if (not isinstance(caption, str)
            or hashlib.sha256(caption.encode("utf-8")).hexdigest()
               != r["exact_rendered_caption_sha256"]
            or source_row.get("original_source_sha256") != source_sha
            or source_row.get("original_source_part_refs") != r["original_source_part_refs"]):
            raise ValueError("Original dialogue or immutable source part changed")
        r["source_exact_dialogue_for_private_av_review"] = caption
    return manifest, rows, source_sha


def verified_s09_candidate_locator(path: Path):
    """Source-hashed *machine* lexical anchors; they are NOT true cue times."""
    raw = path.read_bytes()
    locator = json.loads(raw)
    if (locator.get("schema") != "night-court-s09-original-film-untimed-paragraph-audio-locator/1"
        or locator.get("episode_id") != "S09E19"
        or locator.get("original_video_sha256") != VIDEO_SHA["S09E19"]
        or locator.get("original_untimed_source_sha256")
           != "659beb9c50fabdd1028aac9570999d9a16b36e6d582938e10809cc0c664530b2"
        or locator.get("original_source_untimed_paragraph_count") != 347
        or locator.get("original_soundtrack_processed") is not True
        or locator.get("original_speaker_identities_verified") != 0
        or locator.get("candidate_source_paragraphs_given_audio_window") != 231):
        raise ValueError("Original S09 untimed source-AV locator proof mismatch")
    hints = {}
    for entry in locator["matches"]:
        n = entry.get("original_paragraph_id")
        window = entry.get("candidate_original_audio_window_ms")
        if (type(n) is not int or not 1 <= n <= 347 or n in hints
            or not isinstance(window, list) or len(window) != 2
            or any(type(t) is not int for t in window)
            or not 0 <= window[0] < window[1] <= 1_800_000
            or entry.get("original_paragraph_timecode_ms") is not None
            or entry.get("original_film_audio_timing_independently_verified") is not False
            or entry.get("spoken_character_identity_verified") is not False):
            raise ValueError("Fake original S09 paragraph timing or duplicate match")
        hints[n] = window
    if len(hints) != 231:
        raise ValueError("Original S09 source locator did not conserve 231 candidates")
    return hints, hashlib.sha256(raw).hexdigest()


def attach_source_audio_hints(packet: dict, path: Path):
    """Display previously measured original-AVI P0/P1 evidence, never accept it.

    No new names, performed turns or source-clock synchronizations are created.
    Numeric evidence is only valid against this exact canonical manuscript.
    """
    import math
    raw = path.read_bytes()
    report = json.loads(raw)
    ep = packet["episode_id"]
    if (report.get("schema") != "night-court-canonical-original-audio-p0-p1-evidence/1"
        or report.get("episode_id") != ep
        or report.get("original_video_sha256") != packet["original_video_sha256_expected"]
        or report.get("immutable_original_dialogue_sha256") != packet["source_original_dialogue_sha256"]
        or report.get("canonical_manuscript_sha256") != packet["canonical_manuscript_sha256"]
        or report.get("original_video_watched_by_human") is not False
        or report.get("independent_original_actor_voice_accepted") != 0
        or report.get("independent_performed_turns_accepted") != 0
        or report.get("media_audio_pcm_embedding_vectors_or_credentials_preserved") is not False
        or report.get("model_diary_not_film_truth") is not True
        or not isinstance(report.get("source_pcm_sha256"), str)
        or len(report["source_pcm_sha256"]) != 64
        or type(report.get("voice_embedding_windows_usable")) is not int
        or report["voice_embedding_windows_usable"] < 1):
        raise ValueError("Audio hint source, screenplay, original AVI or AV nonacceptance drift")
    by_block = {x["id"]: x for batch in packet["sequential_one_pass_batches"]
                for x in batch["reader_blocks"]}
    by_boundary = {(x["left_reading_block_id"], x["right_reading_block_id"]): x
                   for x in packet["all_adjacent_boundary_questions"]}
    checked_roles = set()
    for x in report.get("unknown_original_soundtrack_proposals", []):
        key = x.get("source_reading_block_id")
        if key not in by_block or key in checked_roles or by_block[key]["provisional_role"] is not None:
            raise ValueError("Acoustic UNKNOWN voice hint has wrong original reading block")
        checked_roles.add(key)
        if (x.get("actor_voice_original_soundtrack_independently_verified") is not False
            or x.get("source_ref") not in by_block[key]["source_parts"]):
            raise ValueError("Audio hint falsely verified a voice or changed source part")
        score = x.get("speaker_similarity")
        if score is not None and (type(score) not in (int, float)
                                  or not math.isfinite(score) or not -1 <= score <= 1):
            raise ValueError("Invalid original-audio voice similarity")
        name=x.get("acoustic_candidate")
        if name is not None and (not isinstance(name,str) or not name.strip()
                                 or x.get("global_and_role_holdout_pass") is not True):
            raise ValueError("Uncalibrated original-audio suggestion given a character name")
        by_block[key]["original_audio_model_uncertified_role_hint"]={
            "role_candidate":name,
            "best_uncertified_role":x.get("uncertified_best_role"),
            "cosine_similarity":score,
            "holdout_gate_passed":x.get("global_and_role_holdout_pass") is True,
            "original_actor_voice_verified":False
        }
    checked_pairs=set()
    for x in report.get("adjacent_P0_original_audio_voice_similarity", []):
        edge=(x.get("source_left"),x.get("source_right"))
        if edge not in by_boundary or edge in checked_pairs:
            raise ValueError("Acoustic boundary evidence is not a unique adjacent P0 question")
        checked_pairs.add(edge)
        original=by_boundary[edge]
        sim=x.get("machine_acoustic_voice_similarity")
        if (type(sim) not in (int,float) or not math.isfinite(sim)
            or not -1<=sim<=1 or x.get("source_audio_p0_performed_boundary_independently_verified") is not False
            or x.get("provisional_display_join") is not original["provisional_same_turn"]):
            raise ValueError("P0 audio pair claims a performed turn or changed provenance")
        original["original_audio_machine_voice_pair_similarity"]=sim
        original["machine_audio_p0_boundary_verified"]=False
    packet["original_soundtrack_machine_evidence_sha256"]=hashlib.sha256(raw).hexdigest()
    packet["machine_audio_hints_attached"]={
        "p1_unknown_candidates":len(checked_roles),
        "p0_adjacent_audio_pairs":len(checked_pairs),
        "is_original_AV_actor_or_turn_certification":False
    }
    return packet


def make_packet(snapshot: Path, episode: str, s09_locator: Path | None = None):
    manifest, rows, source_sha = load_episode(snapshot, episode)
    hints, hint_sha = ({}, None)
    if s09_locator is not None:
        if episode != "S09E19":
            raise ValueError("Untimed S09 audio locator cannot time S01")
        hints, hint_sha = verified_s09_candidate_locator(s09_locator)
    groups, boundaries = [], []
    for i in range(1, len(rows)):
        old, new = rows[i - 1], rows[i]
        joined = old["display_group_id"] == new["display_group_id"]
        # This is a QUESTION, not an independently heard performed boundary.
        boundaries.append({
            "id": f"B{i:04d}",
            "left_reading_block_id": old["reading_block_id"],
            "right_reading_block_id": new["reading_block_id"],
            "provisional_same_turn": joined,
            "priority": "P0_UNVERIFIED_JOIN" if joined else "P0_UNVERIFIED_BREAK",
        })
    internal = {}
    for r in rows:
        for ref in r["original_source_part_refs"]:
            internal.setdefault(ref, []).append(r["reading_block_id"])
    internal = [{"source_part_ref": ref, "reading_block_ids": ids,
                 "priority": "P0_WITHIN_ORIGINAL_SOURCE_PART"}
                for ref, ids in internal.items() if len(ids) > 1]
    for start in range(0, len(rows), BATCH_BLOCKS):
        end = min(start + BATCH_BLOCKS, len(rows))
        subset = rows[start:end]
        clips = [r.get("source_cue_times_not_subturn_times_ms") for r in subset]
        clock_kind = "source_caption_time_not_subturn_time" if episode == "S01E01" else "original_source_untimed"
        source_window = ([max(0, min(v[0] for v in clips) - 1200),
                          max(v[1] for v in clips) + 1200]
                         if all(isinstance(v, list) and len(v) == 2
                                and all(type(t) is int for t in v) for v in clips)
                         else None)
        if episode == "S09E19" and hints:
            candidate = [hints[int(ref[1:4])] for row in subset
                         for ref in row["original_source_part_refs"]
                         if ref.startswith("C") and ref[1:4].isdigit()
                         and int(ref[1:4]) in hints]
            if candidate:
                source_window = [max(0, min(v[0] for v in candidate) - 1200),
                                 max(v[1] for v in candidate) + 1200]
                clock_kind = "unverified_original_audio_lexical_seek_hint_not_source_timecode"
        questions = boundaries[max(0, start - 1):end - 1]
        groups.append({
            "id": f"{episode}-AV-{len(groups) + 1:03d}",
            "block_index_first": start,
            "block_index_end_exclusive": end,
            "source_window_candidate_ms": source_window,
            "source_window_kind": clock_kind,
            "source_clock_verified": False,
            "reader_blocks": [{
                "id": r["reading_block_id"],
                "source_parts": r["original_source_part_refs"],
                "provisional_role": r["candidate_role"],
                "source_dialogue_sha256": r["exact_rendered_caption_sha256"],
                "source_exact_dialogue": r["source_exact_dialogue_for_private_av_review"],
                "provisional_display_group_id": r["display_group_id"]
            } for r in subset],
            "boundary_question_ids": [b["id"] for b in questions],
            "goals_same_source_playback": [
                "P0 listen for all actual speaker changes, joins, interruptions and overlap",
                "P1 identify each voice using heard and visible evidence or abstain",
                "P2 note performance delivery supported by original soundtrack",
                "P3 note narratively important visible props and clothing",
                "P4 observe actor-action-target, cuts and physical business"
            ],
            "whole_original_av_played_and_verified": False
        })
    result = {
        "schema": SCHEMA,
        "episode_id": episode,
        "source_original_dialogue_sha256": source_sha,
        "original_video_sha256_expected": VIDEO_SHA[episode],
        "canonical_manuscript_sha256": manifest["manuscript_sha256"][episode],
        "canonical_edition": manifest["episode_editorial_integrations"][episode],
        "original_source_speaking_part_refs": len(set(
            ref for r in rows for ref in r["original_source_part_refs"])),
        "source_reader_blocks": len(rows),
        "provisional_display_groups": manifest["episodes"][episode]["display_groups"],
        "source_timecodes_available": episode == "S01E01",
        "unverified_source_audio_locator_match_count": len(hints),
        "original_audio_locator_report_sha256": hint_sha,
        "review_passes_required": len(groups),
        "all_adjacent_boundary_questions": boundaries,
        "within_source_part_handoffs_needing_review": internal,
        "sequential_one_pass_batches": groups,
        "no_fabricated_certifications": True,
        "original_audio_video_inspected_by_this_command": False,
        "script_final_or_full_episode_accepted": False,
        "workflow_instruction": "Review each sequential batch once on the SHA-pinned original film with synchronized sound; "
            "answer all P0 and P1 questions first, then record P2/P3/P4. "
            "Persist decisions in ONE stable episode ledger; regenerate ONE canonical screenplay. "
            "Machine-proposed names, source timestamps and display joins are not original-AV proof."
    }
    if len(boundaries) != len(rows) - 1:
        raise ValueError("Missing boundary")
    if sum(len(g["reader_blocks"]) for g in groups) != len(rows):
        raise ValueError("Review has incomplete reading-block coverage")
    if sum(b["provisional_same_turn"] for b in boundaries) != (
        len(rows) - manifest["episodes"][episode]["display_groups"]):
        raise ValueError("Unverified display joins mismatch")
    acoustic = snapshot.resolve().parent / "episode-finish-current" / (episode + "-original-audio-p0p1-evidence.json")
    if acoustic.is_file():
        attach_source_audio_hints(result, acoustic)
    result["packet_sha256"] = digest(result)
    return result


def block_turn_segments(row: dict, decision: dict):
    """Validate source-exact within-caption P0 handoffs, Unicode codepoint offsets.

    Every block is either one explicitly reviewed voice or consecutive
    nonempty exact-source slices. No changed letters, reordered captions,
    omitted dialogue, invented subturn clocks, or silent speaker switches.
    """
    content = row["source_exact_dialogue"]
    if (not isinstance(content, str) or not content or
        hashlib.sha256(content.encode("utf-8")).hexdigest()
        != row["source_dialogue_sha256"]):
        raise ValueError("Original caption text altered in AV review")
    if decision.get("intra_block_speaker_changes_reviewed") is not True:
        raise ValueError("P0 within-caption speaker handoffs not source-reviewed")
    role = decision.get("role")
    if not isinstance(role, str) or not role.strip():
        raise ValueError("P1 source role missing")
    raw = decision.get("segments")
    if raw is None:
        return [{"start": 0, "end": len(content), "role": role.strip()}]
    if not isinstance(raw, list) or not 1 <= len(raw) <= 20:
        raise ValueError("P0 split segments must be a bounded nonempty list")
    last = 0
    parts = []
    for piece in raw:
        if not isinstance(piece, dict) or set(piece) != {"start", "end", "role"}:
            raise ValueError("P0 segment must contain exact offset/role fields")
        a, b, who = piece["start"], piece["end"], piece["role"]
        if (type(a) is not int or type(b) is not int or
            a != last or not a < b <= len(content) or
            not isinstance(who, str) or not who.strip()):
            raise ValueError("P0 source-character segment lost, overlapped, reordered or unlabeled")
        parts.append({"start": a, "end": b, "role": who.strip()})
        last = b
    if last != len(content) or parts[0]["role"] != role.strip():
        raise ValueError("P0 source-character segments incomplete or first role inconsistent")
    if any(a["role"] == b["role"] for a, b in zip(parts, parts[1:])):
        raise ValueError("P0 redundant split: adjacent subturns have the same role")
    if "".join(content[x["start"]:x["end"]] for x in parts) != content:
        raise ValueError("P0 original dialogue not exactly conserved")
    return parts


def verify_decisions(packet: dict, decisions: dict):
    """Refuse script-complete claims without per-boundary, per-block original AV review.

    Checking a signed reviewer ledger is *not* itself proof of someone watching.
    Reviewer must have genuinely listened and watched the pinned original film.
    """
    if (decisions.get("packet_sha256") != packet.get("packet_sha256")
        or decisions.get("episode_id") != packet["episode_id"]
        or decisions.get("original_video_sha256") != packet["original_video_sha256_expected"]
        or decisions.get("review_method") != "continuous_original_synchronized_av"
        or decisions.get("original_source_film_sha256_verified_in_browser") is not True
        or decisions.get("original_media_sha256_computed_locally") != packet["original_video_sha256_expected"]
        or decisions.get("playback_edition_kind") not in ("same_original_file", "viewer_supplied_proxy_source_equivalence_unverified")
        or not isinstance(decisions.get("reviewer"), str)
        or not decisions["reviewer"].strip()):
        raise ValueError("Missing reviewer, source media SHA or matching packet")
    decision_boundaries = decisions.get("boundaries", {})
    decision_roles = decisions.get("roles", {})
    decision_batches = decisions.get("batches", {})
    if not all(isinstance(x, dict) for x in (decision_boundaries, decision_roles, decision_batches)):
        raise ValueError("Malformed independent AV decisions")
    required_edges = {x["id"] for x in packet["all_adjacent_boundary_questions"]}
    required_blocks = {r["id"] for batch in packet["sequential_one_pass_batches"]
                       for r in batch["reader_blocks"]}
    required_batches = {b["id"] for b in packet["sequential_one_pass_batches"]}
    if (set(decision_boundaries) != required_edges
        or set(decision_roles) != required_blocks
        or set(decision_batches) != required_batches):
        raise ValueError("Episode not fully reviewed: missing P0 boundaries, P1 roles or viewing batches")
    for outcome in decision_boundaries.values():
        if not isinstance(outcome, dict) or outcome.get("result") not in (
                "same_speaker_continuation", "new_speaker", "overlapping_voices"):
            raise ValueError("A P0 boundary remains unreviewed")
        if outcome.get("heard_on_original_audio") is not True:
            raise ValueError("P0 decision requires original sound")
    for batch in packet["sequential_one_pass_batches"]:
        for row in batch["reader_blocks"]:
            value = decision_roles[row["id"]]
            if (not isinstance(value, dict) or not isinstance(value.get("role"), str)
                or not value["role"].strip()
                or value.get("original_audio_voice_reviewed") is not True):
                raise ValueError("P1 role has no original-audio decision; UNIDENTIFIED VOICE is permitted")
            block_turn_segments(row, value)
    for value in decision_batches.values():
        if (not isinstance(value, dict)
            or value.get("synchronized_original_video_and_sound_reviewed") is not True
            or not isinstance(value.get("observed_original_film_playback_seconds"), (int, float))
            or isinstance(value.get("observed_original_film_playback_seconds"), bool)
            or not 8 <= value["observed_original_film_playback_seconds"] <= 1800
            or not isinstance(value.get("performance_notes"), list)
            or not isinstance(value.get("visible_props_and_wardrobe"), list)
            or not isinstance(value.get("observed_actor_action_target"), list)):
            raise ValueError("Original performance and picture coverage is incomplete")
    return {"episode_id": packet["episode_id"], "all_original_source_turn_boundaries_reviewed": True,
            "all_candidate_voices_source_listened": True, "all_sequential_av_batches_reviewed": True,
            "editorial_decisions_complete": True,
            "caveat": "Reviewer declarations, not automatic proof of audiovisual viewing."}


def render_reviewed_screenplay(packet: dict, decisions: dict) -> str:
    """One exact-caption reader from witnessed P0/P1 decisions and AV notes.

    Does not imply independent certification beyond the source-review
    declarations already checked by verify_decisions.
    """
    verify_decisions(packet, decisions)
    episode = packet["episode_id"]
    output = [
        f"# {episode}: Night Court (1984–1992), source-AV reviewed screenplay",
        "",
        "**Evidence tier:** reviewer-attested original synchronized playback; "
        "**independent second-editor audiovisual certification remains separate.** "
        "Do not mistake a machine-signed checklist for independent film acceptance.",
        "",
        "Original immutable dialogue SHA-256: "
        + packet["source_original_dialogue_sha256"],
        "Original film SHA-256: " + packet["original_video_sha256_expected"],
        "Canonical input manuscript SHA-256: " + packet["canonical_manuscript_sha256"],
        "Source viewing reviewer: " + decisions["reviewer"],
        "",
        "## Performed dialogue, delivery and stage business",
        "",
    ]
    prior_role = None
    index = 0
    for batch in packet["sequential_one_pass_batches"]:
        source_review = decisions["batches"][batch["id"]]
        for key, heading in (
            ("performance_notes", "Original soundtrack delivery"),
            ("visible_props_and_wardrobe", "Original picture: clothing and objects"),
            ("observed_actor_action_target", "Original moving-picture blocking")
        ):
            notes = source_review[key]
            if notes:
                output.append("*" + heading + ":*")
                for note in notes:
                    if not isinstance(note, str) or not note.strip() or len(note) > 800:
                        raise ValueError("Source AV note must be a bounded, useful observation")
                    output.append("* " + note.strip())
                output.append("")
        for row in batch["reader_blocks"]:
            pieces = block_turn_segments(row, decisions["roles"][row["id"]])
            caption = row["source_exact_dialogue"]
            for part_number, piece in enumerate(pieces):
                new_role = piece["role"]
                if index == 0 and part_number == 0:
                    change = True
                elif part_number > 0:
                    change = True  # Original source: true within-block P0 switch
                else:
                    result = decisions["boundaries"][f"B{index:04d}"]["result"]
                    change = result != "same_speaker_continuation"
                    if not change and new_role != prior_role:
                        raise ValueError("P0 same-voice continuation has conflicting P1 character names")
                if change:
                    output.extend(["", "### " + new_role, ""])
                exact_part = caption[piece["start"]:piece["end"]]
                output.extend("    " + textline for textline in exact_part.split("\n"))
                output.append("")
                prior_role = new_role
            index += 1
    if index != packet["source_reader_blocks"]:
        raise ValueError("Completed reader lost an original source block")
    return "\n".join(output).strip() + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--snapshot", type=Path, required=True)
    ap.add_argument("--episode", choices=(*EPISODES, "both"), required=True)
    ap.add_argument("--output", type=Path, required=True,
                    help="Stable destination directory; files overwritten in place, no vNN history")
    ap.add_argument("--s09-original-audio-locator", type=Path,
                    help="Existing SHAs-pinned untimed-source acoustic seek hints, NEVER original subtitle timings")
    ap.add_argument("--verify-decisions", type=Path,
                    help="Explicit signed human original-AV ledger for one episode")
    ap.add_argument("--render-reviewed-screenplay", action="store_true",
                    help="Render the ONE stable complete reader only after all source AV decisions validate")
    args = ap.parse_args()
    if args.render_reviewed_screenplay and not args.verify_decisions:
        ap.error("--render-reviewed-screenplay requires --verify-decisions")
    if args.verify_decisions and args.episode == "both":
        ap.error("Verify a single episode at a time")
    args.output.mkdir(parents=True, exist_ok=True)
    for ep in (EPISODES if args.episode == "both" else (args.episode,)):
        packet = make_packet(args.snapshot, ep,
                             args.s09_original_audio_locator if ep == "S09E19" else None)
        target = args.output / f"{ep}-one-pass-av-review.json"
        target.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", "utf-8")
        print(ep, "blocks", packet["source_reader_blocks"], "batches",
              packet["review_passes_required"], "P0 boundaries",
              len(packet["all_adjacent_boundary_questions"]), "no AV certifications")
        if args.verify_decisions:
            decision = json.loads(args.verify_decisions.read_text("utf-8"))
            print(json.dumps(verify_decisions(packet, decision), sort_keys=True))
            if args.render_reviewed_screenplay:
                final = render_reviewed_screenplay(packet, decision)
                target = args.output / f"{ep}-original-av-reviewed-screenplay.md"
                target.write_text(final, encoding="utf-8")
                print("reviewer-attested complete screenplay candidate:", target)


if __name__ == "__main__":
    main()
