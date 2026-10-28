#!/usr/bin/env python3
"""Local-only lexical retrieval over private Night Court fan script chunks.

Search source-authenticated chunks with zero model downloads or network calls.
Returns a private response JSON with text; stdout deliberately prints only
counts, not copyrighted episode dialogue.
"""
from __future__ import annotations
import argparse
import collections
import hashlib
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


def verified_original_av_overrides(records: list[dict], baseline: Path,
                                   review_root: Path) -> list[dict]:
    """Replace only fully published, source-pinned pilot text IN MEMORY.

    The persisted provisional 193-episode corpus and immutable SRT witness
    remain unchanged. No machine speaker model can promote a script here.
    """
    from export_fan_retrieval_chunks import partition_sections, chunk_section, section_heading
    from episode_finish import VIDEO_SHA
    if not review_root.is_dir():
        return records
    layout_file=baseline/"working-screenplay-layout-manifest.json"
    replacements={}
    for ep in ("S01E01","S09E19"):
        screenplay=review_root/(ep+"-original-av-reviewed-screenplay.md")
        manifest_file=review_root/(ep+"-original-av-reviewed-manifest.json")
        ledger=review_root/(ep+"-original-av-decisions.json")
        present=(screenplay.is_file(),manifest_file.is_file(),ledger.is_file())
        if not any(present):
            continue
        # A submitted partial draft must not displace any canonical source.
        if present==(False,False,True):
            continue
        if not all(present):
            raise ValueError("Incomplete source-reviewed pilot publication files: "+ep)
        if not layout_file.is_file():
            raise ValueError("Original canonical pilot layout unavailable for AV retrieval")
        layout=json.loads(layout_file.read_text("utf-8"))
        proof=json.loads(manifest_file.read_text("utf-8"))
        raw=screenplay.read_bytes()
        caption_witness={r["caption_source_sha256"] for r in records if r["episode_id"]==ep}
        if len(caption_witness)!=1:
            raise ValueError("No unambiguous pilot source caption for reviewed replacement")
        src=next(iter(caption_witness))
        digest=lambda content:hashlib.sha256(content).hexdigest()
        old=baseline/(ep+"-working-screenplay.md")
        if (proof.get("schema")!="night-court-original-av-stable-reviewed-screenplay-publication/1"
            or proof.get("episode_id")!=ep
            or proof.get("original_film_sha256")!=VIDEO_SHA[ep]
            or proof.get("immutable_original_dialogue_sha256")!=src
            or proof.get("reviewed_manuscript_sha256")!=digest(raw)
            or proof.get("actual_editorial_ledger_sha256")!=digest(ledger.read_bytes())
            or proof.get("canonical_input_manuscript_sha256")!=layout["manuscript_sha256"][ep]
            or not old.is_file()
            or digest(old.read_bytes())!=layout["manuscript_sha256"][ep]
            or proof.get("caption_witness_remains_immutable") is not True
            or proof.get("software_does_not_prove_human_attention") is not True
            or proof.get("evidence_tier") not in (
                "original_av_reviewer_attested_pending_independent_editor",
                "reviewer_and_independent_spotcheck_attested")):
            raise ValueError("Reviewer-attested pilot/source SHA provenance mismatch")
        doc=raw.decode("utf-8")
        if src not in doc or not doc.startswith("# "+ep+":"):
            raise ValueError("Reviewed screenplay lost original caption witness or episode identity")
        original=[r for r in records if r["episode_id"]==ep]
        template=original[0]
        replacement=[]
        for secnum,section in enumerate(partition_sections(doc),1):
            for partnum,chunk in enumerate(chunk_section(section,3600),1):
                replacement.append({
                    **template,
                    "episode_id":ep,
                    "record_id":f"{ep}:retrieval:{len(replacement)+1:04d}",
                    "section_index":secnum,
                    "section_part":partnum,
                    "section_label":section_heading(section),
                    "script_path":"../episode-finish-current/"+screenplay.name,
                    "script_sha256":digest(raw),
                    "caption_source_sha256":src,
                    "retrieval_text":chunk,
                    "evidence_tier":proof["evidence_tier"],
                    # This is an actual original-AV reviewer declaration.
                    # Tool validation does NOT prove actor identity or human sight.
                    "speaker_names_verified":False,
                    "whole_episode_av_certified":False,
                    "section_is_verified_visual_scene":False,
                })
        if "".join(r["retrieval_text"] for r in replacement)!=doc:
            raise ValueError("Source-reviewed pilot retrieval lost script characters")
        replacements[ep]=replacement
    if not replacements:
        return records
    out=[];emitted=set()
    for rec in records:
        ep=rec["episode_id"]
        if ep in replacements:
            if ep not in emitted:
                out.extend(replacements[ep]);emitted.add(ep)
        else:
            out.append(rec)
    return out


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
    # Canonical private search automatically prefers a source-AV reviewed
    # screenplay only when a complete, source-checked publication exists.
    if (path.name=="fan-retrieval-chunks.jsonl"
        and path.parent.name=="private-fan-retrieval"
        and path.parent.parent.name=="pilot-current"):
        root=path.parent.parent.parent
        records=verified_original_av_overrides(
            records,path.parent.parent,root/"episode-finish-current")
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
