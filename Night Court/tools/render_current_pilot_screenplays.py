#!/usr/bin/env python3
"""Private screenplay-layout layer for the two original Night Court pilots.

Groups contiguous *provisionally* same-named dialogue for reading, without
asserting true performed-turn boundaries or changing immutable sources.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
from build_pilot_fan_beat_cards import ROOT, load_witness

SOURCE = {
    "S01E01": ("aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496", 404, True),
    "S09E19": ("659beb9c50fabdd1028aac9570999d9a16b36e6d582938e10809cc0c664530b2", 347, False),
}
INPUT = "pilot-source-episode-turns-v15.jsonl"
INPUT_MANIFEST = "pilot-source-episode-turns-v15-manifest.json"

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def time_envelope(row):
    value = row.get("source_original_times_ms")
    if isinstance(value, dict):
        value = [value]
    if not value:
        return None
    if not isinstance(value, list):
        raise ValueError("Malformed original cue times")
    start = min(x["start_ms"] for x in value)
    end = max(x["end_ms"] for x in value)
    if type(start) is not int or type(end) is not int or not 0 <= start < end:
        raise ValueError("Invalid original cue time envelope")
    return (start, end)

def check_source(rows, manifest, binary, witnesses):
    expected = {
        "source_role_record_sha256": sha(binary),
        "original_caption_source_units": 751,
        "provisional_named_original_source_units": 621,
        "original_source_units_still_UNKNOWN": 130,
        "current_provisional_speaking_blocks": 726,
        "new_performer_turns_independently_audio_verified": 0,
        "new_original_actor_identities_certified": 0,
    }
    if len(rows) != 726 or any(manifest.get(k) != v for k,v in expected.items()):
        raise ValueError("Private v15 source-first manifest/count drift")
    roles = defaultdict(set)
    blocks = set()
    last = (-1, 0)
    for row in rows:
        ep = row.get("episode_id")
        if ep not in SOURCE:
            raise ValueError("Unexpected original pilot")
        ref = row.get("original_source_part_refs")
        if not isinstance(ref,list) or not ref or len(ref)!=len(set(ref)):
            raise ValueError("Missing/duplicate source cue refs")
        numbers=[]
        for part in ref:
            if (not isinstance(part,str) or len(part)!=6 or part[0]!="C"
                or not part[1:4].isdigit() or part[4]!="." or
                not part[5].isdigit() or part[5]=="0"):
                raise ValueError("Malformed original source part ref")
            numbers.append(int(part[1:4]))
        if numbers != sorted(numbers):
            raise ValueError("Out-of-order source part references")
        src, count, timed = SOURCE[ep]
        meta, cues = witnesses[ep]
        if (meta["sha256"]!=src or meta["timecoded"] is not timed
            or row.get("original_source_sha256")!=src
            or any(n<1 or n>len(cues) for n in numbers)):
            raise ValueError("Original held cue SHA/identity changed")
        if ep=="S09E19" and (row.get("source_original_times_ms") is not None
                             or row.get("original_source_untimed") is not True):
            raise ValueError("Invented original S09 timing")
        pos=(list(SOURCE).index(ep),numbers[0])
        if pos<last:
            raise ValueError("Original episode cue order changed")
        last=pos
        bid=row.get("reading_block_id")
        if not isinstance(bid,str) or not bid or bid in blocks:
            raise ValueError("Missing/repeated source reading block")
        blocks.add(bid)
        if (not isinstance(row.get("caption_text"),str) or not row["caption_text"].strip()
            or row.get("speaker_turn_boundary_verified") is not False
            or row.get("actor_face_or_voice_independently_verified") is not False):
            raise ValueError("Source text or original AV review status changed")
        role=row.get("candidate_role")
        if role is not None and (not isinstance(role,str) or not role):
            raise ValueError("Malformed provisional role")
        if ep=="S01E01":
            time_envelope(row)
        for part in ref:
            roles[(ep,part)].add(role)
    if {ep:sum(k[0]==ep for k in roles) for ep in SOURCE}!={"S01E01":404,"S09E19":347}:
        raise ValueError("Immutable original source-unit coverage changed")
    if sum(None not in r for r in roles.values())!=621:
        raise ValueError("Provisional source roles changed")
    return {"original_source_units":len(roles),"named_provisional":621,"unknown":130}

def display_join(left, right):
    if (left["episode_id"]!=right["episode_id"] or
        left.get("candidate_role") is None or
        left.get("candidate_role")!=right.get("candidate_role") or
        set(left["original_source_part_refs"]) & set(right["original_source_part_refs"])):
        return False
    # Protect large genuine S01 cue gaps from being formatted as one utterance.
    if left["episode_id"]=="S01E01":
        a,b=time_envelope(left),time_envelope(right)
        if a and b and b[0]-a[1]>2500:
            return False
    return True

def group_rows(rows, compact=True):
    result={ep:[] for ep in SOURCE}
    for row in rows:
        groups=result[row["episode_id"]]
        if compact and groups and display_join(groups[-1][-1],row):
            groups[-1].append(row)
        else:
            groups.append([row])
    return result

def render(rows, compact=True):
    grouped=group_rows(rows,compact)
    manuscripts={}
    sidecars={}
    summary={}
    for ep, groups in grouped.items():
        src, count, timed=SOURCE[ep]
        lines=[f"# {ep}: Night Court (1984–1992), working screenplay",
               "", "**Provisional dialogue reading only.**",
               "Original character identities and display continuations are not",
               "independently audio-verified. Scene boundaries, delivery and physical",
               "business await source AV inspection. S09 source is entirely untimed.",
               f"Original caption source SHA-256: {src}", "",
               "## Dialogue (scenes awaiting verification)", ""]
        side=[]
        for group_id, members in enumerate(groups,1):
            role=members[0].get("candidate_role")
            suffix=(" · DISPLAY CONTINUATION, UNVERIFIED" if len(members)>1
                    else " · PROVISIONAL" if role else " · UNKNOWN")
            lines.extend(["### "+(role or "UNIDENTIFIED SPEAKER")+suffix, ""])
            for row in members:
                # Keep the private source-derived text literally, no punctuation,
                # dash, linebreak, word or inferred scene insertions.
                lines.extend("    "+part for part in row["caption_text"].split("\n"))
                lines.append("")
                side.append({
                    "reading_block_id":row["reading_block_id"],
                    "source_reading_ref":row["source_reading_ref"],
                    "original_source_part_refs":row["original_source_part_refs"],
                    "source_sha256":row["original_source_sha256"],
                    "exact_rendered_caption_sha256":sha(row["caption_text"].encode("utf-8")),
                    "candidate_role":role,
                    "display_group_id":group_id,
                    "display_join_not_performed_turn_proof":len(members)>1,
                    "source_cue_times_not_subturn_times_ms":time_envelope(row) if timed else None,
                    "source_exact_character_span":row.get("source_exact_character_span"),
                    "original_source_unicode_spans_v13":row.get("original_source_unicode_spans_v13"),
                    "actual_original_av_reviewer_accepted":False,
                })
        manuscripts[ep]="\n".join(lines).rstrip()+"\n"
        sidecars[ep]=side
        summary[ep]={"source_units":count, "source_blocks":len(side),
                     "display_groups":len(groups),
                     "display_joins_unverified":len(side)-len(groups),
                     "original_caption_timed":timed,
                     "full_original_audio_video_accepted":False}
    return manuscripts,sidecars,summary

def build(root:Path,private_v15:Path,output:Path,compact=True):
    if output.resolve().is_relative_to(root.resolve()):
        raise ValueError("Private source dialogue must never be written inside repo")
    binary=(private_v15/INPUT).read_bytes()
    if len(binary)>16_000_000:
        raise ValueError("Unexpected huge private reader")
    manifest=json.loads((private_v15/INPUT_MANIFEST).read_text("utf-8"))
    rows=[json.loads(t) for t in binary.decode("utf-8").splitlines() if t.strip()]
    witnesses={ep:load_witness(root,ep) for ep in SOURCE}
    counts=check_source(rows,manifest,binary,witnesses)
    manuscripts,sidecars,summary=render(rows,compact)
    output.mkdir(parents=True,exist_ok=True)
    report={"schema":"night-court-private-pilot-screenplay-layout/1",
            "source_v15_reader_sha256":sha(binary),
            "source_unit_counts":counts,
            "episodes":summary,
            "new_independently_verified_performed_turns":0,
            "new_independently_verified_actor_voices":0,
            "scene_review_complete":False,
            "manuscript_sha256":{}}
    for ep,text in manuscripts.items():
        (output/f"{ep}-working-screenplay.md").write_text(text,"utf-8")
        report["manuscript_sha256"][ep]=sha(text.encode("utf-8"))
        (output/f"{ep}-working-screenplay-provenance.jsonl").write_text(
            "".join(json.dumps(record,sort_keys=True,ensure_ascii=False)+"\n"
                    for record in sidecars[ep]),"utf-8")
    (output/"working-screenplay-layout-manifest.json").write_text(
        json.dumps(report,indent=2,sort_keys=True)+"\n","utf-8")
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,default=ROOT)
    p.add_argument("--source-first-v15",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--no-layout-continuations",action="store_true")
    a=p.parse_args()
    report=build(a.root,a.source_first_v15,a.output,
                 compact=not a.no_layout_continuations)
    print("Two working pilot screenplay drafts rendered, no AV certs; ",
          {k:v["display_groups"] for k,v in report["episodes"].items()})

if __name__=="__main__":
    main()
