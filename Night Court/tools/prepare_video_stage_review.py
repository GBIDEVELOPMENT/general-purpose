#!/usr/bin/env python3
"""Produce source-safe, editable original-video reviewer decisions from VLM output.

Never accepts a model claim. Default creates all ten questions for every
original-source window, including missing actions and props, so a reviewer
can identify omissions as well as hallucinations in one direct source pass.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import json
from pathlib import Path
import re

from run_headless_video_description import SCHEMA as MODEL_SCHEMA, FIELDS
from review_video_stage_directions import (
    DECISION_SCHEMA, valid_window, adjudicate,
)

SHA = re.compile(r"[0-9a-f]{64}\Z")
EPISODE = re.compile(r"S0[1-9]E[0-9]{2}\Z")
REVIEWER = re.compile(r"[A-Za-z0-9_.-]{1,80}\Z")
MAX_INPUT = 150_000
MAX_OUTPUT = 150_000
NOT_REVIEWED = "Pending direct original-source video review"


def prepare(model, model_sha, reviewer_id="editor-unassigned"):
    if not isinstance(model, dict) or model.get("schema") != MODEL_SCHEMA:
        raise ValueError("Expected a completed headless video-model report")
    episode = model.get("episode_id")
    digest = model.get("source_video_sha256")
    if not isinstance(episode, str) or not EPISODE.fullmatch(episode):
        raise ValueError("Unrecognized original episode")
    if not isinstance(digest, str) or not SHA.fullmatch(digest):
        raise ValueError("Invalid source video identity")
    if model.get("verified_source_sha256") != digest:
        raise ValueError("Original video SHA not verified before model run")
    if model.get("script_or_claim_independently_accepted") is not False:
        raise ValueError("Model cannot certify an episode")
    if not isinstance(model_sha, str) or not SHA.fullmatch(model_sha):
        raise ValueError("Invalid exact model report SHA")
    if not isinstance(reviewer_id, str) or not REVIEWER.fullmatch(reviewer_id):
        raise ValueError("Invalid proposed editor identifier")
    windows = model.get("windows")
    if not isinstance(windows, list) or not 1 <= len(windows) <= 12:
        raise ValueError("Expected bounded video review windows")
    ids, ordered, decisions = set(), [], []
    for window in windows:
        data = valid_window(model, window)
        wid = window["id"]
        if wid in ids:
            raise ValueError("Duplicate model window")
        ids.add(wid)
        ordered.append(window)
        for field in FIELDS:
            # The field must stay unaccepted until the reviewer sees original
            # picture; even if the model omitted it, the source may contain a
            # significant action that low-motion selection missed.
            decisions.append({
                "window_id": wid,
                "field": field,
                "verdict": "deferred",
                "source_window_ms": [window["start_ms"], window["end_ms"]],
                "direct_original_video_review_attested": False,
                "reviewer_text": None,
                "reason": NOT_REVIEWED,
            })
    ordered.sort(key=lambda w: (w["start_ms"], w["id"]))
    decisions.sort(key=lambda d: (next(w["start_ms"] for w in ordered if w["id"]==d["window_id"]),
                                  d["window_id"], FIELDS.index(d["field"])))
    output = {
        "schema": DECISION_SCHEMA,
        "episode_id": episode,
        "source_video_sha256": digest,
        "model_report_sha256": model_sha,
        "reviewer_id": reviewer_id,
        "decisions": decisions,
        "_editor_instructions": (
            "Verify actual synchronized original source at exact window times. "
            "For each field, choose accepted/corrected/rejected/deferred and a "
            "supporting source-attested decision. Never use the model text alone; "
            "set direct_original_video_review_attested=true only after viewing "
            "the matching original video. Accepted/corrected need reviewer_text; "
            "rejected/deferred need reason. Editing this file is a reviewer act."
        ),
        "_original_full_episode_independently_certified": False,
    }
    # The established reviewer bridge must accept the untouched template
    # without producing a single approved stage direction.
    derived = adjudicate(model, output, model_sha)
    if derived["editorial_stage_directions"] or derived["field_decisions_count"] != len(decisions):
        raise ValueError("Initial reviewer template is not safely deferred")
    return output, ordered


def review_priority_hints(field: str, claim: str):
    """Heuristic reviewer QUEUE labels only, never source-truth decisions."""
    if field not in FIELDS or not isinstance(claim, str):
        raise ValueError("Unknown field or model claim")
    if not claim.strip():
        return ["missing_model_observation"]
    text = claim.lower()
    flags = []
    if re.search(r"\b(may|might|possibly|perhaps|probably|likely|appears? to|seems? to)\b", text):
        flags.append("speculative_wording")
    if re.search(r"\b(listening|speaking|conversation|confrontation|tension|emotion|intently|preparing to|social gathering|motive|intent)\b", text):
        flags.append("motive_or_unverified_audio")
    if field == "props" or re.search(r"\b(pocket square|hairpin|glass of water|badge|ring|coin)\b", text):
        flags.append("inspect_fine_prop_identity")
    if re.search(r"\b(none|no one|no physical comedy|no one enters|no one exits|nothing happens)\b", text):
        flags.append("absence_requires_full_clip_review")
    if field in ("actions", "physical_comedy", "proposed_stage_direction") and re.search(
        r"\b(touch(?:es|ed|ing)?|reach(?:es|ed|ing)?|hand(?:s|ed|ing)?|"
        r"pass(?:es|ed|ing)?|give(?:s|n|ing)?|take(?:s|n|ing)?|"
        r"point(?:s|ed|ing)?|push(?:es|ed|ing)?|pull(?:s|ed|ing)?|"
        r"grab(?:s|bed|bing)?|place(?:s|d|ing)?|strike(?:s|n)?|"
        r"hold(?:s|ing)?|raise(?:s|d|ing)?)\b", text
    ):
        flags.append("verify_action_actor_and_recipient_from_original_moving_video")
    # A stage direction is never mechanically accepted even without flags.
    if field == "proposed_stage_direction":
        flags.append("never_copy_model_stage_prose_without_source_review")
    return flags if flags else ["normal_original_video_check"]


def escape_untrusted_markdown(text: str):
    """Render external model prose as plain words, never active MD/HTML links."""
    escaped = html.escape(str(text), quote=True)
    return re.sub(r"([\\`*_{}\[\]()#+!>|-])", r"\\\1", escaped)


def render_packet(model, ordered, template):
    lines = [
        "# Night Court source-video visual review packet",
        "",
        f"Episode: {template['episode_id']}",
        f"Original AVI SHA-256: {template['source_video_sha256']}",
        f"Exact model report SHA-256: {template['model_report_sha256']}",
        f"Review identifier: {template['reviewer_id']}",
        "",
        "**All fields deferred. No movie was viewed or action accepted by this generator.** "
        "Review the real source video and soundtrack directly. Use the accompanying "
        "decision JSON to record claims, corrections, rejections and omissions. "
        "The existing dialogue source and episode publication status are untouched.",
        "",
    ]
    for w in ordered:
        lines.extend([
            f"## {w['id']} · {w['start_ms']/1000:.3f}–{w['end_ms']/1000:.3f}s",
            "",
            f"Selection reason: {html.escape(str(w.get('selection_reason') or 'unclassified'))}",
            "",
            "Boundary is only a **candidate** cut-safe window, not an independently confirmed shot or dramatic scene.",
            ("Model temporal sampling: " + str(model.get("video_sampling_fps", "unknown"))
             + " fps (not full original source continuity); verify who initiates every gesture in the actual moving clip."),
            "",
        ])
        if w.get("status") == "requires_review":
            lines.extend([
                "Model output parser status: " + escape_untrusted_markdown(str(w.get("model_output_error") or "unknown")),
                "Model output token limit: " + str(model.get("max_generated_tokens", "unknown")) +
                "; do not assume token truncation without full generated-output evidence.",
                "Model response was invalid or incomplete, so no structured assertions were accepted.",
                "",
                "Untrusted model excerpt: " + escape_untrusted_markdown(str(w.get("model_response_excerpt") or "")[:800]),
                "",
            ])
        else:
            data = w.get("model_hypothesis") or {}
            for field in FIELDS:
                claim = data.get(field) or ""
                lines.append(f"- **{field}:** {escape_untrusted_markdown(claim or '[model did not describe]')}")
                lines.append("  - Review priorities (heuristic, not verdicts): " +
                             ", ".join(review_priority_hints(field, claim)))
            lines.append("")
        lines.append("Source-review tasks: confirm visible actions, omitted prop business, "
                     "entrances/exits, camera cuts, reactions and whether a proposed "
                     "stage direction is supportable. Do not identify actors from still images.")
        lines.append("")
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model-report", type=Path, required=True)
    p.add_argument("--decisions", type=Path, required=True)
    p.add_argument("--review-packet", type=Path)
    p.add_argument("--reviewer-id", default="editor-unassigned")
    args = p.parse_args()
    outputs = [args.decisions] + ([args.review_packet] if args.review_packet else [])
    if any(x.exists() or x.resolve() == args.model_report.resolve() for x in outputs):
        p.error("Refusing to overwrite model report or reviewer decisions")
    if len({x.resolve() for x in outputs}) != len(outputs):
        p.error("Review packet and decision output must be different")
    raw = args.model_report.read_bytes()
    if len(raw) > MAX_INPUT:
        raise ValueError("Oversized model report")
    model_sha = hashlib.sha256(raw).hexdigest()
    model = json.loads(raw)
    output, ordered = prepare(model, model_sha, args.reviewer_id)
    encoded = (json.dumps(output, indent=2, ensure_ascii=False) + "\n").encode()
    if len(encoded) > MAX_OUTPUT:
        raise ValueError("Decision template exceeds byte budget")
    args.decisions.parent.mkdir(parents=True, exist_ok=True)
    args.decisions.write_bytes(encoded)
    if args.review_packet:
        packet = render_packet(model, ordered, output)
        if len(packet.encode()) > MAX_OUTPUT:
            raise ValueError("Preview exceeds byte budget")
        args.review_packet.parent.mkdir(parents=True, exist_ok=True)
        args.review_packet.write_text(packet, encoding="utf-8")
    print(f"{output['episode_id']}: {len(ordered)} windows, {len(output['decisions'])} "
          "pending review questions, zero accepted stage directions")


if __name__ == "__main__":
    main()
