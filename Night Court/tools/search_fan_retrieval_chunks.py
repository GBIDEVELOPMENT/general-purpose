#!/usr/bin/env python3
"""Local-only lexical retrieval over private Night Court fan script chunks.

Search source-authenticated chunks with zero model downloads or network calls.
Returns a private response JSON with text; stdout deliberately prints only
counts, not copyrighted episode dialogue.
"""
from __future__ import annotations
import argparse
import collections
import json
import math
import re
import unicodedata
from pathlib import Path

SCHEMA = "night-court-private-fan-retrieval-chunks/1"
SEARCH_SCHEMA = "night-court-private-fan-retrieval-search/1"
STOP = frozenset(
    "a an and are as at be been but by can did do does for from had has have "
    "how i in into is it its me my of on or our s say so that the their them "
    "then there these this to was were what when where which who why with you "
    "your would about episode show night court character scene line said"
    .split()
)


def words(text: str) -> list[str]:
    plain = unicodedata.normalize("NFKD", text).casefold()
    plain = "".join(ch for ch in plain if not unicodedata.combining(ch))
    return [w for w in re.findall(r"[a-z0-9]+", plain) if len(w) > 1 and w not in STOP]


def load_records(path: Path) -> list[dict]:
    if not path.is_file():
        raise FileNotFoundError(path)
    records = []
    last_id = None
    current_episode = ""
    for index, line in enumerate(path.read_text("utf-8").splitlines(), 1):
        record = json.loads(line)
        if record.get("schema") != SCHEMA:
            raise ValueError(f"Unexpected retrieval schema at line {index}")
        ep = record.get("episode_id")
        rid = record.get("record_id")
        if not isinstance(ep, str) or not re.fullmatch(r"S\d{2}E\d{2}", ep):
            raise ValueError(f"Bad episode ID on record {index}")
        if not isinstance(rid, str) or not rid.startswith(ep + ":retrieval:"):
            raise ValueError(f"Bad record ID on record {index}")
        if not isinstance(record.get("retrieval_text"), str):
            raise ValueError(f"Missing source text on record {index}")
        if ep != current_episode:
            current_episode, last_id = ep, None
        if rid == last_id:
            raise ValueError("Duplicate consecutive retrieval record ID")
        last_id = rid
        records.append(record)
    if len({r["record_id"] for r in records}) != len(records):
        raise ValueError("Duplicated record IDs in retrieval source")
    if not records:
        raise ValueError("Empty retrieval corpus")
    return records


def score_records(records: list[dict], query: str, episode: str | None = None) -> list[tuple[float, int]]:
    terms = words(query)
    if not terms:
        raise ValueError("Search query has no significant words")
    if episode is not None and not re.fullmatch(r"S\d{2}E\d{2}", episode):
        raise ValueError("Episode filter must be SxxEyy")
    eligible = [
        (i, r) for i, r in enumerate(records)
        if episode is None or r["episode_id"] == episode
    ]
    if not eligible:
        return []
    descriptions = []
    lengths = []
    counts = []
    df = collections.Counter()
    for idx, r in eligible:
        # Build a stable score from actual text and a modest boost for
        # metadata; generic headings/preamble cannot eclipse true passages.
        tokens = words(r["retrieval_text"])
        tf = collections.Counter(tokens)
        counts.append((idx, tf))
        lengths.append(len(tokens))
        descriptions.append(words(r.get("episode_title", "") + " " + r.get("section_label", "")))
        df.update(set(tf))
    avgdl = sum(lengths) / max(1, len(lengths))
    ranked = []
    qtf = collections.Counter(terms)
    for pos, (idx, tf) in enumerate(counts):
        s = 0.0
        dl = lengths[pos]
        for token, qfreq in qtf.items():
            freq = tf.get(token, 0)
            if not freq:
                continue
            idf = math.log(1.0 + (len(eligible) - df[token] + .5) / (df[token] + .5))
            s += idf * ((freq * 2.2) / (freq + 1.2 * (0.25 + 0.75 * dl / max(1, avgdl))))
            s += idf * 0.20 * min(3, descriptions[pos].count(token))
            if qfreq > 1:
                s *= (1 + .025 * min(qfreq - 1, 3))
        if s > 0:
            ranked.append((round(s, 7), idx))
    return sorted(ranked, key=lambda x: (-x[0], records[x[1]]["record_id"]))


def search(records: list[dict], query: str, limit: int = 6, episode: str | None = None, neighbors: int = 1) -> dict:
    if not 1 <= limit <= 50:
        raise ValueError("Result limit must be 1..50")
    if not 0 <= neighbors <= 3:
        raise ValueError("Neighbor count must be 0..3")
    ranked = score_records(records, query, episode)
    selected = ranked[:limit]
    by_ep = collections.defaultdict(list)
    for record in records:
        by_ep[record["episode_id"]].append(record)
    position = {
        (r["episode_id"], r["record_id"]): i
        for ep, group in by_ep.items() for i, r in enumerate(group)
    }
    hits = []
    for score, i in selected:
        r = records[i]
        group = by_ep[r["episode_id"]]
        p = position[(r["episode_id"], r["record_id"])]
        context = [neighbor for neighbor in group[max(0, p - neighbors):p + neighbors + 1]
                   if neighbor["record_id"] != r["record_id"]]
        # Same-source repeated evidence must not be counted as independent.
        hits.append({
            "match_id": r["record_id"],
            "score": score,
            "episode_id": r["episode_id"],
            "episode_title": r["episode_title"],
            "script_sha256": r["script_sha256"],
            "caption_source_sha256": r["caption_source_sha256"],
            "evidence_tier": r["evidence_tier"],
            "speaker_names_verified": r["speaker_names_verified"],
            "whole_episode_av_certified": r["whole_episode_av_certified"],
            "source_text": r["retrieval_text"],
            "adjacent_source_context": [{
                "record_id": item["record_id"],
                "source_text": item["retrieval_text"]
            } for item in context],
        })
    return {
        "schema": SEARCH_SCHEMA,
        "query": query,
        "episode_filter": episode,
        "searched_chunks": len(records),
        "hits": hits,
        "warning": ("Retrieval chunks and adjacent context share source witnesses. "
                    "Speaker attribution and stage action remain provisional, "
                    "and source-only section headings are not verified film scenes.")
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, required=True,
                        help="Path to locally produced fan-retrieval-chunks.jsonl")
    parser.add_argument("--query", required=True)
    parser.add_argument("--output", type=Path, required=True,
                        help="Private JSON search result path; must not be in repository")
    parser.add_argument("--episode", default=None)
    parser.add_argument("--limit", type=int, default=6)
    parser.add_argument("--neighbors", type=int, default=1)
    options = parser.parse_args()
    source = options.corpus.resolve()
    target = options.output.resolve()
    if target == source:
        raise ValueError("Do not overwrite the source corpus")
    if target.is_relative_to(Path(__file__).resolve().parents[1]):
        raise ValueError("Result containing private episode text must be outside the Night Court repository")
    result = search(load_records(options.corpus), options.query, options.limit, options.episode, options.neighbors)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print(f"{len(result['hits'])} hits in {result['searched_chunks']} source chunks; results saved privately")


if __name__ == "__main__":
    main()
