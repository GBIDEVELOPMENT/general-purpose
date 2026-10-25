#!/usr/bin/env python3
"""Review model-proposed visible staging into separate, source-linked editorial notes.

This script NEVER certifies an episode, identifies a performer, alters source
captions, or accepts model output without an explicit reviewer decision.
Review signatures are statements of reviewer action, not cryptographic proof.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

from run_headless_video_description import FIELDS, SCHEMA as MODEL_SCHEMA

SCHEMA = "night-court-reviewed-visual-staging/1"
DECISION_SCHEMA = "night-court-visual-review-decisions/1"
SHA = re.compile(r"[0-9a-f]{64}\Z")
ID = re.compile(r"[A-Za-z0-9_.-]{1,80}\Z")
VERDICTS = ("accepted", "corrected", "rejected", "deferred")
MAX_BYTES = 150_000
MAX_DECISIONS = 120


def file_sha(raw):
    return hashlib.sha256(raw).hexdigest()


def check_sha(value, name):
    if not isinstance(value, str) or not SHA.fullmatch(value):
        raise ValueError(f"Invalid {name}")
    return value


def valid_window(model, window):
    if not isinstance(window, dict) or not ID.fullmatch(str(window.get("id", ""))):
        raise ValueError("Invalid model window")
    times = (window.get("start_ms"), window.get("end_ms"))
    duration = model.get("duration_ms")
    if not all(type(t) is int for t in times) or type(duration) is not int:
        raise ValueError("Invalid model timestamps")
    if not 0 <= times[0] < times[1] <= duration:
        raise ValueError("Model window escapes source runtime")
    if window.get("independently_accepted") is not False or window.get("source_AV_human_review_done") is not False:
        raise ValueError("Unreviewed input claims visual acceptance")
    if window.get("candidate_cut_crossing") is not False:
        raise ValueError("Cross-cut or unknown-cut original sequence")
    if window.get("status") not in ("machine_proposed", "requires_review"):
        raise ValueError("Only original video model reports may be reviewed")
    data = window.get("model_hypothesis")
    if data is not None:
        if not isinstance(data, dict) or set(data) != set(FIELDS):
            raise ValueError("Unexpected model proposal schema")
        if any(not isinstance(v, str) or len(v) > 1200 for v in data.values()):
            raise ValueError("Unsafe model proposal field")
    return data


def adjudicate(model, decisions, model_hash):
    if not isinstance(model, dict) or model.get("schema") != MODEL_SCHEMA:
        raise ValueError("Expected an actual model-run evidence report")
    if model.get("script_or_claim_independently_accepted") is not False:
        raise ValueError("Input falsely asserts episode acceptance")
    episode = model.get("episode_id")
    if not isinstance(episode, str) or not re.fullmatch(r"S0[1-9]E[0-9]{2}", episode):
        raise ValueError("Invalid original-series episode")
    video_sha = check_sha(model.get("source_video_sha256"), "source video SHA")
    if model.get("verified_source_sha256") != video_sha:
        raise ValueError("Model report lacks independently checked source hash")
    if not isinstance(decisions, dict) or decisions.get("schema") != DECISION_SCHEMA:
        raise ValueError("Expected reviewer decision document")
    if decisions.get("episode_id") != episode or decisions.get("source_video_sha256") != video_sha:
        raise ValueError("Reviewer document source mismatch")
    if decisions.get("model_report_sha256") != model_hash:
        raise ValueError("Reviewer document is for a different model report")
    reviewer = decisions.get("reviewer_id")
    if not isinstance(reviewer, str) or not ID.fullmatch(reviewer):
        raise ValueError("Reviewer audit identifier required")
    entries = model.get("windows")
    if not isinstance(entries, list) or not 1 <= len(entries) <= 12:
        raise ValueError("Invalid original-source review window count")
    windows = {}
    for row in entries:
        valid_window(model, row)
        if row["id"] in windows:
            raise ValueError("Repeated model window")
        windows[row["id"]] = row
    review_rows = decisions.get("decisions")
    if not isinstance(review_rows, list) or len(review_rows) > MAX_DECISIONS:
        raise ValueError("Unbounded or missing reviewer decisions")
    seen = set()
    audited, accepted_staging = [], []
    for decision in review_rows:
        if not isinstance(decision, dict):
            raise ValueError("Bad reviewer decision")
        ident = decision.get("window_id")
        field = decision.get("field")
        verdict = decision.get("verdict")
        if ident not in windows or field not in FIELDS or verdict not in VERDICTS:
            raise ValueError("Unknown video window, field or verdict")
        key = (ident, field)
        if key in seen:
            raise ValueError("Duplicate reviewer decision")
        seen.add(key)
        row = windows[ident]
        times = decision.get("source_window_ms")
        if times != [row["start_ms"], row["end_ms"]]:
            raise ValueError("Reviewer source time-window mismatch")
        attested = decision.get("direct_original_video_review_attested")
        if type(attested) is not bool:
            raise ValueError("Explicit original-video review attestation required")
        if verdict in ("accepted", "corrected", "rejected") and attested is not True:
            raise ValueError("Source review is required to accept/correct/reject")
        reviewer_text = decision.get("reviewer_text")
        reason = decision.get("reason")
        if verdict in ("accepted", "corrected"):
            if not isinstance(reviewer_text, str) or not 1 <= len(reviewer_text.strip()) <= 1200:
                raise ValueError("Accepted notes need explicit reviewer-authored text")
        elif reviewer_text is not None:
            raise ValueError("Rejected/deferred model observation cannot supply accepted prose")
        if verdict in ("rejected", "deferred") and (not isinstance(reason, str) or not 1 <= len(reason.strip()) <= 500):
            raise ValueError("Rejected/deferred outcome needs a reason")
        hypothesis = (row.get("model_hypothesis") or {}).get(field)
        if verdict == "accepted" and not hypothesis:
            raise ValueError("Cannot accept an absent model observation")
        provenance = {
            "window_id": ident, "field": field, "verdict": verdict,
            "source_video_sha256": video_sha,
            "source_window_ms": times,
            "model_proposal": hypothesis,
            "reviewer_text": reviewer_text,
            "reason": reason,
            "direct_original_video_review_attested": attested,
            "reviewer_id": reviewer,
            "shot_partition_independently_verified": False,
            "independent_episode_certification": False,
        }
        audited.append(provenance)
        if field == "proposed_stage_direction" and verdict in ("accepted", "corrected"):
            accepted_staging.append({
                "window_id": ident,
                "start_ms": row["start_ms"], "end_ms": row["end_ms"],
                "text": reviewer_text.strip(), "reviewer_decision": verdict,
                "reviewer_id": reviewer,
                "source_video_sha256": video_sha,
                "evidence_status": "reviewer_attested_source_video_not_independently_certified",
            })
    audited.sort(key=lambda x: (windows[x["window_id"]]["start_ms"], x["window_id"], FIELDS.index(x["field"])))
    accepted_staging.sort(key=lambda x: (x["start_ms"], x["window_id"]))
    counts = Counter(x["verdict"] for x in audited)
    return {
        "schema": SCHEMA, "episode_id": episode,
        "source_video_sha256": video_sha,
        "model_report_sha256": model_hash, "reviewer_id": reviewer,
        "model_proposed_window_count": len(windows),
        "field_decisions_count": len(audited),
        "unreviewed_field_count": len(windows) * len(FIELDS) - len(audited),
        "decision_counts": {v: counts[v] for v in VERDICTS},
        "field_decisions": audited,
        "editorial_stage_directions": accepted_staging,
        "full_episode_av_certified": False,
        "source_caption_or_dialogue_modified": False,
        "model_outputs_were_not_automatically_accepted": True,
        "notice": "Editorial original-video review statements require independent corroboration before archival publication.",
    }


def render_editorial_appendix(report):
    lines = [
        f"# {report['episode_id']} reviewer-attested visual staging appendix",
        "",
        "Source video SHA-256: " + report["source_video_sha256"],
        "Model report SHA-256: " + report["model_report_sha256"],
        "No original dialogue is changed; none of these passages independently certifies the episode.",
        "",
    ]
    for row in report["editorial_stage_directions"]:
        start = row["start_ms"] / 1000
        end = row["end_ms"] / 1000
        lines.extend([
            f"## {start:.3f}s–{end:.3f}s | {row['window_id']}",
            "",
            row["text"],
            "",
            f"_Reviewer-attested {row['reviewer_decision']}; independently unverified archival status._",
            "",
        ])
    if not report["editorial_stage_directions"]:
        lines.extend(["No accepted original-video stage directions yet.", ""])
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model-report", required=True, type=Path)
    p.add_argument("--decisions", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--appendix", type=Path)
    args = p.parse_args()
    inputs = (args.model_report, args.decisions)
    destinations = [args.output] + ([args.appendix] if args.appendix else [])
    if any(out.exists() or out.resolve() in (src.resolve() for src in inputs) for out in destinations):
        p.error("Refusing to overwrite evidence or existing source")
    if len(set(path.resolve() for path in destinations)) != len(destinations):
        p.error("JSON and appendix outputs must be separate files")
    raw_model = args.model_report.read_bytes()
    raw_review = args.decisions.read_bytes()
    if len(raw_model) > MAX_BYTES or len(raw_review) > MAX_BYTES:
        p.error("Oversize original-video review material")
    report = adjudicate(json.loads(raw_model), json.loads(raw_review), file_sha(raw_model))
    report["review_decisions_sha256"] = file_sha(raw_review)
    encoded = (json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode()
    if len(encoded) > MAX_BYTES:
        raise ValueError("Review output exceeds budget")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(encoded)
    if args.appendix:
        args.appendix.parent.mkdir(parents=True, exist_ok=True)
        args.appendix.write_text(render_editorial_appendix(report), encoding="utf-8")
    print(f"{report['episode_id']}: {len(report['editorial_stage_directions'])} "
          "reviewer-attested staging notes; 0 certified episodes")


if __name__ == "__main__":
    main()
