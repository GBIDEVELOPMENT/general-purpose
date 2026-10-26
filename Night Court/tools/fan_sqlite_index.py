#!/usr/bin/env python3
"""Build a single private Night Court fan retrieval database (standard SQLite FTS5).

Indexes source-witness script chunks, provisional per-role original dialogue,
and separately flagged editorial comedy/story analyses. No model, network,
media download or copyrighted text in stdout. Do not commit the generated DB.
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
from collections import Counter
from pathlib import Path

from build_pilot_character_evidence import SCHEMA as ROLE_SCHEMA
from build_pilot_fan_beat_cards import CARD_SCHEMA
from search_fan_corpus import load_cards
from search_fan_retrieval_chunks import load_records, words

SCHEMA = "night-court-private-unified-fan-fts/1"
KINDS = ("script_witness", "provisional_character_dialogue", "editorial_comedy_and_story")
ROOT = Path(__file__).resolve().parents[1]


def rows_from_jsonl(path: Path) -> list[dict]:
    if not path.is_file():
        raise FileNotFoundError(path)
    return [json.loads(line) for line in path.read_text("utf-8").splitlines() if line.strip()]


def validate_evidence(original: list[dict], cards: list[dict],
                      roles: list[dict], require_full: bool = True) -> dict:
    editions = {}
    for src in original:
        editions.setdefault(src["episode_id"], set()).add(src["caption_source_sha256"])
    if any(len(v) != 1 for v in editions.values()):
        raise ValueError("Conflicting source editions in unified episode retrieval")
    ids = set()
    named = 0
    units = 0
    for row in roles:
        ep = row.get("episode_id")
        key = row.get("reading_block_id")
        refs = row.get("original_source_part_refs")
        if (row.get("schema") != ROLE_SCHEMA or not isinstance(key, str) or key in ids
            or not key.startswith(str(ep) + ":speaker-evidence:")
            or not isinstance(refs, list) or not refs
            or row.get("original_source_sha256") not in editions.get(ep, set())
            or row.get("speaker_turn_boundary_verified") is not False
            or row.get("actor_face_or_voice_independently_verified") is not False
            or not isinstance(row.get("caption_text"), str)):
            raise ValueError("Unsafe, duplicate or non-source-linked role evidence")
        ids.add(key)
        candidate = row.get("candidate_role")
        if candidate is not None and (not isinstance(candidate, str) or not candidate.strip()):
            raise ValueError("Invalid provisional character role")
        if candidate is None and row.get("role_attribution_status") != "unidentified":
            raise ValueError("Unknown original speaker promoted to a character")
        if candidate is not None and row.get("role_attribution_status") != "provisional_not_original_audio_verified":
            raise ValueError("Provisional role silently promoted")
        units += len(refs)
        if candidate:
            named += len(refs)
    by_episode = Counter(c["episode_id"] for c in cards)
    if require_full and (
        len(editions) != 193 or len(cards) != 21 or len(roles) != 715
        or (units, named) != (751, 487) or by_episode != {"S01E01": 10, "S09E19": 11}
    ):
        raise ValueError("Not the complete source-only 193-episode/pilot enrichment release")
    return {
        "source_episodes": len(editions),
        "script_chunks": len(original),
        "editorial_beat_cards": len(cards),
        "provisional_character_reading_blocks": len(roles),
        "pilot_original_speaking_units": units,
        "pilot_provisionally_named_speaking_units": named,
        "source_editions": {k: next(iter(v)) for k, v in sorted(editions.items())},
    }


def apply_speaker_improvements(source: list[dict], roles: list[dict],
                               improvements: list[dict],
                               require_full: bool = True) -> list[dict]:
    """Supersede matching UNKNOWN role blocks, never index conflicting old labels.

    The historical 715-reading-block baseline remains independently validated
    before this function. The corrected representation contains 716 proposed
    speaker segments because one S09 original paragraph held two voices.
    """
    from collections import defaultdict
    from hashlib import sha256
    groups = defaultdict(list)
    if require_full and (len(improvements) != 4
                         or {(x.get("episode_id"), x.get("source_ref")) for x in improvements} !=
                         {("S01E01", "C142.1"), ("S09E19", "C027.1"), ("S09E19", "C034.1")}):
        raise ValueError("Unexpected high-priority speaker revision coverage")
    for item in improvements:
        ep, ref = item.get("episode_id"), item.get("source_ref")
        if (item.get("schema") !=
                "night-court-original-pilot-external-attribution-application/1"
            or item.get("original_soundtrack_verified") is not False
            or item.get("character_identity_status") != "external_or_context_editorial_proposal"
            or not isinstance(item.get("start_char"), int)
            or not isinstance(item.get("end_char"), int)
            or not isinstance(item.get("text"), str)
            or not isinstance(item.get("candidate_role"), str)
            or not item["candidate_role"].strip()
            or not isinstance(item.get("reader_label"), str)
            or not item["reader_label"].startswith(item["candidate_role"] + " · ")
            or "UNVERIFIED" not in item["reader_label"]
            or not isinstance(ref, str)):
            raise ValueError("Invalid or falsely certified external speaker proposal")
        groups[(ep, ref)].append(item)
    old_by_key = {(r["episode_id"], r.get("source_reading_ref")): r for r in roles}
    result = [r for r in roles if
              (r["episode_id"], r.get("source_reading_ref")) not in groups]
    source_by_episode = defaultdict(list)
    for row in source:
        source_by_episode[row["episode_id"]].append(row)
    for (ep, ref), entries in groups.items():
        previous = old_by_key.get((ep, ref))
        if previous is None or previous["candidate_role"] is not None:
            raise ValueError("Cannot supersede a named or nonexistent earlier speaking block")
        original = previous["caption_text"]
        if not all(x.get("source_witness_sha256") == previous["original_source_sha256"]
                   and x.get("source_cue_sha256") == sha256(original.encode()).hexdigest()
                   for x in entries):
            raise ValueError("Speaker correction conflicts with source caption SHA")
        document = "".join(x["retrieval_text"] for x in source_by_episode[ep])
        spans = sorted(entries, key=lambda x: x["start_char"])
        pos = 0
        for idx, row in enumerate(spans, 1):
            a,b=row["start_char"],row["end_char"]
            if not (pos <= a < b <= len(original)
                    and not original[pos:a].strip()
                    and original[a:b] == row["text"]):
                raise ValueError("Proposed voice segments alter or omit source words")
            if row["reader_label"] + "\n" + row["text"] not in document:
                raise ValueError("New speaker reading not actually present in indexed v6 pilot")
            replacement = dict(previous)
            replacement.update({
                "reading_block_id": previous["reading_block_id"] + f":speaker-p{idx}",
                "caption_text": row["text"],
                "candidate_role": row["candidate_role"],
                "role_attribution_status": "external_or_context_editorial_proposal",
                "speaker_turn_boundary_verified": False,
                "actor_face_or_voice_independently_verified": False,
                "original_source_spans_shared_across_multiple_voices": len(spans) > 1,
                "source_cue_start_char": a,
                "source_cue_end_char": b,
                "external_episode_quote_url": row["external_episode_quote_url"],
                "source_quote_dependency_possible": True,
            })
            result.append(replacement)
            pos=b
        if original[pos:].strip():
            raise ValueError("Last proposed speaker span does not cover complete original dialogue")
    if len({x["reading_block_id"] for x in result}) != len(result):
        raise ValueError("Duplicated corrected character reading ID")
    if require_full and len(result) != 716:
        raise ValueError("Expected 716 post-split provisional pilot speaking segments")
    return result


def use_source_checked_context_roles(source: list[dict], old_roles: list[dict],
                                     context_path: Path,
                                     full: bool = True,
                                     source_acoustic_v8: bool = False) -> tuple[list[dict], dict]:
    """Verify original speaker records still cover identical caption units.

    The v7 reader is a P1-first view, not independently sound-verified.
    It *must not* silently promote old known roles or invent new dialogue.
    """
    import hashlib
    from collections import defaultdict
    manifest_path = context_path.parent / (
        "pilot-original-acoustic-speaker-manifest.json" if source_acoustic_v8
        else "pilot-contextual-speaker-manifest.json"
    )
    manifest = json.loads(manifest_path.read_text("utf-8"))
    raw = context_path.read_bytes()
    sha_field = ("source_role_record_sha256" if source_acoustic_v8
                 else "reading_record_sha256")
    if hashlib.sha256(raw).hexdigest() != manifest.get(sha_field):
        raise ValueError("Private character source-index SHA256 mismatch")
    newer = rows_from_jsonl(context_path)
    old_map = {(r["episode_id"], r["source_reading_ref"]): r for r in old_roles}
    groups = defaultdict(list)
    for row in newer:
        if row.get("schema") != "night-court-private-character-dialogue-evidence/1":
            raise ValueError("Unexpected v7 original character evidence record")
        key = (row["episode_id"], row["source_reading_ref"])
        if key not in old_map:
            raise ValueError("V7 invented a new original speaking cue")
        orig = old_map[key]
        if (row["original_source_sha256"] != orig["original_source_sha256"]
            or row["original_source_part_refs"] != orig["original_source_part_refs"]
            or row.get("speaker_turn_boundary_verified") is not False
            or row.get("actor_face_or_voice_independently_verified") is not False):
            raise ValueError("V7 changed original source identity or claimed AV certainty")
        if (orig["candidate_role"] is not None
            and orig["candidate_role"] != row["candidate_role"]):
            raise ValueError("V7 replaced a previously named source role without reviewed evidence")
        groups[key].append(row)
    if set(groups) != set(old_map):
        raise ValueError("V7 dropped an original dialogue speaking block")
    for key, parts in groups.items():
        orig = old_map[key]
        if len(parts) == 1:
            if parts[0]["caption_text"] != orig["caption_text"]:
                raise ValueError("V7 altered an original spoken text block")
        elif (key == ("S09E19", "C034.1") and len(parts) == 2
              and " ".join(p["caption_text"] for p in parts) == orig["caption_text"]
              and all(p["candidate_role"] for p in parts)):
            pass
        else:
            raise ValueError("V7 split/duplicated an unsupported original source cue")
    source_docs = defaultdict(str)
    for r in source:
        source_docs[r["episode_id"]] += r["retrieval_text"]
    for row in newer:
        if row["role_attribution_status"] == "narrative_context_candidate_not_voice_verified":
            if (row["candidate_role"] is None
                or row.get("actor_face_or_voice_independently_verified") is not False
                or row.get("original_audio_reviewed") is not False):
                raise ValueError("Contextual identity masquerades as confirmed voice")
        if row.get("role_attribution_status")=="original_soundtrack_embedding_support_not_audio_verified":
            if (not source_acoustic_v8
                or row.get("original_soundtrack_acoustic_similarity_proposal_only") is not True
                or row.get("original_soundtrack_human_speaker_identity_verified") is not False
                or row.get("source_acoustic_role_source_conditioned_on_previous_provisional_labels") is not True):
                raise ValueError("Original soundtrack role silently accepted as verified identity")
        expected = ((row["candidate_role"] or "UNIDENTIFIED SPEAKER")
                    + " · " + row["role_attribution_status"] + "\n" + row["caption_text"])
        if expected not in source_docs[row["episode_id"]]:
            raise ValueError("Contextual named voice not represented in matching source script")
    source_keys = {}
    for row in newer:
        for ref in row["original_source_part_refs"]:
            source_keys.setdefault((row["episode_id"], ref), set()).add(row["candidate_role"])
    accepted = sum(None not in roles for roles in source_keys.values())
    expected_named, expected_unknown = ((587,164) if source_acoustic_v8 else (583,168))
    if full and (len(newer),len(source_keys),accepted,len(source_keys)-accepted)!=(
        716,751,expected_named,expected_unknown
    ):
        raise ValueError("Original source pilot totals no longer match speaker evidence")
    if full and source_acoustic_v8 and (
        manifest.get("source_units_with_provisional_names")!=587
        or manifest.get("original_units_still_unknown")!=164
        or manifest.get("source_speaker_identities_human_verified_by_pass")!=0
    ):
        raise ValueError("Original source voice-v8 acceptance falsely claimed")
    if full and not source_acoustic_v8 and (
        manifest.get("source_units_total")!=751
        or manifest.get("source_units_provisionally_named")!=583
        or manifest.get("source_units_unknown")!=168
        or manifest.get("audio_confirmed_by_this_pass")!=0
    ):
        raise ValueError("V7 report mismatches actual original pilot coverage")
    prefix = "v8" if source_acoustic_v8 else "v7"
    return newer, {
        prefix+"_provisional_speaker_record_count":len(newer),
        prefix+"_provisionally_named_original_units":accepted,
        prefix+"_unidentified_original_units":len(source_keys)-accepted,
        prefix+"_audio_confirmed_in_this_pass":0,
    }


def build_database(db_path: Path, corpus_path: Path, card_path: Path,
                   role_path: Path, require_full: bool = True,
                   speaker_override_path: Path | None = None,
                   context_role_path: Path | None = None,
                   acoustic_context_role_path: Path | None = None) -> dict:
    if db_path.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError("Private indexed dialogue database must be outside the repository")
    if sum(x is not None for x in (
        speaker_override_path, context_role_path, acoustic_context_role_path
    ))>1:
        raise ValueError("Choose exactly one pilot character-role evidence overlay")
    if db_path.resolve() in {corpus_path.resolve(), card_path.resolve(), role_path.resolve(),
                             speaker_override_path.resolve() if speaker_override_path else None,
                             context_role_path.resolve() if context_role_path else None,
                             acoustic_context_role_path.resolve() if acoustic_context_role_path else None}:
        raise ValueError("Refusing to overwrite a source file with the database")
    source = load_records(corpus_path)
    cards = load_cards(card_path, source)
    roles = rows_from_jsonl(role_path)
    report = validate_evidence(source, cards, roles, require_full=require_full)
    if speaker_override_path is not None:
        revisions = rows_from_jsonl(speaker_override_path)
        roles = apply_speaker_improvements(source, roles, revisions, require_full=require_full)
        report["post_speaker_improvement_blocks"] = len(roles)
        report["speaker_improvement_provisional_source_units"] = len(set(
            (x["episode_id"], x["source_ref"]) for x in revisions))
        report["speaker_improvement_independently_audio_verified"] = 0
    if context_role_path is not None:
        roles, summary = use_source_checked_context_roles(source, roles,
                       context_role_path, full=require_full)
        report.update(summary)
    if acoustic_context_role_path is not None:
        roles, summary = use_source_checked_context_roles(source, roles,
            acoustic_context_role_path, full=require_full, source_acoustic_v8=True)
        report.update(summary)
    if db_path.exists():
        raise FileExistsError("Refuse overwriting an existing fan corpus database")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db_path)
    try:
        con.executescript("""
        PRAGMA journal_mode=DELETE;
        CREATE TABLE documents(
          id INTEGER PRIMARY KEY,
          document_id TEXT NOT NULL UNIQUE,
          kind TEXT NOT NULL,
          episode_id TEXT NOT NULL,
          role TEXT,
          title TEXT NOT NULL,
          body TEXT NOT NULL,
          source_sha256 TEXT NOT NULL,
          evidence_state TEXT NOT NULL,
          source_data_json TEXT NOT NULL
        );
        CREATE INDEX by_kind_episode ON documents(kind, episode_id);
        CREATE INDEX by_role ON documents(role);
        CREATE VIRTUAL TABLE search_fts USING fts5(
          title, body, role, content='documents', content_rowid='id',
          tokenize='porter unicode61 remove_diacritics 2'
        );
        CREATE TABLE manifest(key TEXT PRIMARY KEY, value TEXT NOT NULL);
        """)
        rows = []
        for r in source:
            rows.append((
                r["record_id"], KINDS[0], r["episode_id"], None,
                r["episode_title"] + " " + r["section_label"], r["retrieval_text"],
                r["caption_source_sha256"], r["evidence_tier"],
                json.dumps(r, ensure_ascii=False, sort_keys=True),
            ))
        for r in roles:
            rows.append((
                r["reading_block_id"], KINDS[1], r["episode_id"], r["candidate_role"],
                r["candidate_role"] or "Unidentified voice",
                r["caption_text"], r["original_source_sha256"],
                r["role_attribution_status"],
                json.dumps(r, ensure_ascii=False, sort_keys=True),
            ))
        for r in cards:
            rows.append((
                r["id"], KINDS[2], r["episode_id"], " ".join(r["candidate_characters"]),
                r["title"], r["semantic_text"], r["source_witness_sha256"],
                "editorial_interpretation_only",
                json.dumps(r, ensure_ascii=False, sort_keys=True),
            ))
        con.executemany(
            "INSERT INTO documents(document_id,kind,episode_id,role,title,body,"
            "source_sha256,evidence_state,source_data_json) VALUES(?,?,?,?,?,?,?,?,?)", rows)
        con.execute("INSERT INTO search_fts(search_fts) VALUES ('rebuild')")
        con.execute("INSERT INTO manifest(key,value) VALUES (?,?)",
                    ("schema", SCHEMA))
        con.execute("INSERT INTO manifest(key,value) VALUES (?,?)",
                    ("summary", json.dumps(report, ensure_ascii=False, sort_keys=True)))
        con.commit()
        integrity = con.execute("PRAGMA quick_check").fetchone()[0]
        if integrity != "ok":
            raise ValueError("SQLite index integrity check failed: " + integrity)
        total = con.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
        if total != len(rows):
            raise ValueError("SQLite indexed document count mismatch")
        report["indexed_documents"] = total
        return report
    except Exception:
        con.close()
        db_path.unlink(missing_ok=True)
        raise
    finally:
        con.close()


def query(db_path: Path, prompt: str, episode: str | None = None,
          role: str | None = None, limit_each: int = 5) -> dict:
    if not 1 <= limit_each <= 30:
        raise ValueError("Limit must be 1..30")
    if episode and not re.fullmatch(r"S\d{2}E\d{2}", episode):
        raise ValueError("Invalid episode filter")
    tokens = words(prompt)
    if not tokens:
        raise ValueError("No significant query terms")
    # Each term is quoted to prevent user-supplied FTS operators/SQL injection.
    matched = " OR ".join('"' + term + '"' for term in sorted(set(tokens)))
    con = sqlite3.connect(f"file:{db_path.resolve()}?mode=ro", uri=True)
    try:
        got = con.execute("SELECT value FROM manifest WHERE key='schema'").fetchone()
        if not got or got[0] != SCHEMA:
            raise ValueError("Wrong/private Night Court FTS database schema")
        output = {}
        for kind in KINDS:
            clauses = ["search_fts MATCH ?", "documents.kind = ?"]
            args = [matched, kind]
            if episode:
                clauses.append("documents.episode_id = ?")
                args.append(episode)
            if role and kind == KINDS[1]:
                clauses.append("documents.role = ?")
                args.append(role)
            sql = ("SELECT documents.source_data_json, bm25(search_fts) AS rank "
                   "FROM search_fts JOIN documents ON search_fts.rowid = documents.id "
                   "WHERE " + " AND ".join(clauses) +
                   " ORDER BY rank ASC, documents.document_id ASC LIMIT ?")
            rows = con.execute(sql, (*args, limit_each)).fetchall()
            output[kind] = [
                {"rank": float(score), "evidence": json.loads(doc)}
                for doc, score in rows
            ]
        return {
            "schema": SCHEMA, "query": prompt, "episode_filter": episode,
            "role_filter_on_character_evidence_only": role,
            "results_by_evidence_kind": output,
            "reminder": ("Original source speech and images are not automatically "
                         "authenticated by provisional role labels or a fan's "
                         "editorial interpretation of a joke."),
        }
    finally:
        con.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("build")
    init.add_argument("--corpus", type=Path, required=True)
    init.add_argument("--cards", type=Path, required=True)
    init.add_argument("--roles", type=Path, required=True)
    init.add_argument("--database", type=Path, required=True)
    init.add_argument("--allow-partial", action="store_true")
    init.add_argument("--speaker-overrides", type=Path, default=None)
    init.add_argument("--context-roles", type=Path, default=None)
    init.add_argument("--acoustic-context-roles", type=Path, default=None)
    srch = sub.add_parser("query")
    srch.add_argument("--database", type=Path, required=True)
    srch.add_argument("--query", required=True)
    srch.add_argument("--episode", default=None)
    srch.add_argument("--role", default=None)
    srch.add_argument("--limit", type=int, default=5)
    srch.add_argument("--output", type=Path, required=True)
    opts = parser.parse_args()
    if opts.command == "build":
        report = build_database(opts.database, opts.corpus, opts.cards, opts.roles,
                                require_full=not opts.allow_partial,
                                speaker_override_path=opts.speaker_overrides,
                                context_role_path=opts.context_roles,
                                acoustic_context_role_path=opts.acoustic_context_roles)
        print(f"{report['indexed_documents']} private documents indexed across "
              f"{report['source_episodes']} episodes; no dialogue printed")
    else:
        if opts.output.resolve().is_relative_to(ROOT.resolve()):
            raise ValueError("Private full-text search answers must be saved outside the repository")
        response = query(opts.database, opts.query, opts.episode, opts.role, opts.limit)
        opts.output.parent.mkdir(parents=True, exist_ok=True)
        opts.output.write_text(json.dumps(response, ensure_ascii=False, indent=2) + "\n", "utf-8")
        print("Saved private Night Court source/character/comedy search results; no dialogue printed")


if __name__ == "__main__":
    main()
