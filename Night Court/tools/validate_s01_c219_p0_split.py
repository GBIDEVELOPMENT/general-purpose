#!/usr/bin/env python3
"""Propose exact original S01 subtitle C219 two-voice split, never certify actors."""
import hashlib
import json
from pathlib import Path
from build_pilot_fan_beat_cards import ROOT,load_witness
LEDGER=ROOT/"research/s01-c219-speaker-boundary-v1.json"
SHA="aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496"

def validate(root=ROOT,ledger=LEDGER):
    data=json.loads(Path(ledger).read_text("utf-8"))
    m,cues=load_witness(Path(root),"S01E01")
    if (m["sha256"]!=SHA or m["timecoded"] is not True
        or data.get("schema")!="night-court-s01-source-exact-speaker-split-proposal/1"
        or data.get("episode_id")!="S01E01" or data.get("source_caption_sha256")!=SHA
        or data.get("source_ref")!="C219.1"
        or data.get("unique_split_before")!="- Yeah."
        or data.get("original_source_timing_preserved") is not True
        or data.get("independent_video_audio_actor_identity_reviewed") is not False
        or data.get("independent_original_turn_boundary_verified") is not False
        or data.get("provisional_roles")!=[None,None]):
        raise ValueError("Original S01 source speaker turn/actor review provenance invalid")
    cue=cues[218]
    text=cue["text"]
    if text.count("- Yeah.")!=1 or cue.get("start_ms")!=879532 or cue.get("end_ms")!=882330:
        raise ValueError("Original C219 source/timing or cue text unexpected")
    at=text.index("- Yeah.")
    before,after=text[:at],text[at:]
    if not before.strip() or not after.strip() or before+after!=text:
        raise ValueError("C219 source characters lost at provisional voice switch")
    return {"source_ref":"C219.1","original_source_text_sha256":hashlib.sha256(text.encode()).hexdigest(),
            "source_cue_start_ms":cue["start_ms"],"source_cue_end_ms":cue["end_ms"],
            "proposed_unicode_split_offset":at,
            "provisional_speaker_roles":[None,None],
            "independently_accepted_original_voice_or_turns":0}
if __name__=="__main__":
    x=validate()
    print("S01 C219 exact original source dash-delimited reply split is reversible; no actor verified")
