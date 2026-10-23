#!/usr/bin/env python3
"""Create provenance-linked candidate conversation units from HELD caption cues.

This code does not assign speakers from turn order or quoted names. A speaker
is recorded only when the source cue itself has an unambiguous explicit prefix
or WebVTT voice annotation. Leading '-' typography can mean separate speakers,
but the speaker remains UNKNOWN. Gap boundaries are provisional.
"""
from collections import Counter
from pathlib import Path
import json,re

ROOT=Path(__file__).resolve().parents[1]
GAP_MS=12000
PREFIX=re.compile(r"^\s*([A-Z][A-Z0-9 '.-]{1,32}):\s+(.+)$",re.S)
VTT=re.compile(r"^\s*<v\s+([^>]+)>(.*?)(?:</v>)?\s*$",re.S|re.I)
START_DASH=re.compile(r"^\s*[-–—]\s+(.+)$",re.S)

def save(file,body):
    file.parent.mkdir(parents=True,exist_ok=True)
    if not file.exists() or file.read_text("utf-8")!=body:
        file.write_text(body,"utf-8")
        return True
    return False

def parse_caption(cue,metadata):
    text=cue["text"].replace("\r","").strip()
    if not text:return []
    # Only captions whose multiple physical lines BOTH start with dashes are
    # split into distinct unattributed turns; a single leading dash is ambiguous.
    lines=[line.strip() for line in text.splitlines() if line.strip()]
    if len(lines)>=2 and all(START_DASH.match(line) for line in lines):
        parts=[START_DASH.match(line).group(1) for line in lines]
        indication="multiple_leading_dash_subtitle_lines"
    else:
        parts=[text]
        indication="one_caption_unit"
    units=[]
    for sub_index,part in enumerate(parts,1):
        speaker=None;label=None
        voice=VTT.match(part)
        if voice:
            speaker=voice.group(1).strip()
            label="explicit_webvtt_voice"
        else:
            pref=PREFIX.match(part)
            if pref:
                speaker=pref.group(1).strip()
                label="explicit_caption_speaker_prefix"
        units.append({
            "episode_id":metadata["episode_id"],"source_version_id":metadata["version_id"],
            "source_sha256":metadata["sha256"],
            "cue":cue["cue"],"part":sub_index,
            "unit_id":f'{metadata["episode_id"]}:{metadata["version_id"]}:C{cue["cue"]:05d}.{sub_index}',
            "start_ms":cue["start_ms"],"end_ms":cue["end_ms"],
            "source_text":part,
            "speaker_label_from_source":speaker,
            "speaker_basis":label,
            "speaker_identity_status":"explicit_unverified_source_label" if speaker else "UNKNOWN",
            "subdivision_evidence":indication,
            "scope":"candidate_caption_turn_not_authenticated_speech_turn",
            "source_manifest":"seasons/"+metadata["episode_id"][:3]+"/"+metadata["episode_id"]+"/dialogue/versions/"+metadata["version_id"]+"/manifest.json"
        })
    return units

def build(metadata,cues):
    units=[]
    for cue in cues:units.extend(parse_caption(cue,metadata))
    groups=[]
    current=[]
    previous_end=None
    for row in units:
        beginning=row["start_ms"]
        is_gap=(beginning is not None and previous_end is not None
                and beginning-previous_end>GAP_MS)
        if is_gap and current:
            groups.append(current);current=[]
        current.append(row)
        if row["end_ms"] is not None:
            previous_end=max(previous_end or row["end_ms"],row["end_ms"])
    if current:groups.append(current)
    packets=[]
    for i,group in enumerate(groups,1):
        packets.append({
            "packet_id":f'{metadata["episode_id"]}:{metadata["version_id"]}:P{i:03d}',
            "episode_id":metadata["episode_id"],"version_id":metadata["version_id"],
            "source_sha256":metadata["sha256"],
            "unit_count":len(group),
            "first_cue":group[0]["cue"],"last_cue":group[-1]["cue"],
            "first_start_ms":group[0]["start_ms"],"last_end_ms":group[-1]["end_ms"],
            "speaker_explicit_labels":sorted({u["speaker_label_from_source"] for u in group
                                               if u["speaker_label_from_source"]}),
            "boundary":"gap_over_12s_or_track_start_not_verified_scene_change",
            "units":[u["unit_id"] for u in group]
        })
    return units,packets

def main():
    index=ROOT/"catalog"/"dialogue-index.jsonl"
    sources=[json.loads(line) for line in index.read_text("utf-8").splitlines() if line.strip()] if index.exists() else []
    cover=Counter()
    rows=[]
    all_packets=[]
    totals=Counter()
    for source in sources:
        manifest=ROOT/source["manifest"]
        meta=json.loads(manifest.read_text("utf-8"))
        ep=meta["episode_id"];directory=ROOT/"seasons"/ep[:3]/ep
        cues=[json.loads(line) for line in (directory/meta["segments_path"]).read_text("utf-8").splitlines() if line.strip()]
        units,packets=build(meta,cues)
        outdir=manifest.parent
        save(outdir/"candidate-turns.jsonl","\n".join(json.dumps(u,ensure_ascii=False,sort_keys=True) for u in units)+"\n")
        save(outdir/"conversation-packets.jsonl","\n".join(json.dumps(p,ensure_ascii=False,sort_keys=True) for p in packets)+"\n")
        for u in units:
            totals["units"]+=1
            if u["speaker_label_from_source"]:totals["explicit_source_labels"]+=1
            if u["subdivision_evidence"]=="multiple_leading_dash_subtitle_lines":totals["units_split_from_multi_dash_caption"]+=1
        totals["packets"]+=len(packets)
        cover[ep]+=1
        rows.append({"episode_id":ep,"version_id":meta["version_id"],
                     "source_sha256":meta["sha256"],"source_cues":len(cues),
                     "candidate_turns":len(units),
                     "source_explicit_speaker_labels":sum(bool(u["speaker_label_from_source"]) for u in units),
                     "candidate_conversation_packets":len(packets)})
        all_packets.extend({"episode_id":ep,"version_id":meta["version_id"],
                            "packet_id":p["packet_id"],"unit_count":p["unit_count"],
                            "first_start_ms":p["first_start_ms"],"last_end_ms":p["last_end_ms"]}
                            for p in packets)
    result={
       "series":"night-court-1984","input_held_source_witnesses":len(sources),
       "episodes_with_turns":len(cover),"totals":dict(totals),
       "speaker_model":"explicit_source_labels_only_no_character_inference",
       "conversation_boundary_model":"12s_caption_gap_heuristic_not_scene_segmentation",
       "warnings":[
         "A caption unit is not necessarily an uninterrupted character speech turn.",
         "Source name prefixes may be mistaken or may denote sounds, not people.",
         "Separate leading-dash lines are split without assigning identities.",
         "Unknown speakers remain unknown, and speaker mentions are not identifications.",
         "The immutable source caption text and timing stay authoritative over derived units."
       ],
       "versions":rows}
    save(ROOT/"catalog"/"caption-turn-coverage.json",json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    save(ROOT/"catalog"/"caption-conversation-packets.jsonl","\n".join(json.dumps(x,ensure_ascii=False,sort_keys=True) for x in all_packets)+("\n" if all_packets else ""))
    print("Speaker-anchor preparatory corpus:",len(sources),"source tracks;",len(cover),
          "episodes;",totals["units"],"cue-linked units;",totals["packets"],"candidate packets;",
          totals["explicit_source_labels"],"explicit labels")
if __name__=="__main__":main()
