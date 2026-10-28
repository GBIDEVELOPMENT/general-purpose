#!/usr/bin/env python3
"""Export private, labeled Night Court script chunks for fan-oriented retrieval.

This exporter creates NO new audiovisual claims. It uses the source-only
scaffolds for the series and provisional v5 screenplay readers for two pilots.
It does not download media, call models, or alter canonical sources.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PILOT_SCRIPTS = {
    "S01E01": "seasons/S01/S01E01/derived/additional-original-film-staged-reader-v5/screenplay-extra-observed-business.md",
    "S09E19": "seasons/S09/S09E19/derived/additional-original-film-staged-reader-v5/screenplay-extra-observed-business.md",
}
SCHEMA = "night-court-private-fan-retrieval-chunks/1"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_queue(root: Path) -> list[dict]:
    queue = json.loads((root / "catalog/av-script-reconstruction-queue.json").read_text("utf-8"))
    rows = queue["episodes"]
    if queue["original_episode_records"] != len(rows):
        raise ValueError("Episode queue count mismatch")
    if len({e["episode_id"] for e in rows}) != len(rows):
        raise ValueError("Duplicate episode in source queue")
    return sorted(rows, key=lambda e: e["episode_id"])


def select_script(root: Path, record: dict, v6_root: Path | None = None,
                  v7_root: Path | None = None,
                  v8_root: Path | None = None,
                  v9_root: Path | None = None,
                  v10_root: Path | None = None,
                  v11_root: Path | None = None,
                  v12_root: Path | None = None,
                  v13_root: Path | None = None,
                  patched_root: Path | None = None,
                  turn_root: Path | None = None,
                  s01_p0_root: Path | None = None,
                  working_pilot_root: Path | None = None,
                  factory_root: Path | None = None) -> tuple[Path, str]:
    episode = record["episode_id"]
    if factory_root is not None:
        # Current factory packages may cover just the researched subset:
        # S01E01, S01E02, S01E03, S05E05, S09E19 initially. Fallback to
        # old source-only scaffolds for any missing episode, never for a
        # malformed or stale existing package.
        base = factory_root.resolve()
        if not base.is_relative_to(root.resolve()):
            raise ValueError("Factory retrieval must use private in-repository output")
        folder = base / episode
        if folder.exists():
            path = (folder / "screenplay.md").resolve()
            manifest_path = (folder / "manifest.json").resolve()
            if (not folder.is_dir() or not path.is_relative_to(base)
                or not manifest_path.is_relative_to(base)
                or not path.is_file() or not manifest_path.is_file()):
                raise ValueError(episode + ": partial or unsafe script factory package")
            meta = json.loads(manifest_path.read_text("utf-8"))
            source = record["source_metadata"]
            if (meta.get("schema") != "night-court-one-click-script-factory/1"
                or meta.get("episode_id") != episode
                or meta.get("source_witness_sha256") != source["source_sha256"]
                or meta.get("original_dialogue_sha256") != source["source_sha256"]
                or meta.get("source_version_id") != source["source_version_id"]
                or meta.get("source_has_timecodes") is not source["timed"]
                or meta.get("dialogue_source_changed") is not False
                or meta.get("source_only_claims_never_promoted_to_av_truth") is not True
                or meta.get("actual_av_verified") is not False
                or not isinstance(meta.get("evidence_tier"), str)
                or meta.get("evidence_tier") not in (
                    "canonical_provisional_editorial_script",
                    "contextual_provisional_reading_draft", "source_only_reading_draft")
                or meta.get("script_sha256") != sha256(path.read_bytes())):
                raise ValueError(episode + ": stale, tampered, or AV-unaccepted factory source")
            return path, meta["evidence_tier"]
    if working_pilot_root is not None and episode in PILOT_SCRIPTS:
        path=(working_pilot_root / f"{episode}-working-screenplay.md").resolve()
        if not path.is_relative_to(working_pilot_root.resolve()) or not path.is_file():
            raise ValueError("Private current working screenplay not found")
        return path, "provisional_source_first_chronological_screenplay_layout"
    if s01_p0_root is not None and episode in PILOT_SCRIPTS:
        path=(s01_p0_root / f"{episode}-source-turns-v15.md").resolve()
        if not path.is_relative_to(s01_p0_root.resolve()) or not path.is_file():
            raise ValueError("Private S01 exact-caption speaking-turn reader missing")
        return path, "provisional_original_s01_dashed_reply_turn_v15"
    if turn_root is not None and episode in PILOT_SCRIPTS:
        path=(turn_root / f"{episode}-source-turn-amendments.md").resolve()
        if not path.is_relative_to(turn_root.resolve()) or not path.is_file():
            raise ValueError("Private original source turn-amendment manuscript missing")
        return path, "provisional_original_source_turn_amendment_reader"
    if patched_root is not None and episode in PILOT_SCRIPTS:
        path=(patched_root / f"{episode}-source-role-patches.md").resolve()
        if not path.is_relative_to(patched_root.resolve()) or not path.is_file():
            raise ValueError("Private source-role amendment reader is missing")
        return path, "provisional_source_role_amendments"
    if v13_root is not None and episode in PILOT_SCRIPTS:
        path=(v13_root / f"{episode}-source-turns-v13.md").resolve()
        if not path.is_relative_to(v13_root.resolve()) or not path.is_file():
            raise ValueError("Private S09 exact-source dialogue handoff v13 reader unavailable")
        return path, "provisional_original_source_split_roles_v13"
    if v12_root is not None and episode in PILOT_SCRIPTS:
        path=(v12_root / f"{episode}-source-roles-v12.md").resolve()
        if not path.is_relative_to(v12_root.resolve()) or not path.is_file():
            raise ValueError("Private latest source-backed S09 high-context speaker reader missing")
        return path, "provisional_original_episode_scene_context_reader_v12"
    if v11_root is not None and episode in PILOT_SCRIPTS:
        path=(v11_root / f"{episode}-source-turns-v11.md").resolve()
        if not path.is_relative_to(v11_root.resolve()) or not path.is_file():
            raise ValueError("Private mixed-speaker original-S09 v11 manuscript missing")
        return path, "provisional_source_mixed_voice_reader_v11"
    if v10_root is not None and episode in PILOT_SCRIPTS:
        path = (v10_root / f"{episode}-source-turns-v10.md").resolve()
        if not path.is_relative_to(v10_root.resolve()) or not path.is_file():
            raise ValueError("Private S09 source-turn reunion v10 reader missing")
        return path, "provisional_source_turn_reunion_v10"
    if v9_root is not None and episode in PILOT_SCRIPTS:
        path = (v9_root / f"{episode}-source-speaker-v9.md").resolve()
        if not path.is_relative_to(v9_root.resolve()) or not path.is_file():
            raise ValueError("Private actual original S09 source-acoustic v9 reader unavailable")
        return path, "provisional_original_s09_audio_speaker_reader_v9"
    if v8_root is not None and episode in PILOT_SCRIPTS:
        path = (v8_root / f"{episode}-source-speaker-v8.md").resolve()
        if not path.is_relative_to(v8_root.resolve()) or not path.is_file():
            raise ValueError("Private source-acoustic speaker-v8 source reader unavailable")
        return path, "provisional_original_source_acoustic_speaker_reader_v8"
    if v7_root is not None and episode in PILOT_SCRIPTS:
        path = (v7_root / f"{episode}-private-speaker-first-v7.md").resolve()
        if not path.is_relative_to(v7_root.resolve()) or not path.is_file():
            raise ValueError("Private speaker-v7 source reader unavailable")
        return path, "provisional_original_source_speaker_reader_v7"
    if v6_root is not None and episode in PILOT_SCRIPTS:
        path = (v6_root / episode / "screenplay-external-speakers-v6.md").resolve()
        if not path.is_relative_to(v6_root.resolve()):
            raise ValueError("Invalid private pilot reader path")
        if not path.is_file():
            raise FileNotFoundError("Speaker-v6 private source reader missing: " + episode)
        return path, "provisional_external_quote_speaker_reader_v6"
    tier = "provisional_filmed_staging_working_script" if episode in PILOT_SCRIPTS else "source_only_dialogue_scaffold"
    rel = PILOT_SCRIPTS.get(episode) or record["source_metadata"]["source_only_script"]
    path = (root / rel).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Unsafe path outside Night Court root")
    if not path.is_file():
        raise FileNotFoundError(f"Required existing script not found: {rel}")
    return path, tier


def section_heading(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("### "):
            return line[4:].strip()
    return "Unheaded source section"


def partition_sections(document: str) -> list[str]:
    """Keep every character, including preamble, in document order."""
    markers = [m.start() for m in re.finditer(r"(?m)^### ", document)]
    if not markers:
        return [document]
    cuts = [0] + markers + [len(document)]
    # When the first heading is at byte zero, avoid an empty section.
    return [document[a:b] for a, b in zip(cuts, cuts[1:]) if a != b]


def chunk_section(section: str, maximum: int) -> list[str]:
    """Prefer paragraph boundaries; long indivisible paragraphs can overflow."""
    if maximum < 200:
        raise ValueError("Chunk size must be >= 200 characters")
    pieces = []
    remaining = section
    while remaining:
        if len(remaining) <= maximum:
            pieces.append(remaining)
            break
        candidate = remaining.rfind("\n\n", int(maximum * .45), maximum)
        if candidate >= 0:
            boundary = candidate + 2
        else:
            # Do not split a speaker utterance or a short stage-direction
            # paragraph in half solely to hit a token/character quota.
            later = remaining.find("\n\n", maximum)
            boundary = later + 2 if later >= 0 else len(remaining)
        if boundary <= 0:
            raise ValueError("Chunker failed to advance")
        pieces.append(remaining[:boundary])
        remaining = remaining[boundary:]
    if "".join(pieces) != section:
        raise AssertionError("Source section was not preserved")
    return pieces


def export(root: Path, out_dir: Path, pilot_only: bool = False, max_chars: int = 3600,
           v6_root: Path | None = None, v7_root: Path | None = None,
           v8_root: Path | None = None,
           v9_root: Path | None = None,
           v10_root: Path | None = None,
           v11_root: Path | None = None,
           v12_root: Path | None = None,
           v13_root: Path | None = None,
           patched_root: Path | None = None,
           turn_root: Path | None = None,
           s01_p0_root: Path | None = None,
           working_pilot_root: Path | None = None,
           factory_root: Path | None = None) -> dict:
    if max_chars < 200:
        raise ValueError("Chunk size must be >= 200 characters")
    if out_dir.resolve().is_relative_to(root.resolve()):
        raise ValueError("Private retrieval output must be outside the Night Court source tree")
    if sum(x is not None for x in (v6_root,v7_root,v8_root,v9_root,v10_root,v11_root,v12_root,v13_root,patched_root,turn_root,s01_p0_root,working_pilot_root,factory_root))>1:
        raise ValueError("Choose one speaker reader source per pilot")
    rows = read_queue(root)
    if working_pilot_root is not None:
        working_report=json.loads((working_pilot_root/"working-screenplay-layout-manifest.json").read_text("utf-8"))
        counts=working_report.get("source_unit_counts")
        version=working_report.get("schema")
        editorial = "current_editorial_reader_sha256" in working_report
        expected = (working_report["source_unit_counts"] if editorial else
                    {"original_source_units":751,"named_provisional":651 if version.endswith("/2") else 621,
                     "unknown":100 if version.endswith("/2") else 130})
        blocks = ([405,323] if editorial else [405,322] if version.endswith("/2") else [405,321])
        if editorial:
            integration=json.loads((working_pilot_root/"pilot-current-editorial-manifest.json").read_text("utf-8"))
            if (integration.get("current_editorial_reader_sha256") != working_report["current_editorial_reader_sha256"]
                or integration.get("original_source_units") != 751
                or integration.get("provisional_reader_blocks") != 728
                or integration.get("named_provisional") != counts["named_provisional"]
                or integration.get("units_with_unknown_voice") != counts["unknown"]
                or integration.get("AV_accepted_actors") != 0
                or integration.get("AV_accepted_performed_turns") != 0):
                raise ValueError("Private current episode editorial evidence drift")
        if (version not in ("night-court-private-pilot-screenplay-layout/1","night-court-private-pilot-screenplay-layout/2")
            or counts!=expected
            or set(working_report.get("episodes",{}))!=set(PILOT_SCRIPTS)
            or working_report.get("new_independently_verified_actor_voices")!=0
            or working_report.get("new_independently_verified_performed_turns")!=0
            or working_report.get("scene_review_complete") is not False
            or not re.fullmatch(r"[0-9a-f]{64}",working_report.get("source_v15_reader_sha256",""))
            or [working_report["episodes"][ep].get("source_blocks") for ep in PILOT_SCRIPTS]!=blocks
            or [working_report["episodes"][ep].get("source_units") for ep in PILOT_SCRIPTS]!=[404,347]
            or working_report["episodes"]["S09E19"].get("original_caption_timed") is not False):
            raise ValueError("Private current working screenplay layout source/identity provenance failed")
    if s01_p0_root is not None:
        s01_p0_report=json.loads((s01_p0_root/"pilot-source-episode-turns-v15-manifest.json").read_text("utf-8"))
        if (s01_p0_report.get("original_caption_source_units")!=751
            or s01_p0_report.get("provisional_named_original_source_units")!=621
            or s01_p0_report.get("original_source_units_still_UNKNOWN")!=130
            or s01_p0_report.get("current_provisional_speaking_blocks")!=726
            or s01_p0_report.get("new_original_actor_identities_certified")!=0
            or s01_p0_report.get("source_cue_timing_is_not_performer_turn_timing") is not True
            or s01_p0_report.get("all_original_source_characters_preserved_exactly") is not True):
            raise ValueError("Private S01 first-episode P0 source turn incorrectly certified")
    if turn_root is not None:
        turn_report=json.loads((turn_root/"pilot-source-turn-amendments-manifest.json").read_text("utf-8"))
        if (turn_report.get("original_caption_source_units")!=751
            or turn_report.get("named_original_source_units")!=621
            or turn_report.get("unknown_original_source_units")!=130
            or turn_report.get("new_provisional_reader_turn_blocks")!=725
            or turn_report.get("original_source_exact_text_preserved") is not True
            or turn_report.get("source_new_performer_identifications_AV_certified")!=0
            or turn_report.get("source_new_turn_boundaries_AV_verified")!=0):
            raise ValueError("Original source turn amended P0 actor/turn evidence status drift")
    if patched_root is not None:
        patched_report=json.loads((patched_root / "pilot-source-role-amendments-manifest.json").read_text("utf-8"))
        if (patched_report.get("original_held_source_caption_units")!=751
            or not 613<=patched_report.get("provisionally_named_source_units",0)<=751
            or patched_report.get("unknown_original_source_units")!=751-patched_report["provisionally_named_source_units"]
            or patched_report.get("source_reading_blocks")!=718
            or patched_report.get("source_character_roles_independently_verified_via_AV")!=0
            or patched_report.get("source_original_cue_text_and_part_membership_unchanged") is not True):
            raise ValueError("Private amended original source role status incorrectly certified")
    if v13_root is not None:
        v13_report=json.loads((v13_root / "pilot-source-dialogue-turns-v13-manifest.json").read_text("utf-8"))
        if (v13_report.get("original_held_caption_units")!=751
            or v13_report.get("provisionally_named_original_caption_units")!=613
            or v13_report.get("unidentified_original_caption_units")!=138
            or v13_report.get("new_provisional_speaking_turns")!=718
            or v13_report.get("source_audio_actor_identities_or_true_turns_independently_verified")!=0
            or v13_report.get("all_source_character_spans_reversible") is not True):
            raise ValueError("Private S09 source-span actor handoff v13 status misrepresented")
    if v12_root is not None:
        v12_report=json.loads((v12_root / "pilot-original-speaker-context-v12-manifest.json").read_text("utf-8"))
        if (v12_report.get("original_caption_source_units")!=751
            or v12_report.get("current_provisional_character_named_original_units")!=610
            or v12_report.get("still_unknown_original_source_units")!=141
            or v12_report.get("current_original_speaker_reading_blocks")!=716
            or v12_report.get("new_original_caption_parts_with_working_names")!=15
            or v12_report.get("original_soundtrack_actor_identities_independently_reviewed_and_accepted")!=0
            or v12_report.get("original_S09_source_still_untimed") is not True):
            raise ValueError("Latest original episode contextual speaker working reader falsely certified")
    if v11_root is not None:
        v11_report=json.loads((v11_root / "pilot-current-multi-voice-turns-v11-manifest.json").read_text("utf-8"))
        if (v11_report.get("original_caption_units")!=751
            or v11_report.get("provisional_named_original_units")!=595
            or v11_report.get("original_units_remaining_unknown")!=156
            or v11_report.get("private_provisional_reading_turn_blocks_after")!=716
            or v11_report.get("actual_audio_review_performed") is not False
            or v11_report.get("potential_character_voice_and_turn_verifications_from_actual_original_av")!=0
            or v11_report.get("original_source_fully_reconstructable_via_unicode_spans") is not True):
            raise ValueError("Incorrect current original film mixed-speaker v11 source status")
    if v10_root is not None:
        v10_report = json.loads((v10_root / "pilot-current-source-turns-v10-manifest.json").read_text("utf-8"))
        if (v10_report.get("original_caption_immutable_source_units")!=751
            or v10_report.get("current_provisional_character_named_original_units")!=591
            or v10_report.get("still_unknown_original_source_units")!=160
            or v10_report.get("reader_speaker_turn_blocks_after")!=715
            or v10_report.get("source_audio_human_actor_identity_confirmations_added")!=0
            or v10_report.get("source_single_sentence_still_not_verified_performance_turn") is not True):
            raise ValueError("Private v10 actual original cue turn status not verified")
    if v9_root is not None:
        v9_report = json.loads((v9_root / "pilot-current-speaker-s09-audio-v9-manifest.json").read_text("utf-8"))
        if (v9_report.get("original_source_caption_units")!=751
            or v9_report.get("current_working_named_provisional_original_units")!=590
            or v9_report.get("unidentified_original_cue_units")!=161
            or v9_report.get("quarantined_suspicious_model_proposals")!=1
            or v9_report.get("original_audio_human_identified_characters_added")!=0):
            raise ValueError("Incorrect original-S09-v9 speaker reader status")
    if v8_root is not None:
        v8_report = json.loads((v8_root / "pilot-original-acoustic-speaker-manifest.json").read_text("utf-8"))
        if (v8_report.get("original_source_caption_units")!=751
            or v8_report.get("source_units_with_provisional_names")!=587
            or v8_report.get("original_units_still_unknown")!=164
            or v8_report.get("source_speaker_identities_human_verified_by_pass")!=0):
            raise ValueError("Untrusted private source voice-v8 report")
    if v7_root is not None:
        v7_report = json.loads((v7_root / "pilot-contextual-speaker-manifest.json").read_text("utf-8"))
        if (v7_report.get("source_units_total") != 751
            or v7_report.get("source_units_provisionally_named") != 583
            or v7_report.get("source_units_unknown") != 168
            or v7_report.get("audio_confirmed_by_this_pass") != 0
            or v7_report.get("all_identity_statuses_are_provisional") is not True):
            raise ValueError("Untrusted private speaker-v7 source report")
    if v6_root is not None:
        report = json.loads((v6_root / "speaker-improvement-manifest.json").read_text("utf-8"))
        if (report.get("original_source_speaking_units") != 751
            or report.get("new_provisional_named_source_units") != 490
            or report.get("remaining_unidentified_source_units") != 261
            or report.get("original_audio_speaker_identities_verified_by_this_change") != 0):
            raise ValueError("Untrusted private speaker-v6 reader manifest")
    if pilot_only:
        rows = [e for e in rows if e["episode_id"] in PILOT_SCRIPTS]
        if len(rows) != len(PILOT_SCRIPTS):
            raise ValueError("Both pilot episodes must exist")
    if not rows:
        raise ValueError("Empty source episode queue")
    records = []
    manifest_episodes = []
    for entry in rows:
        episode = entry["episode_id"]
        source_sha = entry["source_metadata"]["source_sha256"]
        if not re.fullmatch(r"[0-9a-f]{64}", source_sha):
            raise ValueError(f"Invalid source SHA: {episode}")
        path, tier = select_script(root, entry, v6_root, v7_root, v8_root, v9_root, v10_root, v11_root, v12_root, v13_root, patched_root, turn_root, s01_p0_root, working_pilot_root, factory_root)
        is_factory = factory_root is not None and path.is_relative_to(factory_root.resolve())
        content = path.read_bytes()
        document = content.decode("utf-8")
        if source_sha not in document:
            raise ValueError(f"Script not linked to expected original caption SHA: {episode}")
        # S09 editor v17 deliberately heads its own complete episode reader
        # with the show name first. Require exact episode identity nonetheless.
        title = document.lstrip()
        if not (title.startswith("# " + episode)
                or (is_factory and episode in title.splitlines()[0])
                or (working_pilot_root is not None and episode == "S09E19"
                    and (title.startswith("# Night Court (1984–1992) • S09E19:")
                          or title.startswith("# Night Court (1984–1992), S09E19:")))):
            raise ValueError(f"Wrong episode script: {episode}")
        for named_season in re.findall(r"\bThe (S\d{2}) original\b", document[:1800]):
            if named_season != episode[:3]:
                raise ValueError(f"Wrong-season pilot prose in {episode} reader header: {named_season}")
        if episode == "S09E19" and entry["source_metadata"]["timed"]:
            raise ValueError("Untimed S09 original witness erroneously marked timed")
        if is_factory:
            rel_path = str(path.relative_to(root.resolve()))
        elif working_pilot_root is not None and episode in PILOT_SCRIPTS:
            expected_sha=working_report["manuscript_sha256"][episode]
            if sha256(content)!=expected_sha:
                raise ValueError("Private current chronological pilot screenplay SHA mismatch")
            rel_path="private-current-working-screenplays/"+path.name
        elif s01_p0_root is not None and episode in PILOT_SCRIPTS:
            expected_sha=s01_p0_report["private_source_manuscripts_sha256"][episode]
            if sha256(content)!=expected_sha:
                raise ValueError("Original S01 source turn v15 manuscript source SHA mismatch")
            rel_path="private-source-turns-v15/"+path.name
        elif turn_root is not None and episode in PILOT_SCRIPTS:
            expected_sha = turn_report["private_reader_sha256_by_episode"][episode]
            if sha256(content)!=expected_sha:
                raise ValueError("Original speaker turn amendment script SHA differs")
            rel_path="private-source-turn-amendments/"+path.name
        elif patched_root is not None and episode in PILOT_SCRIPTS:
            expected_sha = patched_report["manuscripts_sha256_by_episode"][episode]
            if sha256(content)!=expected_sha:
                raise ValueError("Private original role amendment script source hash mismatch")
            rel_path="private-source-role-patches/"+path.name
        elif v13_root is not None and episode in PILOT_SCRIPTS:
            expected_sha = v13_report["private_manuscript_sha256_by_episode"][episode]
            if sha256(content)!=expected_sha:
                raise ValueError("Original S09 two-voice exact-span screenplay SHA mismatch")
            rel_path="private-source-turns-v13/"+path.name
        elif v12_root is not None and episode in PILOT_SCRIPTS:
            expected_sha = v12_report["manuscripts_sha256_by_episode"][episode]
            if sha256(content)!=expected_sha:
                raise ValueError("Original S09 v12 contextual speaker manuscript SHA mismatch")
            rel_path="private-source-speakers-v12/"+path.name
        elif v11_root is not None and episode in PILOT_SCRIPTS:
            expected_sha = v11_report["private_manuscripts_sha256_by_episode"][episode]
            if sha256(content)!=expected_sha:
                raise ValueError("Private source mixed-voice v11 screenplay hash mismatch")
            rel_path = "private-source-turns-v11/" + path.name
        elif v10_root is not None and episode in PILOT_SCRIPTS:
            expected_sha = v10_report["generated_reader_sha256_by_episode"][episode]
            if sha256(content)!=expected_sha:
                raise ValueError("Private v10 source-turn screenplay hash mismatch")
            rel_path = "private-source-turns-v10/" + path.name
        elif v9_root is not None and episode in PILOT_SCRIPTS:
            expected_sha = v9_report["working_manuscript_sha256_by_episode"][episode]
            if sha256(content)!=expected_sha:
                raise ValueError("Private v9 source-acoustic screenplay hash mismatch")
            rel_path = "private-source-speaker-v9/" + path.name
        elif v8_root is not None and episode in PILOT_SCRIPTS:
            expected_sha = v8_report["source_reader_sha256_by_episode"][episode]
            if sha256(content) != expected_sha:
                raise ValueError("Private source-audio v8 speaker-first source text SHA mismatch")
            rel_path = "private-source-speaker-v8/" + path.name
        elif v7_root is not None and episode in PILOT_SCRIPTS:
            expected_sha = v7_report["generated_reader_sha256_by_episode"][episode]
            if sha256(content) != expected_sha:
                raise ValueError("Private v7 speaker-first script hash mismatch")
            rel_path = "private-source-speaker-v7/" + path.name
        elif v6_root is not None and episode in PILOT_SCRIPTS:
            verified = report["pilot_scripts"][episode]
            if (verified["sha256"] != sha256(content)
                or verified["generated_path"] != f"{episode}/screenplay-external-speakers-v6.md"):
                raise ValueError("Generated private speaker-v6 script SHA mismatch")
            rel_path = "private-source-speaker-v6/" + verified["generated_path"]
        else:
            rel_path = path.relative_to(root.resolve()).as_posix()
        parts = []
        for sec_index, section in enumerate(partition_sections(document), 1):
            heading = section_heading(section)
            for sub_index, text in enumerate(chunk_section(section, max_chars), 1):
                parts.append({
                    "schema": SCHEMA,
                    "episode_id": episode,
                    "episode_title": entry["title"],
                    "record_id": f"{episode}:retrieval:{len(parts)+1:04d}",
                    "section_index": sec_index,
                    "section_part": sub_index,
                    "section_label": heading,
                    "script_path": rel_path,
                    "script_sha256": sha256(content),
                    "caption_source_sha256": source_sha,
                    "dialogue_timed_original": bool(entry["source_metadata"]["timed"]),
                    "evidence_tier": tier,
                    "speaker_names_verified": False,
                    "whole_episode_av_certified": False,
                    "section_is_verified_visual_scene": False,
                    "retrieval_text": text,
                })
        if "".join(p["retrieval_text"] for p in parts) != document:
            raise AssertionError(f"Lossy retrieval export for {episode}")
        records.extend(parts)
        manifest_episodes.append({
            "episode_id": episode,
            "title": entry["title"],
            "evidence_tier": tier,
            "source_sha256": source_sha,
            "script_sha256": sha256(content),
            "script_path": rel_path,
            "chunks": len(parts),
            "source_characters": len(document),
        })
    out_dir.mkdir(parents=True, exist_ok=True)
    # Keep original dialog in the owner's designated local/private destination;
    # DO NOT commit the generated bulk corpus or upload to public endpoints.
    chunk_file = out_dir / "fan-retrieval-chunks.jsonl"
    chunk_file.write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in records), "utf-8")
    manifest = {
        "schema": SCHEMA,
        "scope": "original-1984-1992-only",
        "purpose": "private retrieval seed, not verified production screenplay",
        "episode_count": len(manifest_episodes),
        "chunk_count": len(records),
        "all_speakers_and_staging_provisional": True,
        "contains_original_source_dialogue": True,
        "do_not_publicly_redistribute": True,
        "episodes": manifest_episodes,
    }
    (out_dir / "fan-retrieval-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n", "utf-8"
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pilot-only", action="store_true")
    parser.add_argument("--max-chars", type=int, default=3600)
    parser.add_argument("--speaker-v6-root", type=Path, default=None,
                        help="Locally generated verified private v6 speaker manuscripts")
    parser.add_argument("--speaker-v7-root", type=Path, default=None,
                        help="Locally generated source-bound provisional v7 speaker manuscripts")
    parser.add_argument("--speaker-v8-root", type=Path, default=None,
                        help="Locally generated unverified original-acoustic-supported v8 speaker manuscripts")
    parser.add_argument("--speaker-v9-root", type=Path, default=None,
                        help="Current SHA-validated three S09 original-soundtrack contextual proposals")
    parser.add_argument("--speaker-v10-root", type=Path, default=None,
                        help="Private source-turn reunited two-cue S09 speaker working manuscripts")
    parser.add_argument("--speaker-v11-root", type=Path, default=None,
                        help="Private source-exact mixed-voice S09 C188-C192 candidate reader manuscripts")
    parser.add_argument("--speaker-v12-root", type=Path, default=None,
                        help="Private episode-context speaker v12 scripts, 610 tentative named source units")
    parser.add_argument("--speaker-v13-root", type=Path, default=None,
                        help="Private exact-original cue Harriet/Mac Dan/Harry Alex/Roz split-turn scripts")
    parser.add_argument("--speaker-patch-root", type=Path, default=None,
                        help="Generic private original-source role amendments, append-only ledger")
    parser.add_argument("--s01-p0-root", type=Path, default=None,
                        help="Private original S01 exact-source C219 dash reply role-turn reader")
    parser.add_argument("--source-turn-patch-root", type=Path, default=None,
                        help="Generic exact-source original paragraph speaker turn amendments")
    parser.add_argument("--working-pilot-root", type=Path, default=None,
                        help="Private v15 chronological readable screenplay outputs, 621 provisional names")
    parser.add_argument("--factory-root", type=Path, default=None,
                        help="Current SHA-checked stable screenplay factory packages; missing episodes fall back to source-only")
    options = parser.parse_args()
    result = export(options.root, options.output, options.pilot_only, options.max_chars,
                    options.speaker_v6_root, options.speaker_v7_root,
                    options.speaker_v8_root, options.speaker_v9_root,
                    options.speaker_v10_root, options.speaker_v11_root,
                    options.speaker_v12_root, options.speaker_v13_root,
                    options.speaker_patch_root, options.source_turn_patch_root,
                    options.s01_p0_root, options.working_pilot_root,
                    options.factory_root)
    print(f"Exported {result['chunk_count']} retrieval chunks from {result['episode_count']} episodes")


if __name__ == "__main__":
    main()
