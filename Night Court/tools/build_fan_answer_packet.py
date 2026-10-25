#!/usr/bin/env python3
"""Produce a private, ready-to-supply Night Court superfan LLM context packet.

Offline only: source evidence from the local SQLite database. The assistant
persona is a stylistic role, never a claim the actual system watched television.
"""
from __future__ import annotations
import argparse
import hashlib
from pathlib import Path

from fan_sqlite_index import ROOT, query as index_query

HEADER = """# Night Court (1984–1992): source-grounded fan response packet

## Answering instructions for the receiving LLM

Perform the role of an intensely knowledgeable, curious fan of the **original 1984–1992 Night Court**. Be specific, enjoyable and analytically engaged with the show, not a generic publicity blurb. This is a persona for conversation, not a claim about the assistant's real life or viewing experiences.

Use the retrieved evidence below, and separate three kinds rigorously:

1. **Original dialogue/script witness**: actual held caption text; timings and speaker names are not wholly validated. Source-only scaffold headings are subtitle-gap clusters, not certified scenes.
2. **Provisional character dialogue**: original text reproduced and source-SHA checked, but the named character is an editorial hypothesis; unknown voices stay unknown. Nearby same-role captions need not be one performance turn.
3. **Editorial comedy/story reading**: helpful interpretive analysis anchored to short exact original caption phrases, not audio-verified tone, identified actors or independently viewed physical movement.

Don't invent quotations, scenes, identities, comic intonation, props, running jokes, or production trivia absent from the evidence. Clarify uncertainty naturally rather than routinely reciting warnings. When a story point is supported but a specific voice or gesture is unknown, answer the supported portion. For a genuinely unsupported answer, say what material is missing. Do not conflate the 2023 revival or other sitcoms. A fan interpretation is welcome when explicitly recognizable as interpretation.

Use brief source references such as [S01E01 C209] or [S09E19 original paragraph 283] when precision matters; the labels below provide exact locators. The full quoted passage remains private to this prompt context. Avoid padding the response with repeated caveats.
"""


def snippet(text: str, budget: int) -> str:
    if len(text) <= budget:
        return text.strip()
    window = text[:budget]
    para = window.rfind("\n\n", max(50, budget // 2))
    if para >= 0:
        return window[:para].strip() + "\n[Longer source passage omitted from this packet]"
    return window.rstrip() + "\n[Passage truncated to retrieval budget]"


def build_packet(db: Path, question: str, episode: str | None = None,
                 role: str | None = None, hits_each: int = 4,
                 max_chars: int = 16000) -> str:
    if max_chars < 2500:
        raise ValueError("Minimum private prompt budget is 2500 characters")
    result = index_query(db, question, episode, role, hits_each)
    remaining = max_chars
    body = [HEADER, "\n## Actual user question\n\n" + question.strip() + "\n"]
    remaining -= sum(map(len, body))
    labels = (
        ("script_witness", "A. Original dialogue and working-script witness"),
        ("provisional_character_dialogue", "B. Provisional role-specific source dialogue"),
        ("editorial_comedy_and_story", "C. Interpretation grounded to source cue anchors"),
    )
    hits_used = 0
    for kind, heading in labels:
        blocks = ["\n## " + heading + "\n"]
        values = result["results_by_evidence_kind"].get(kind, [])
        if not values:
            blocks.append("\nNo matching records from this evidence category.\n")
        for hit in values:
            data = hit["evidence"]
            episode_id = data["episode_id"]
            if kind == "script_witness":
                provenance = (data["record_id"] + " · " + data["evidence_tier"] +
                              " · original caption SHA256 " + data["caption_source_sha256"])
                passage = data["retrieval_text"]
            elif kind == "provisional_character_dialogue":
                provenance = (
                    data["reading_block_id"] + " · " + (data.get("source_reading_ref") or ", ".join(data.get("original_source_part_refs", []))) +
                    " · role: " + (data["candidate_role"] or "UNIDENTIFIED") +
                    " · " + data["role_attribution_status"] +
                    " · original source SHA256 " + data["original_source_sha256"]
                )
                passage = data["caption_text"]
            else:
                evidence = ", ".join("C" + str(x["caption_cue"]) for x in data["source_anchor_evidence"])
                provenance = (data["id"] + " · cues: " + evidence +
                              " · source SHA256 " + data["source_witness_sha256"])
                passage = (
                    "Title: " + data["title"] + "\nSetup: " + data["setup"] +
                    "\nPayoff: " + data["payoff"] +
                    "\nEditorial interpretation: " + data["interpretation"] +
                    "\nMechanisms (interpretive): " + ", ".join(data["mechanisms"])
                )
            intro = f"\n### {episode_id} · {provenance}\n\n"
            allowance = min(1350, max(0, remaining - len(intro) - 80))
            if allowance < 120:
                break
            portion = intro + snippet(passage, allowance) + "\n"
            blocks.append(portion)
            remaining -= len(portion)
            hits_used += 1
        body.extend(blocks)
        remaining -= len(blocks[0]) + (len(blocks[1]) if not values else 0)
    if hits_used == 0:
        body.append("\nNo relevant source evidence was retrieved; do not fabricate an episode answer.\n")
    body.append("\n## Answer now\n\nRespond to the actual question in the requested fan persona, with conclusions grounded in the evidence above. If a source quote or performance claim is uncertain, avoid false certainty.\n")
    response = "".join(body)
    if len(response) > max_chars:
        # Retain the question and direct evidence rather than publishing an
        # overbudget/partially chopped prompt as if complete.
        raise ValueError("Prompt exceeded bounded budget; reduce --hits or raise --max-chars")
    return response


def save_packet(db: Path, question: str, target: Path, **kwargs) -> dict:
    if target.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError("Prompt includes private transcript passages; keep it outside the repository")
    if target.resolve() == db.resolve():
        raise ValueError("Do not overwrite the database")
    packet = build_packet(db, question, **kwargs)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(packet, "utf-8")
    return {
        "packet_sha256": hashlib.sha256(packet.encode("utf-8")).hexdigest(),
        "characters": len(packet),
        "contains_private_source_dialogue": True,
        "generated_answer": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--question", required=True)
    parser.add_argument("--episode")
    parser.add_argument("--role")
    parser.add_argument("--hits", type=int, default=4)
    parser.add_argument("--max-chars", type=int, default=16000)
    parser.add_argument("--output", type=Path, required=True)
    a = parser.parse_args()
    report = save_packet(a.database, a.question, a.output, episode=a.episode,
                         role=a.role, hits_each=a.hits, max_chars=a.max_chars)
    print(f"Private fan answer packet prepared ({report['characters']} chars); "
          "no source passage printed, no model called")


if __name__ == "__main__":
    main()
