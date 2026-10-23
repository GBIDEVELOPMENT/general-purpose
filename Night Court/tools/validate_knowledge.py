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
    print("VALID:",len(ids),"episode dossiers;",
          sum(len(x["named_character_mentions"]) for x in records),"name-mention relationships;",
          sum(len(x["theme_lexical_cues"]) for x in records),"lexical topic flags;",
          "guestcast file:",coverage.exists())

if __name__=="__main__":main()
