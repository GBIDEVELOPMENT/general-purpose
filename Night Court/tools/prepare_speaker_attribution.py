#!/usr/bin/env python3
"""Build text-only speaker-attribution work packets from actually held captions.

Deterministic, offline and attribution-neutral. Splits only *explicit*
multi-speaker caption typography; does not guess speakers from style.
The output is preparation for agents, not an automatically reconstructed script.
"""
from __future__ import annotations
from collections import Counter
from html import unescape
from pathlib import Path
import json
import re
import unicodedata

ROOT=Path(__file__).resolve().parents[1]
EPISODES=ROOT/"seasons"
INDEX=ROOT/"catalog"/"dialogue-index.jsonl"
CAST=ROOT/"catalog"/"tvmaze-main-cast.json"
PACKET_LIMIT=48
PACKET_OVERLAP=6
GAP_SCENE_MS=30000

# Canonical TVmaze names may differ from the names used in dialogue.
# All aliases remain hypotheses for matching labels/addressees; never
# evidence that the character appears in a given episode.
KNOWN_ALIASES={
 "Harold T. Stone":["Harry","Harry Stone","Judge Stone","Judge Harry Stone"],
 "Dan Fielding":["Dan"],
 "Bull Shannon":["Bull"],
 "Mac Robinson":["Mac"],
 "Lana Wagner":["Lana"],
 "Selma Hacker":["Selma"],
 "Florence Kleiner":["Flo","Florence"],
 "Christine Sullivan":["Christine"],
 "Roz Russell":["Roz"],
 "Billie Young":["Billie"],
 "Liz Williams":["Liz"],
 "Sheila Gardner":["Sheila"],
 "Quon Le":["Quon Le"],
 "Art Fensterman":["Art","Fensterman"]
}
STOP_ALIASES={"the","a","i","you","me","her","his","him","she","he","it",
 "dr","mr","mrs","ms","miss","judge","your honor","court","man","woman","boy",
 "girl","officer","cop","lawyer","judge stone","first","second"}

def dump(obj):
    return json.dumps(obj,ensure_ascii=False,sort_keys=True)

def save(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    if not path.exists() or path.read_text("utf-8")!=data:
        path.write_text(data,"utf-8")
        return 1
    return 0

def norm(s):
    return unicodedata.normalize("NFKC",s).strip().casefold()

def canon(s):
    return re.sub(r"\s+"," ",re.sub(r"<[^>]*>"," ",unescape(s))).strip()

def cast_roster(episode):
    mains=json.loads(CAST.read_text("utf-8"))["credits"]
    guests=episode.get("credits",{}).get("guest_cast",[])
    out={}
    for role_type,items in (("series_wide_cast_only",mains),
                            ("episode_specific_guest_credit",guests)):
        for item in items:
            c=item.get("character") or {}
            if c.get("tvmaze_id") is None:continue
            key=f"tvmaze:{c['tvmaze_id']}"
            name=c.get("name") or ""
            if not name:continue
            aliases=[name,*KNOWN_ALIASES.get(name,[])]
            parts=name.split()
            if len(parts)>1 and parts[0].casefold() not in STOP_ALIASES:
                aliases.append(parts[0])
            aliases=list(dict.fromkeys(x for x in aliases if norm(x) not in STOP_ALIASES))
            if key not in out:
                out[key]={"character_id":key,"character_name":name,
                    "actor_name":(item.get("person") or {}).get("name"),
                    "credit_scope":role_type,"aliases":aliases}
            elif role_type=="episode_specific_guest_credit":
                out[key]["credit_scope"]=role_type
    return sorted(out.values(),key=lambda d:(d["credit_scope"]!="episode_specific_guest_credit",d["character_name"]))

def explicit_colon_speaker(text,roster):
    pattern=re.match(r"^\s*(?:\[(?P<bracket>[A-Za-z][A-Za-z .'-]{1,35})\]|(?P<name>[A-Za-z][A-Za-z .'-]{1,35}))\s*:\s+\S",text)
    if not pattern:return []
    label=norm(pattern.group("bracket") or pattern.group("name"))
    return [r["character_id"] for r in roster
            if label in {norm(a) for a in r["aliases"]}]

def addressed_people(text,roster):
    candidates=[]
    t=canon(text)
    for r in roster:
        for alias in r["aliases"]:
            if len(alias)<3:continue
            # Vocative syntax. A name anywhere in a sentence is NOT
            # necessarily the addressee; do not classify arbitrary mentions.
            quoted=re.escape(alias)
            p=rf"(?i)(?:^|[,!?]\s+|\b(?:hey|hi|listen|thanks|thank you|okay|oh)\s+){quoted}\s*[,!?]"
            if re.search(p,t):
                candidates.append(r["character_id"])
                break
    return sorted(set(candidates))

def pieces(text):
    """Split strong typography, retaining original cue and exact text pieces."""
    lines=[line for line in text.replace("\r\n","\n").split("\n") if line.strip()]
    if not lines:return []
    dash=lambda s:bool(re.match(r"^\s*[-–—]\s+\S",s))
    marked=[i for i,line in enumerate(lines) if dash(line)]
    # Multiple dashes strongly indicate two speakers. A later dash after
    # an undashed opening line is also a plausible new speaker.
    if len(marked)>=2 or (len(lines)>=2 and 0 not in marked and any(i>0 for i in marked)):
        groups=[]
        current=[]
        for i,line in enumerate(lines):
            if current and i in marked:
                groups.append("\n".join(current))
                current=[]
            current.append(line)
        if current:groups.append("\n".join(current))
        return [(g,"explicit_caption_dash_segment") for g in groups]
    return [("\n".join(lines),"unsplit_caption_cue")]

def make_turns(episode,source,roster):
    rows=[json.loads(line) for line in source.read_text("utf-8").splitlines() if line.strip()]
    scene=1
    prev_end=None
    turns=[]
    for cue in rows:
        a,b=cue.get("start_ms"),cue.get("end_ms")
        if a is not None and prev_end is not None and a-prev_end>=GAP_SCENE_MS:
            scene+=1
        if b is not None:
            prev_end=b if prev_end is None else max(prev_end,b)
        segments=pieces(cue["text"])
        if len(segments)>8:raise ValueError("Unexpected complex caption segmentation")
        for idx,(raw,method) in enumerate(segments):
            # cue index always references the exact held source segment.
            turns.append({
                "turn_id":f"{episode['id']}:C{cue['cue']:05d}:{idx+1}",
                "source_cue":cue["cue"],"piece_number":idx+1,
                "start_ms":a,"end_ms":b,
                "text":raw,
                "piece_method":method,
                "provisional_scene_number":scene,
                "scene_boundary_quality":"timing_gap_heuristic_not_a_verified_scene",
                "structural_signals":{
                    "explicit_speaker_label_candidates":explicit_colon_speaker(raw,roster),
                    "vocative_addressee_candidates_not_speakers":addressed_people(raw,roster),
                    "leading_speaker_dash":bool(re.match(r"^\s*[-–—]\s+",raw)),
                    "source_cue_split_into_multiple_pieces":len(segments)>1,
                    "contains_multiline_text":"\n" in raw
                },
                "speaker":"UNKNOWN",
                "speaker_status":"unattributed_not_inferred",
                "attribution_confidence":None,
                "evidence":[]})
    return turns

def packages(turns,roster,meta):
    rows=[]
    index=0
    while index<len(turns):
        end=min(len(turns),index+PACKET_LIMIT)
        batch=turns[index:end]
        rows.append({
           "packet_id":f"{meta['episode_id']}:{meta['version_id']}:P{len(rows)+1:03d}",
           "episode_id":meta["episode_id"],"version_id":meta["version_id"],
           "source_sha256":meta["sha256"],
           "span":{"first_turn_id":batch[0]["turn_id"],
                   "last_turn_id":batch[-1]["turn_id"],
                   "index_start":index,"index_end_exclusive":end},
           "candidate_characters":roster,
           "speaker_options":["UNKNOWN","UNIDENTIFIED_GUEST","OFFSCREEN_OR_CROWD"],
           "utterances":batch,
           "task":"Infer speaker identity globally; return evidence and alternatives, never edit any source text."
        })
        if end==len(turns):break
        index=end-PACKET_OVERLAP
    return rows

def prepare_one(item):
    manifest=ROOT/item["manifest"]
    meta=json.loads(manifest.read_text("utf-8"))
    ep=EPISODES/item["episode_id"][:3]/item["episode_id"]
    episode=json.loads((ep/"episode.json").read_text("utf-8"))
    if episode["id"]!=meta["episode_id"] or item["sha256"]!=meta["sha256"]:
        raise ValueError("Episode or source identity does not agree with version manifest")
    if meta["format"] not in ("srt","vtt","txt"):
        return None
    roster=cast_roster(episode)
    segments=ep/meta["segments_path"]
    turns=make_turns(episode,segments,roster)
    pack=packages(turns,roster,meta)
    output=manifest.parent/"speaker-attribution"
    source={
      "episode_id":item["episode_id"],"version_id":item["version_id"],
      "source_sha256":item["sha256"],
      "roster_basis":"TVmaze episode guest credits and series-level main cast; never proof of appearance",
      "candidate_characters":roster,
      "unknown_categories":["UNKNOWN","UNIDENTIFIED_GUEST","OFFSCREEN_OR_CROWD"],
      "segmentation_warning":"Caption lines can span speakers, and a single speaker can span many cues. Only explicit typographic splits are made.",
      "speaker_assignment_status":"none_proposed_by_this_deterministic_stage",
      "provisional_scene_status":"long silence heuristic; NOT verified location or scene"
    }
    changed=0
    changed+=save(output/"candidate-roster.json",json.dumps(source,indent=2,ensure_ascii=False)+"\n")
    changed+=save(output/"turns.jsonl","\n".join(dump(t) for t in turns)+"\n")
    changed+=save(output/"agent-packets.jsonl","\n".join(dump(p) for p in pack)+"\n")
    return {"episode_id":item["episode_id"],"version_id":item["version_id"],
            "turns":len(turns),"source_cues":meta["cue_count"],
            "explicit_dash_split_turns":sum(t["piece_method"]=="explicit_caption_dash_segment" for t in turns),
            "possible_explicit_labels":sum(bool(t["structural_signals"]["explicit_speaker_label_candidates"]) for t in turns),
            "possible_vocatives":sum(bool(t["structural_signals"]["vocative_addressee_candidates_not_speakers"]) for t in turns),
            "provisional_scenes":max(t["provisional_scene_number"] for t in turns),
            "characters_roster_size":len(roster),"packets":len(pack),
            "source_manifest":item["manifest"],"derived_path":str(output.relative_to(ROOT)),
            "files_changed":changed}

def main():
    if not INDEX.exists():raise ValueError("Missing archived dialogue index")
    items=[json.loads(s) for s in INDEX.read_text("utf-8").splitlines() if s.strip()]
    reports=[]
    for item in items:
        result=prepare_one(item)
        if result:reports.append(result)
    report={
        "series":"night-court-1984","version_count":len(reports),
        "episodes_with_packets":len({x["episode_id"] for x in reports}),
        "caption_cues":sum(x["source_cues"] for x in reports),
        "attribution_units":sum(x["turns"] for x in reports),
        "packets":sum(x["packets"] for x in reports),
        "explicit_speaker_names_assigned":0,
        "authoritative_assignments":0,
        "status":"attribution work packets only; no character-to-line claims",
        "limits":[
           "No audio/video, no guarantee of character attribution",
           "Episode guest credits and show-wide cast are priors, not proof",
           "Caption typographical dashes are imperfect indicators of speaker change",
           "Provisional scene boundaries are only time-gap indicators",
           "No script is treated as canonical without source-level evidence and uncertainty handling"
        ],
        "versions":reports
    }
    save(ROOT/"catalog"/"speaker-attribution-preparation.json",json.dumps(report,indent=2)+"\n")
    print("Prepared",report["attribution_units"],"unattributed units in",
          report["packets"],"agent work packets across",
          report["episodes_with_packets"],"episodes;",report["caption_cues"],"source cues")

if __name__=="__main__":main()
