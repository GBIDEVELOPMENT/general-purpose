#!/usr/bin/env python3
"""Produce evidence-linked LLM retrieval dossiers from 193 licensed episode capsules.

This is deterministic information retrieval, NOT creative reconstruction, scene
segmentation or a claim that named characters actually appeared on screen.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from html import unescape
from pathlib import Path
import json
import re

ROOT=Path(__file__).resolve().parents[1]
COUNTS=[13,22,22,22,22,22,24,24,22]
ALIASES={
 "harry-stone":["Harry","Harry Stone","Judge Stone","Harold T. Stone"],
 "dan-fielding":["Dan","Dan Fielding"],
 "bull-shannon":["Bull","Bull Shannon"],
 "selma-hacker":["Selma","Selma Hacker"],
 "florence-kleiner":["Flo","Florence","Florence Kleiner"],
 "roz-russell":["Roz","Roz Russell"],
 "christine-sullivan":["Christine","Christine Sullivan"],
 "mac-robinson":["Mac","Mac Robinson"],
 "quon-le":["Quon Le","Quon-Le"],
 "lana-wagner":["Lana","Lana Wagner"],
 "billie-young":["Billie","Billie Young"],
 "liz-williams":["Liz","Liz Williams"],
 "sheila-gardner":["Sheila","Sheila Gardner"],
 "buddy-ryan":["Buddy","Buddy Ryan"],
 "leon":["Leon"],
 "art-fensterman":["Art","Art Fensterman"],
 "phil":["Phil"]
}
TOPICS={
 "family-parenthood":r"\b(mother|father|parent|son|daughter|baby|pregnan\w*|brother|sister|adopt\w*|family|children|child)\b",
 "romantic-relationships":r"\b(date|dating|marri\w*|wedding|boyfriend|girlfriend|romanc\w*|love|divorc\w*|kiss\w*)\b",
 "work-and-career":r"\b(job|employment|hiring|fired|career|promotion|boss|strike|office|work\w*)\b",
 "legal-institutions":r"\b(judge|judicial|trial|lawsuit|court|jur\w*|prosecut\w*|bail\w*|arrest\w*|attorney|lawyer)\b",
 "health-and-medicine":r"\b(hospital|doctor|surg\w*|medical|disease|injur\w*|accident|sick|illness)\b",
 "money-and-class":r"\b(money|wealth\w*|poor|rich|debt|bank|inherit\w*|salary|lottery)\b",
 "politics-and-government":r"\b(election|congress|president|mayor|politic\w*|senat\w*|campaign)\b",
 "religion-and-tradition":r"\b(religio\w*|church|nun|rabbi|priest|christmas|holiday|thanksgiving)\b",
 "performance-and-entertainment":r"\b(music|sing\w*|concert|movie|film|theat\w*|video|show|magician|magic|perform\w*)\b",
 "supernatural-and-scifi":r"\b(ghost|alien|ufo|magic|supernatural|psychic|hypnot\w*|time.travel)\b",
 "animals":r"\b(cat|dog|puppy|kitten|monkey|animal|pet|bird)\b",
 "confinement-and-disaster":r"\b(storm|blizzard|hurricane|trapp\w*|stuck|quarantin\w*|flood|fire|evacuat\w*)\b"
}

def plain(text):
    """Loss-tolerant reading text, not a faithful MediaWiki rendering."""
    text=re.sub(r"<ref\b[^>]*>.*?</ref>","",text,flags=re.S|re.I)
    text=re.sub(r"<ref\b[^>]*/>","",text,flags=re.I)
    text=re.sub(r"\[\[([^]|]+)\|([^]]+)\]\]",r"\2",text)
    text=re.sub(r"\[\[([^]]+)\]\]",r"\1",text)
    text=re.sub(r"\[https?://[^\s\]]+\s+([^\]]+)\]",r"\1",text)
    text=re.sub(r"'{2,5}","",text)
    text=re.sub(r"<br\s*/?>","\n",text,flags=re.I)
    # Unknown MediaWiki templates are not silently interpreted as prose.
    text=re.sub(r"\{\{[^{}]*\}\}","",text)
    text=re.sub(r"<[^>]+>","",text)
    text=unescape(text)
    text=re.sub(r"[ \t]+"," ",text)
    text=re.sub(r"\n{3,}","\n\n",text)
    return text.strip()

def references(text):
    found=[]
    for character,variants in ALIASES.items():
        matches=[]
        for variant in variants:
            p=r"(?<!\w)"+re.escape(variant)+r"(?!\w)"
            for m in re.finditer(p,text,re.I):
                matches.append((m.start(),m.end(),text[m.start():m.end()]))
        # Prevent duplicate overlapping alias matches such as Harry / Harry Stone.
        matches.sort(key=lambda x:(x[0],-(x[1]-x[0])))
        unique=[]
        for span in matches:
            if not any(span[0]<p[1] and p[0]<span[1] for p in unique):
                unique.append(span)
        if unique:
            found.append({"character_id":character,"matched_terms":sorted(set(m[2] for m in unique)),
                          "count":len(unique),"text_offset_spans":[[m[0],m[1]] for m in unique],
                          "relationship":"name_mentioned_in_source_capsule",
                          "not_evidence_of_appearance":True})
    return found

def topical_cues(text):
    cues=[]
    for topic,pattern in TOPICS.items():
        hits=list(re.finditer(pattern,text,re.I))
        if hits:
            cues.append({"topic":topic,
                         "matched_words":sorted(set(x.group(0).lower() for x in hits)),
                         "match_count":len(hits),
                         "kind":"lexical_evidence_only_not_editorial_topic_judgment"})
    return cues

def write(path,content):
    if isinstance(content,(dict,list)):
        content=json.dumps(content,ensure_ascii=False,indent=2)+"\n"
    if not path.exists() or path.read_text("utf-8")!=content:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(content,"utf-8")
        return 1
    return 0

def main():
    documents=[]
    character_edges=[]
    tag_edges=[]
    changes=0
    for s,count in enumerate(COUNTS,1):
        for n in range(1,count+1):
            episode_id=f"S{s:02d}E{n:02d}"
            directory=ROOT/"seasons"/f"S{s:02d}"/episode_id
            episode=json.loads((directory/"episode.json").read_text("utf-8"))
            source=directory/"authorized-text"/"wikipedia-episode-capsule.wikitext"
            evidence=directory/"sources"/"wikipedia-capsule.provenance.json"
            if not source.exists() or not evidence.exists():
                raise ValueError(f"{episode_id}: missing licensed capsule")
            text=plain(source.read_text("utf-8"))
            meta=json.loads(evidence.read_text("utf-8"))
            if not text:raise ValueError(f"{episode_id}: empty caption")
            mention=references(text)
            cues=topical_cues(text)
            report={
                "id":episode_id,"title":episode["title"],
                "broadcast_date":episode["original_air_date"],
                "season":s,"episode":n,
                "plot_source_plaintext":text,
                "plot_source_type":"licensed_third_party_encyclopedia_synopsis",
                "not_original_transcript":True,
                "source":{"path":"seasons/S%02d/%s/authorized-text/wikipedia-episode-capsule.wikitext"%(s,episode_id),
                          "permalink":meta["permalink"],"license":meta["license"],
                          "revision":meta["source_revision"],"attribution":meta["attribution"]},
                "production":{"director":episode["credits"]["director"],
                              "writer_credit":episode["credits"].get("writer_credit_display"),
                              "production_code":episode["credits"]["production_code"]},
                "named_character_mentions":mention,
                "theme_lexical_cues":cues,
                "scope_limits":["character mentions do not prove onscreen presence",
                                "topic cues are lexical matches, not narrative interpretation",
                                "synopses can omit events and dialogue; no scene timing is available"]
            }
            changes+=write(directory/"derived"/"evidence-dossier.json",report)
            character_lines=(", ".join(x["character_id"] for x in mention) if mention else "none detected in capsule")
            cue_lines=(", ".join(x["topic"] for x in cues) if cues else "none detected in capsule")
            markdown=(f"# {episode_id}: {episode['title']}\n\n"
                      f"**Originally aired:** {episode['original_air_date']}  \n"
                      f"**Director:** {episode['credits']['director']}  \n"
                      f"**Written by (source credit):** {episode['credits'].get('writer_credit_display')}  \n"
                      f"**Production code:** {episode['credits']['production_code']}\n\n"
                      f"## Licensed reference synopsis\n\n{text}\n\n"
                      f"Source: [Wikipedia episode list, revision {meta['source_revision']}]({meta['permalink']}). "
                      f"Copyright Wikipedia contributors, {meta['license']}; see "
                      f"[provenance](../sources/wikipedia-capsule.provenance.json). "
                      f"This is an encyclopedia synopsis, not closed captions or a television transcript.\n\n"
                      f"## Machine-detected pointers\n\n"
                      f"Names mentioned: {character_lines}.\n\n"
                      f"Lexical themes: {cue_lines}.\n\n"
                      f"These are search aids only; no assertion of participation, dialogue, scenes or mood. "
                      f"See [structured dossier](evidence-dossier.json) for supporting matched terms and offsets.\n")
            changes+=write(directory/"derived"/"reading-note.md",markdown)
            documents.append(report)
            for m in mention:
                character_edges.append({"episode_id":episode_id,"character_id":m["character_id"],
                    "evidence":"wikipedia_capsule_text","matched_terms":m["matched_terms"],
                    "relationship":"explicit_name_mention_only"})
            for t in cues:
                tag_edges.append({"episode_id":episode_id,"topic":t["topic"],
                    "matched_terms":t["matched_words"],"relationship":"lexical_topic_hint_only"})
    changes+=write(ROOT/"catalog"/"episode-knowledge.jsonl",
                   "\n".join(json.dumps(d,ensure_ascii=False,sort_keys=True) for d in documents)+"\n")
    changes+=write(ROOT/"catalog"/"character-mentions.jsonl",
                   "\n".join(json.dumps(d,ensure_ascii=False,sort_keys=True) for d in character_edges)+"\n")
    changes+=write(ROOT/"catalog"/"theme-cues.jsonl",
                   "\n".join(json.dumps(d,ensure_ascii=False,sort_keys=True) for d in tag_edges)+"\n")
    coverage={
      "episodes_indexed":len(documents),
      "character_mentions":len(character_edges),
      "lexical_topic_hints":len(tag_edges),
      "episodes_with_named_character_mentions":sum(bool(d["named_character_mentions"]) for d in documents),
      "episodes_with_lexical_topic_hints":sum(bool(d["theme_lexical_cues"]) for d in documents),
      "character_mention_episode_counts":dict(sorted(Counter(e["character_id"] for e in character_edges).items())),
      "theme_episode_counts":dict(sorted(Counter(e["topic"] for e in tag_edges).items())),
      "limitations":["lexical indexing, not narrative fact extraction",
                     "licensed Wikipedia capsule source reused; no independent corroboration",
                     "episode-specific case studies have not been scene-validated"],
      "canonical_status":"retrieval_scaffold_not_canonical_knowledge"
    }
    changes+=write(ROOT/"catalog"/"retrieval-coverage.json",coverage)
    print("Index populated",len(documents),"episodes;",len(character_edges),"name-mention edges;",
          len(tag_edges),"lexical topic edges;",changes,"files changed")

if __name__=="__main__":main()
