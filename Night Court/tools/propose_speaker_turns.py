#!/usr/bin/env python3
"""Conservative P0 speaker-turn decisions over caption-derived units.

Never equate an SRT cue boundary with a speaking-turn boundary. Only explicit,
matching source labels authorize a provisional merge; unlabeled speech is
review-needed, including consecutive cues. All source units are preserved.
This produces review proposals, not independently verified diarization.
"""
from __future__ import annotations
import json
from pathlib import Path
from build_caption_turns import build

ROOT=Path(__file__).resolve().parents[1]
MAX_GAP_MS=2000

def propose(units, max_gap_ms=MAX_GAP_MS):
    """Return contiguous groups with reversible source lineage and decisions."""
    groups=[]
    decisions=[]
    for row in units:
        if not groups:
            groups.append([row])
            continue
        left=groups[-1][-1]
        right=row
        a=left.get("speaker_label_from_source")
        b=right.get("speaker_label_from_source")
        start=right.get("start_ms")
        end=left.get("end_ms")
        gap=None if start is None or end is None else start-end
        adjacency=(right.get("cue")==left.get("cue") or
                   right.get("cue")==left.get("cue")+1)
        same_source=(left.get("source_sha256")==right.get("source_sha256") and
                     left.get("source_version_id")==right.get("source_version_id"))
        if not same_source or not adjacency:
            decision="keep_separate_source_discontinuity"
        elif a and b and a!=b:
            decision="keep_separate_explicit_label_change"
        elif gap is not None and gap>max_gap_ms:
            decision="keep_separate_long_pause_review"
        elif a and b and a==b:
            decision="merge_same_explicit_source_label_provisional"
        else:
            decision="unknown_speaker_boundary_review"
        pair={"left_unit_id":left["unit_id"],"right_unit_id":right["unit_id"],
              "left_cue":left["cue"],"right_cue":right["cue"],
              "decision":decision,"gap_ms":gap,
              "source_label_left":a,"source_label_right":b,
              "human_or_av_confirmed":False}
        decisions.append(pair)
        if decision.startswith("merge_"):
            groups[-1].append(row)
        else:
            groups.append([row])
    output=[]
    for idx,group in enumerate(groups,1):
        labels={u.get("speaker_label_from_source") for u in group}
        label=next(iter(labels)) if len(labels)==1 else None
        output.append({
          "turn_id":f"T{idx:05d}",
          "unit_ids":[u["unit_id"] for u in group],
          "source_cue_parts":[{"cue":u["cue"],"part":u["part"]} for u in group],
          "source_text_parts":[u["source_text"] for u in group],
          "source_label_provisional":label,
          "character_identity_verified":False,
          "boundary_verified":False,
          "status":"candidate_turn_unreviewed"})
    return output,decisions

def for_episode(episode,root=ROOT):
    sources=[json.loads(s) for s in (root/"catalog/dialogue-index.jsonl").read_text("utf-8").splitlines() if s.strip()]
    matches=[s for s in sources if s["episode_id"]==episode]
    if len(matches)!=1:raise ValueError("Expected one source edition")
    meta=json.loads((root/matches[0]["manifest"]).read_text("utf-8"))
    cues=[json.loads(s) for s in (root/"seasons"/episode[:3]/episode/meta["segments_path"]).read_text("utf-8").splitlines() if s.strip()]
    units,_=build(meta,cues)
    turns,decisions=propose(units)
    return {"schema":"night-court-p0-turn-boundaries/1","episode_id":episode,
            "source_sha256":meta["sha256"],"candidate_turns":turns,
            "boundary_decisions":decisions,
            "summary":{"source_units":len(units),"candidate_turns":len(turns),
              "provisional_label_merges":sum(x["decision"].startswith("merge_") for x in decisions),
              "uncertain_boundaries":sum(x["decision"]=="unknown_speaker_boundary_review" for x in decisions)},
            "independently_verified":False}

def main():
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--episode",required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    result=for_episode(args.episode)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(result["summary"])

if __name__=="__main__":main()
