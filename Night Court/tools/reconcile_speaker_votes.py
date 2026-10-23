#!/usr/bin/env python3
"""Validate independent speaker proposals and emit uncertainty-marked draft scripts.

Each per-version speaker-attribution/votes/<agent-id>.jsonl file contains:
{"turn_id":"S01E01:C00001:1","speaker_id":"tvmaze:99640",
 "confidence":0.84,"source_sha256":"...", "evidence_turn_ids":["S01E01:C00001:1"],
 "short_evidence_summary":"Name spoken with corresponding reply in the scene"}

Numerical confidence is a model rating, not calibrated probability.
Two agreeing agent names are not necessarily independent ground truth.
"""
from collections import Counter,defaultdict
from pathlib import Path
import json,re

ROOT=Path(__file__).resolve().parents[1]
SPECIAL={"UNKNOWN","UNIDENTIFIED_GUEST","OFFSCREEN_OR_CROWD"}

def rows(file):
    return [json.loads(line) for line in file.read_text("utf-8").splitlines() if line.strip()] if file.exists() else []

def save(file,content):
    file.parent.mkdir(parents=True,exist_ok=True)
    if not file.exists() or file.read_text("utf-8")!=content:
        file.write_text(content,"utf-8")
        return 1
    return 0

def checked_vote(v,agent,sha,turn_ids,roster):
    if not isinstance(v,dict) or not {"turn_id","speaker_id","confidence","source_sha256","evidence_turn_ids"}.issubset(v):
        raise ValueError("Incomplete vote record")
    if v["turn_id"] not in turn_ids:raise ValueError("Unknown turn id "+str(v["turn_id"]))
    if v["source_sha256"]!=sha:raise ValueError("Wrong caption source SHA")
    if v["speaker_id"] not in roster|SPECIAL:raise ValueError("Unknown credited role "+str(v["speaker_id"]))
    n=v["confidence"]
    if not isinstance(n,(float,int)) or isinstance(n,bool) or not 0<=n<=1:
        raise ValueError("Agent rating must be in 0..1")
    evidence=v["evidence_turn_ids"]
    if not isinstance(evidence,list) or not all(isinstance(x,str) and x in turn_ids for x in evidence):
        raise ValueError("Every evidence pointer must be an original turn ID")
    if v["speaker_id"] not in SPECIAL and not evidence:
        raise ValueError("Named attribution lacks evidence")
    return {"agent_id":agent,"turn_id":v["turn_id"],
        "speaker_id":v["speaker_id"],"confidence_rating_uncalibrated":n,
        "evidence_turn_ids":evidence,
        "short_evidence_summary":str(v.get("short_evidence_summary",""))[:500]}

def reconcile(turn,votes):
    explicit=turn["structural_signals"]["explicit_speaker_label_candidates"]
    count=len({v["agent_id"] for v in votes})
    proposed=Counter(v["speaker_id"] for v in votes if v["speaker_id"] not in SPECIAL)
    base={"turn_id":turn["turn_id"],"agent_count":count,
          "evidence_turn_ids":sorted({t for v in votes for t in v["evidence_turn_ids"]}),
          "alternatives":[{"speaker_id":key,"votes":n} for key,n in proposed.most_common(3)],
          "confidence_rating_uncalibrated":None}
    if len(explicit)==1:
        return {**base,"speaker_id":explicit[0],
                "status":"explicit_source_caption_label",
                "evidence_turn_ids":[turn["turn_id"]],"explanation":"Unique explicit character prefix in the held text"}
    if count>=2 and len(proposed)==1:
        name=next(iter(proposed))
        reliable={v["agent_id"] for v in votes if v["speaker_id"]==name and
                  v["confidence_rating_uncalibrated"]>=0.75}
        addressees=turn["structural_signals"]["vocative_addressee_candidates_not_speakers"]
        if reliable=={v["agent_id"] for v in votes} and name not in addressees:
            return {**base,"speaker_id":name,"status":"uncalibrated_agent_agreement",
                    "confidence_rating_uncalibrated":min(v["confidence_rating_uncalibrated"] for v in votes),
                    "explanation":"At least two distinct agent IDs agree; not independent verification"}
    return {**base,"speaker_id":"UNKNOWN","status":"unresolved",
            "explanation":"Contradictory, insufficient, self-address or missing evidence"}

def one_version(item):
    meta_file=ROOT/item["manifest"]
    meta=json.loads(meta_file.read_text("utf-8"))
    folder=meta_file.parent/"speaker-attribution"
    if not folder.exists():return None
    vote_dir=folder/"votes"
    vote_files=sorted(vote_dir.glob("*.jsonl")) if vote_dir.exists() else []
    if not vote_files:return None
    turns=rows(folder/"turns.jsonl")
    known={turn["turn_id"]:turn for turn in turns}
    roster=json.loads((folder/"candidate-roster.json").read_text("utf-8"))["candidate_characters"]
    ids={c["character_id"] for c in roster}
    names={c["character_id"]:c["character_name"] for c in roster}
    votes=defaultdict(list)
    for file in vote_files:
        agent=file.stem
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,80}",agent):
            raise ValueError("Invalid vote file agent ID: "+agent)
        seen=set()
        for vote in rows(file):
            v=checked_vote(vote,agent,meta["sha256"],known,ids)
            if v["turn_id"] in seen:raise ValueError("Duplicate agent vote for a turn")
            seen.add(v["turn_id"])
            votes[v["turn_id"]].append(v)
    answer=[reconcile(t,votes[t["turn_id"]]) for t in turns]
    changed=save(folder/"speaker-proposals-reconciled.jsonl",
                 "\n".join(json.dumps(x,ensure_ascii=False,sort_keys=True) for x in answer)+"\n")
    lines=["# PROVISIONAL text-only dialogue for "+meta["episode_id"],"",
           "Source SHA-256: "+meta["sha256"],"",
           "This is not a verified screenplay. Unknown identities remain UNKNOWN.",
           "Provisional scenes are defined by caption gaps, not watched footage.",""]
    last_scene=0
    for t,a in zip(turns,answer):
        if t["provisional_scene_number"]!=last_scene:
            last_scene=t["provisional_scene_number"]
            lines.extend(["","## [PROVISIONAL SCENE "+str(last_scene)+"]",""])
        name=names.get(a["speaker_id"],a["speaker_id"])
        when=f"{t['start_ms']/1000:.1f}s" if t["start_ms"] is not None else "untimed"
        lines.append("**"+name+"** ["+when+"; "+a["status"]+"; "+t["turn_id"]+"]")
        lines.append("")
        # Add indentation, never rewrite the actual caption text.
        lines.extend("    "+line for line in t["text"].splitlines())
        lines.append("")
    changed+=save(folder/"script-provisional.md","\n".join(lines)+"\n")
    statuses=Counter(x["status"] for x in answer)
    return {"episode_id":meta["episode_id"],"version_id":meta["version_id"],
        "total_turns":len(turns),"vote_files":len(vote_files),
        "statuses":dict(statuses),"files_changed":changed,
        "script_path":str((folder/"script-provisional.md").relative_to(ROOT))}

def main():
    reports=[]
    for item in rows(ROOT/"catalog"/"dialogue-index.jsonl"):
        p=one_version(item)
        if p:reports.append(p)
    doc={"series":"night-court-1984","versions_with_proposals":len(reports),
        "status":"Provisional multi-agent votes, not video-verified attribution",
        "uncertainty_rule":"An unsupported or contradictory identity stays UNKNOWN",
        "versions":reports}
    save(ROOT/"catalog"/"speaker-attribution-reconciliation.json",
         json.dumps(doc,indent=2,ensure_ascii=False)+"\n")
    print("Reconciling text-only dialogue:",len(reports),"versions with vote files")

if __name__=="__main__":main()
