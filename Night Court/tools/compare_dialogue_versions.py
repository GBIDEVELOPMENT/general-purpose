#!/usr/bin/env python3
"""Compare HELD dialogue witnesses without canonizing any one version.

Reference is the longest tokenized source only as a comparison anchor.
Every result retains edition and source SHA; differences are word-level
search aids, never proof an actor said a line or the recording is complete.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from difflib import SequenceMatcher
from hashlib import sha256
from pathlib import Path
import json
import re

ROOT=Path(__file__).resolve().parents[1]
WORD_LIMIT=15000
DIFF_LIMIT=12

def load_jsonl(file):
    if not file.exists():return []
    return [json.loads(s) for s in file.read_text("utf-8").splitlines() if s.strip()]

def tokens(segments):
    data="\n".join(c["text"] for c in segments)
    data=re.sub(r"<[^>]*>"," ",data)
    data=re.sub(r"\[[^]]{1,180}\]"," ",data)
    data=re.sub(r"(?m)^\s*[A-Z][A-Z0-9 .'-]{1,30}:\s*","",data)
    return re.findall(r"[^\W_]+(?:['’][^\W_]+)?",data.lower(),flags=re.U)

def prepare(row):
    key=row["episode_id"]
    manifest=ROOT/row["manifest"]
    obj=json.loads(manifest.read_text("utf-8"))
    base=ROOT/"seasons"/key[:3]/key
    segments=load_jsonl(base/obj["segments_path"])
    words=tokens(segments)
    return {"row":row,"manifest":obj,"words":words,
            "fingerprint":sha256(" ".join(words).encode("utf-8")).hexdigest(),
            "source_path":row["manifest"]}

def compare(a,b):
    words_a=a["words"][:WORD_LIMIT]
    words_b=b["words"][:WORD_LIMIT]
    if not words_a or not words_b:
        score=None;ratio=None;matched=0;edits=[]
    else:
        sm=SequenceMatcher(None,words_a,words_b,autojunk=True)
        score=round(sm.ratio(),4)
        matched=sum(k.size for k in sm.get_matching_blocks())
        ratio=round(matched/min(len(words_a),len(words_b)),4)
        edits=[]
        for tag,i,j,x,y in sm.get_opcodes():
            if tag=="equal":continue
            if len(edits)>=DIFF_LIMIT:break
            edits.append({"operation":tag,"anchor_word_span":[i,j],
                "other_word_span":[x,y],
                "anchor_excerpt":" ".join(words_a[i:min(j,i+16)]),
                "other_excerpt":" ".join(words_b[x:min(y,x+16)])})
    is_same=a["fingerprint"]==b["fingerprint"]
    if score is None:status="insufficient_dialogue_to_compare"
    elif is_same:status="same_normalized_words"
    elif score>=0.97:status="close_transcript_wording"
    elif ratio is not None and ratio>=0.92:status="substantial_overlap_with_different_lengths"
    else:status="materially_different_source_witnesses"
    return {
      "reference_version":a["row"]["version_id"],
      "reference_sha256":a["row"]["sha256"],
      "reference_manifest":a["source_path"],
      "other_version":b["row"]["version_id"],
      "other_sha256":b["row"]["sha256"],
      "other_manifest":b["source_path"],
      "reference_word_count":len(a["words"]),
      "other_word_count":len(b["words"]),
      "reference_normalized_word_sha256":a["fingerprint"],
      "other_normalized_word_sha256":b["fingerprint"],
      "status":status,
      "similarity_score_first_15000_words":score,
      "shorter_track_word_alignment_ratio_first_15000":ratio,
      "matched_words_first_15000":matched,
      "limited_word_diff_examples":edits,
      "analysis_caveat":"Word alignment strips markup and bracketed effects; speaker, timing and edition validity are NOT determined.",
      "not_canonical":True
    }

def write(path,data):
    content=json.dumps(data,indent=2,ensure_ascii=False,sort_keys=True)+"\n"
    if not path.exists() or path.read_text("utf-8")!=content:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(content,"utf-8")

def main():
    records=load_jsonl(ROOT/"catalog"/"dialogue-index.jsonl")
    versions_by_episode=defaultdict(list)
    fingerprints=defaultdict(list)
    for row in records:
        item=prepare(row)
        versions_by_episode[row["episode_id"]].append(item)
        if len(item["words"])>=50:
            fingerprints[item["fingerprint"]].append({"episode_id":row["episode_id"],
                "version_id":row["version_id"],"source_sha256":row["sha256"],
                "words":len(item["words"])})
    comparisons=[];status=Counter()
    for episode,versions in sorted(versions_by_episode.items()):
        if len(versions)<2:continue
        # Max number of comparisons = n-1, not combinatorial all pairs.
        ordered=sorted(versions,key=lambda x:(-len(x["words"]),x["row"]["version_id"]))
        anchor=ordered[0]
        evaluated=[compare(anchor,item) for item in ordered[1:]]
        for c in evaluated:status[c["status"]]+=1
        report={"episode_id":episode,"reference_strategy":"most_words_held_not_canonical",
                "versions":len(ordered),"comparisons":evaluated,
                "source_limit":"15k words per source for bounded comparison; original source bytes remain intact"}
        write(ROOT/"seasons"/episode[:3]/episode/"dialogue"/"variant-comparison.json",report)
        comparisons.extend({"episode_id":episode,**c} for c in evaluated)
    unexpected=[]
    for fingerprint,members in fingerprints.items():
        if len({x["episode_id"] for x in members})>1:
            unexpected.append({"fingerprint":fingerprint,"versions":members,
                               "interpretation":"possible cross-episode misassignment; manual check needed"})
    output={
       "series":"night-court-1984",
       "source_witnesses":len(records),
       "episodes_with_comparable_versions":sum(len(v)>1 for v in versions_by_episode.values()),
       "version_comparisons":len(comparisons),
       "status_counts":dict(sorted(status.items())),
       "cross_episode_identical_long_text_alerts":unexpected,
       "comparison_results":comparisons,
       "limitation":"A word-similar source is not necessarily accurate, complete or from the same video cut."}
    write(ROOT/"catalog"/"dialogue-variant-comparison.json",output)
    print("VARIANT COMPARISON:",len(records),"source versions;",
          len(comparisons),"episode-local pairs;",
          len(unexpected),"possible cross-episode text collisions")

if __name__=="__main__":main()
