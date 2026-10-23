#!/usr/bin/env python3
"""Summarize episode-credit and caption evidence for provisional scene participants.

Inputs are the existing owner-supplied source-preserved captions and the
episode's TVmaze guest credits + show-wide cast roster. Output never assigns
speakers to unlabeled turns; direct address is *addressee* evidence only.
Provisional scene boundaries come from caption gaps, not observed camera cuts.
"""
from collections import Counter,defaultdict
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/"catalog"/"dialogue-index.jsonl"

def load_jsonl(path):
    return [json.loads(x) for x in path.read_text("utf-8").splitlines() if x.strip()]

def write(path,obj):
    data=json.dumps(obj,indent=2,ensure_ascii=False,sort_keys=True)+"\n"
    if not path.exists() or path.read_text("utf-8")!=data:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(data,"utf-8")
        return 1
    return 0

def scene_summary(number,turns,roster):
    lookup={c["character_id"]:c for c in roster}
    speaker_labels=defaultdict(list)
    addressee_mentions=defaultdict(list)
    unknown_signals=0
    for turn in turns:
        identity=turn["turn_id"]
        signals=turn["structural_signals"]
        labeled=signals.get("explicit_speaker_label_candidates",[])
        addressed=signals.get("vocative_addressee_candidates_not_speakers",[])
        if len(labeled)==1 and labeled[0] in lookup:
            speaker_labels[labeled[0]].append(identity)
        else:
            unknown_signals+=1
        for person in addressed:
            if person in lookup:addressee_mentions[person].append(identity)
    identified=[]
    for key in sorted(set(speaker_labels)|set(addressee_mentions)):
        role=lookup[key]
        explicit=speaker_labels.get(key,[])
        address=addressee_mentions.get(key,[])
        identified.append({
            "character_id":key,"character_name":role["character_name"],
            "actor_name":role.get("actor_name"),
            "credit_scope":role["credit_scope"],
            "explicit_source_speaker_label_turn_ids":explicit,
            "addressed_by_name_turn_ids":address,
            "speaker_hypothesis_strength":"strong_explicit_label" if explicit else "addressee_only_not_a_speaker",
            "reported_scene_presence":"uncertain_from_text_only",
            "evidence_note":"An addressed person is a possible listener, not the speaker of that turn."
        })
    identified.sort(key=lambda r:(
        -len(r["explicit_source_speaker_label_turn_ids"]),
        -len(r["addressed_by_name_turn_ids"]),
        r["character_name"].casefold()))
    implicit_guest=[{
        "character_id":r["character_id"],"character_name":r["character_name"],
        "actor_name":r.get("actor_name"),"basis":"episode_specific_guest_credit_only",
        "scene_presence":"unverified"
    } for r in roster if r["credit_scope"]=="episode_specific_guest_credit"
        and r["character_id"] not in set(speaker_labels)|set(addressee_mentions)]
    implicit_series=[{
        "character_id":r["character_id"],"character_name":r["character_name"],
        "actor_name":r.get("actor_name"),"basis":"series_wide_cast_credit_only",
        "scene_presence":"unverified"
    } for r in roster if r["credit_scope"]=="series_wide_cast_only"
        and r["character_id"] not in set(speaker_labels)|set(addressee_mentions)]
    times=[t["start_ms"] for t in turns if t["start_ms"] is not None]
    ends=[t["end_ms"] for t in turns if t["end_ms"] is not None]
    return {
        "scene_ordinal":number,
        "scene_status":"time_gap_hypothesis_not_screen_verified",
        "source_turn_count":len(turns),
        "first_source_turn_id":turns[0]["turn_id"],"last_source_turn_id":turns[-1]["turn_id"],
        "first_start_ms":min(times) if times else None,
        "last_end_ms":max(ends) if ends else None,
        "turns_with_no_unique_speaker_label":unknown_signals,
        "textually_signaled_possible_participants":identified,
        "credited_guest_roles_without_textual_scene_signal":implicit_guest,
        "series_cast_without_textual_scene_signal":implicit_series,
        "uncredited_participants_must_remain_possible":True,
        "limits":[
           "A name spoken in direct address is a listener hypothesis, not a speaker label.",
           "Episode guest cast credits prove credited role only, not participation in this particular scene.",
           "Show-wide cast credit does not establish an episode appearance.",
           "A timestamp gap does not identify an actual scene boundary.",
           "UNKNOWN, UNIDENTIFIED_GUEST and OFFSCREEN_OR_CROWD must remain candidate classes."
        ]
    }

def summarize_version(index):
    manifest=ROOT/index["manifest"]
    source=json.loads(manifest.read_text("utf-8"))
    folder=manifest.parent/"speaker-attribution"
    roster_file=folder/"candidate-roster.json"
    turns_file=folder/"turns.jsonl"
    if not roster_file.exists() or not turns_file.exists():
        raise ValueError("Speaker packet preparation required before scene evidence: "+str(folder))
    c=json.loads(roster_file.read_text("utf-8"))
    if c["source_sha256"]!=index["sha256"] or c["episode_id"]!=index["episode_id"]:
        raise ValueError("Roster source identity mismatch")
    roster=c["candidate_characters"]
    turns=load_jsonl(turns_file)
    by_scene=defaultdict(list)
    for t in turns:
        if not str(t["turn_id"]).startswith(index["episode_id"]+":"):
            raise ValueError("Cross-episode dialogue turn")
        by_scene[t["provisional_scene_number"]].append(t)
    result={
      "episode_id":index["episode_id"],
      "version_id":index["version_id"],
      "source_sha256":index["sha256"],
      "source_manifest":index["manifest"],
      "source_caption_turns":len(turns),
      "credit_roster_count":len(roster),
      "provisional_scene_count":len(by_scene),
      "character_to_scene_evidence_status":"participant_hypotheses_only_not_attributed_speakers",
      "scenes":[scene_summary(n,scenes,roster) for n,scenes in sorted(by_scene.items())]
    }
    changed=write(folder/"scene-participation-evidence.json",result)
    return result,changed

def main():
    if not INDEX.exists():raise ValueError("Missing dialogue index")
    versions=load_jsonl(INDEX)
    records=[]
    changed=0
    for item in versions:
        r,c=summarize_version(item)
        records.append(r)
        changed+=c
    totals={
      "series":"night-court-1984",
      "episodes":len({r["episode_id"] for r in records}),
      "versions":len(records),
      "provisional_scenes":sum(r["provisional_scene_count"] for r in records),
      "scenes_with_explicit_speaker_labels":sum(
          any(c["explicit_source_speaker_label_turn_ids"] for c in s["textually_signaled_possible_participants"])
          for r in records for s in r["scenes"]),
      "scenes_with_name_address_signals":sum(
          any(c["addressed_by_name_turn_ids"] for c in s["textually_signaled_possible_participants"])
          for r in records for s in r["scenes"]),
      "source_limits":"Participant hypotheses only. No new speaker assignments or AV-verified appearances.",
      "versions_index":[{"episode_id":r["episode_id"],"version_id":r["version_id"],
                         "source_sha256":r["source_sha256"],
                         "scene_count":r["provisional_scene_count"],
                         "file":str((ROOT/r["source_manifest"]).parent.relative_to(ROOT)/"speaker-attribution"/"scene-participation-evidence.json")}
                        for r in records]}
    changed+=write(ROOT/"catalog"/"scene-participation-evidence.json",totals)
    print("Scene participant evidence:",totals["versions"],"versions,",totals["provisional_scenes"],
          "provisional scenes, name-address signals in",totals["scenes_with_name_address_signals"],
          "scenes, explicit speaker label signals in",totals["scenes_with_explicit_speaker_labels"],
          "scenes; changed",changed,"files")

if __name__=="__main__":main()
