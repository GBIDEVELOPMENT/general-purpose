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


def build_database(db_path: Path, corpus_path: Path, card_path: Path,
                   role_path: Path, require_full: bool = True) -> dict:
    if db_path.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError("Private indexed dialogue database must be outside the repository")
    if db_path.resolve() in {corpus_path.resolve(), card_path.resolve(), role_path.resolve()}:
        raise ValueError("Refusing to overwrite a source file with the database")
    source = load_records(corpus_path)
    cards = load_cards(card_path, source)
    roles = rows_from_jsonl(role_path)
    report = validate_evidence(source, cards, roles, require_full=require_full)
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
                                require_full=not opts.allow_partial)
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
