#!/usr/bin/env python3
"""Offline review of machine-readable Night Court evidence and source boundaries."""
from collections import Counter
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
COUNTS=[13,22,22,22,22,22,24,24,22]

def read_jsonl(path):
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def main():
    records=read_jsonl(ROOT/"catalog"/"episode-knowledge.jsonl")
    assert len(records)==193,("expected 193 retrieval records",len(records))
    ids=set()
    for d in records:
        key=d["id"]
        assert key not in ids, ("duplicate",key)
        ids.add(key)
        assert d["source"]["license"]=="CC BY-SA 4.0",key
        assert d["plot_source_type"]=="licensed_third_party_encyclopedia_synopsis",key
        assert d["not_original_transcript"] is True,key
        assert d["source"]["revision"],key
        assert d["source"]["permalink"].startswith("https://en.wikipedia.org/w/"),key
        text=d["plot_source_plaintext"]
        assert text.strip(),key
        for mention in d["named_character_mentions"]:
            assert mention["relationship"]=="name_mentioned_in_source_capsule",key
            assert mention["not_evidence_of_appearance"] is True,key
            for start,end in mention["text_offset_spans"]:
                assert 0<=start<end<=len(text),(key,start,end)
                assert text[start:end].lower() in [s.lower() for s in mention["matched_terms"]],key
        for cue in d["theme_lexical_cues"]:
            assert cue["kind"]=="lexical_evidence_only_not_editorial_topic_judgment",key
            assert cue["matched_words"],key
        p=ROOT/"seasons"/key[:3]/key/"derived"
        assert (p/"evidence-dossier.json").exists(),key
        assert (p/"reading-note.md").exists(),key
        assert json.loads((p/"evidence-dossier.json").read_text("utf-8"))==d,key
    assert len(ids)==193
    castfile=ROOT/"catalog"/"tvmaze-main-cast.json"
    coverage=ROOT/"catalog"/"tvmaze-guestcast-coverage.json"
    if castfile.exists():
        cast=json.loads(castfile.read_text("utf-8"))
        assert cast["attribution"]["show_id"]==1489
        assert cast["attribution"]["source"]=="TVmaze"
    if coverage.exists():
        c=json.loads(coverage.read_text("utf-8"))["counts"]
        assert c["episode_records_with_embedding"]<=193
        assert c["episode_records_with_guests"]+c["episode_records_empty_guestcast"]==c["episode_records_with_embedding"]
    # Source statements should retain exact character offsets into source plaintext.
    statements=read_jsonl(ROOT/"catalog"/"source-statements.jsonl")
    keyed={r["id"]:r for r in records}
    for st in statements:
        origin=keyed[st["episode_id"]]
        assert st["source_revision"]==origin["source"]["revision"],st["id"]
        assert origin["plot_source_plaintext"][st["text_start"]:st["text_end"]]==st["text"],st["id"]
        assert st["kind"]=="attributed_encyclopedia_source_statement_not_verified_event",st["id"]
    summary=json.loads((ROOT/"catalog"/"source-statements-status.json").read_text("utf-8"))
    assert len(statements)==summary["source_statements"]
    assert summary["episodes"]==193

    # Episode-specific role credits must agree with graph edges and source coverage.
    cast_graph=ROOT/"catalog"/"cast-relationship-graph.json"
    if cast_graph.exists():
        graph=json.loads(cast_graph.read_text("utf-8"))
        c=graph["credits"]
        assert len([e for e in c if e["credit_scope"]=="episode_guest_cast"])==graph["episode_guest_cast_credits"]
        assert all(e["person_id"] in graph["persons"] for e in c)
        assert all(e["character_id"] in graph["characters"] for e in c)
        assert graph["missing_guest_cast_collections"]==0
        assert coverage.exists()
        sourcecounts=json.loads(coverage.read_text("utf-8"))["counts"]
        assert graph["episode_guest_cast_credits"]==sourcecounts["guest_credit_edges"]
    audit=ROOT/"catalog"/"holdings-coverage.json"
    if audit.exists():
        a=json.loads(audit.read_text("utf-8"))
        assert a["episodes"] and len(a["episodes"])==193
        assert a["totals"]["licensed_wikipedia_capsule_held"]==193
        assert a["totals"]["full_transcripts_held"]==0
        if coverage.exists():
            assert a["totals"]["guestcast_credited_roles"]==sourcecounts["guest_credit_edges"]
    context=ROOT/"research"/"licensed-wiki"/"context"/"manifest.json"
    if context.exists():
        cm=json.loads(context.read_text("utf-8"))
        for value in cm["captured"].values():
            assert (ROOT/value["source_file"]).exists()
        assert cm["captured_count"]==len(cm["captured"])
    fandom=ROOT/"research"/"fandom-wiki"/"collection-status.json"
    if fandom.exists():
        f=json.loads(fandom.read_text("utf-8"))
        if f["status"]=="blocked_by_robots":
            assert not list((ROOT/"research"/"fandom-wiki").glob("*.wikitext"))
    snapshots=ROOT/"catalog"/"wiki-revision-archive.json"
    if snapshots.exists():
        import hashlib
        manifest=json.loads(snapshots.read_text("utf-8"))
        assert manifest["snapshot_count"]==len(manifest["snapshots"])
        seen=set()
        for item in manifest["snapshots"]:
            key=(item["source"],item["revision"])
            assert key not in seen,key
            seen.add(key)
            archived=ROOT/item["snapshot_path"]
            rights=ROOT/item["provenance_path"]
            assert archived.exists() and rights.exists(),key
            assert hashlib.sha256(archived.read_bytes()).hexdigest()==item["sha256"],key
            assert item["license"]=="CC BY-SA 4.0",key
            proof=json.loads(rights.read_text("utf-8"))
            assert proof["source_revision"]==item["revision"],key
            assert proof["immutable_revision"],key
    print("VALID:",len(ids),"episode dossiers;",
          sum(len(x["named_character_mentions"]) for x in records),"name-mention relationships;",
          sum(len(x["theme_lexical_cues"]) for x in records),"lexical topic flags;",
          "guestcast file:",coverage.exists())

if __name__=="__main__":main()
