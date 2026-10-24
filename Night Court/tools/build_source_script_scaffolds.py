#!/usr/bin/env python3
"""Create complete original Night Court subtitle-only reading-script scaffolds.

The output is not a verified screenplay. Source caption turns and 12-second
conversation gaps are useful *editorial units*, NOT actual scene cuts or
performer/character identification. Source witnesses remain untouched.
"""
from collections import Counter
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/"catalog"/"dialogue-index.jsonl"
STATUS=ROOT/"catalog"/"source-script-scaffold-coverage.json"
FILENAME="source-script-scaffold-v1.md"

def jsonl(path):
    if not path.is_file():raise ValueError("Required source missing: "+str(path))
    return [json.loads(x) for x in path.read_text("utf-8").splitlines() if x.strip()]

def clock(ms):
    if ms is None:return "UNTIMED"
    if not isinstance(ms,int) or ms<0:raise ValueError("Negative/invalid source cue time")
    return f"{ms//60000:02}:{(ms%60000)/1000:06.3f}"

def render_source(item):
    ep=item["episode_id"]
    if not (len(ep)==6 and ep.startswith("S") and ep[3]=="E"):
        raise ValueError("Unexpected original-series episode ID")
    meta=json.loads((ROOT/item["manifest"]).read_text("utf-8"))
    episode=json.loads((ROOT/"seasons"/ep[:3]/ep/"episode.json").read_text("utf-8"))
    if (episode["id"]!=ep or meta["episode_id"]!=ep or meta["sha256"]!=item["sha256"]
        or meta["version_id"]!=item["version_id"] or meta["declared_complete"]):
        raise ValueError("Source or episode identity drift")
    folder=(ROOT/item["manifest"]).parent
    units=jsonl(folder/"candidate-turns.jsonl")
    packets=jsonl(folder/"conversation-packets.jsonl")
    segments=jsonl(ROOT/"seasons"/ep[:3]/ep/meta["segments_path"])
    original_cues={x["cue"] for x in segments}
    if len(segments)!=meta["cue_count"] or original_cues!=set(range(1,len(segments)+1)):
        raise ValueError("Missing original source caption cues")
    ids=[x["unit_id"] for x in units]
    if len(set(ids))!=len(ids):raise ValueError("Duplicate speaker-agnostic original caption units")
    byid={x["unit_id"]:x for x in units}
    if any(x["source_sha256"]!=item["sha256"] or x["episode_id"]!=ep for x in units):
        raise ValueError("Candidate turns have mixed source fingerprints")
    coverage=[v for p in packets for v in p["units"]]
    if len(coverage)!=len(units) or sorted(coverage)!=sorted(ids):
        raise ValueError("Lost or duplicated caption turn during conversation grouping")
    if {x["cue"] for x in units}!=original_cues:
        raise ValueError("Scaffold omitted an original caption cue")
    if not packets:raise ValueError("No candidate conversation units")
    lines=[
       "# "+ep+" · "+episode["title"],
       "",
       "**SOURCE-ONLY READING-SCRIPT SCAFFOLD · NOT A PRODUCTION SCREENPLAY**",
       "",
       f"- Original-source version: \u0060{item['version_id']}\u0060",
       f"- Source SHA-256: \u0060{item['sha256']}\u0060",
       f"- Source format: \u0060{meta['format']}\u0060",
       f"- Original cue count: {len(segments)}; derived caption units: {len(units)}",
       f"- Provisional dialogue blocks: {len(packets)} (12-second subtitle-gap heuristic, not scene detection)",
       "- Scene settings, entrances, physical action, speech identity, voice tone, audience reactions and original broadcast cut: **NOT VERIFIED**.",
       "- Source text reproduced for private owner-directed research; third-party reuse permissions not independently established.",
       "",
       "## Source dialogue timeline",""]
    for idx,pack in enumerate(packets,1):
        if pack["packet_id"].split(":")[-1]!=f"P{idx:03d}":
            raise ValueError("Out-of-order conversation block IDs")
        heading=f"### Dialogue block {idx:03d}"
        if pack["first_start_ms"] is not None:
            heading+=f' | {clock(pack["first_start_ms"])}–{clock(pack["last_end_ms"])} source SRT time'
        else:heading+=" | UNTIMED SOURCE PARAGRAPHS"
        lines.extend([heading,"",
           "*Setting / actual scene boundary: not observed; dialogue-gap block only.*",""])
        for uid in pack["units"]:
            u=byid[uid]
            start=u["start_ms"];end=u["end_ms"]
            if (start is None)!=(end is None):
                raise ValueError("Partially timed caption witness")
            timing=(f"{clock(start)}–{clock(end)}" if start is not None else "UNTIMED")
            speaker=(f'UNVERIFIED SOURCE LABEL: {u["speaker_label_from_source"]}'
                     if u["speaker_label_from_source"] else "UNIDENTIFIED VOICE")
            lines.append(f'**[{timing} · C{u["cue"]:05d}.{u["part"]} · {speaker}]**')
            # Preserve original raw line content; display each physical line as a quotation.
            lines += ["> "+line for line in u["source_text"].splitlines()]
            lines.append("")
    lines += [
       "## Research and acceptance gates","",
       "- Confirm source text against the actual source-video edition and full runtime.",
       "- Identify actual scene headings from shot and location evidence, not caption gaps.",
       "- Review speech turns/overlap, diarize voices and ground character identities.",
       "- Describe visible entrances, gestures, props, facial reactions and physical comedy from frames/clips.",
       "- Add reviewable acoustic pitch, pauses, emphasis and expressive-delivery observations.",
       "- Independently verify completeness before calling this an episode production script.",
       "",
       "**No audiovisual completeness, stage direction, voice identity or performance interpretation is certified by this scaffold.**",""
    ]
    return "\n".join(lines),{
        "episode_id":ep,"title":episode["title"],"source_format":meta["format"],
        "source_sha256":item["sha256"],"version_id":meta["version_id"],
        "caption_cues":len(segments),"unattributed_caption_units":len(units),
        "candidate_conversation_blocks":len(packets),
        "timed":bool(meta["timecoded"]),
        "scene_headings_verified":0,"source_audio_alignment_verified":False,
        "speaker_identity_verified":False,"stage_directions_video_verified":False,
        "complete_script_verified":False,
        "derived_path":f"seasons/{ep[:3]}/{ep}/derived/{FILENAME}"
    }

def main():
    sources=jsonl(INDEX)
    if len(sources)!=193 or len({x["episode_id"] for x in sources})!=193:
        raise ValueError("Expected 193 distinct original episodes in source index")
    result=[]
    for s in sources:
        text,detail=render_source(s)
        path=ROOT/detail["derived_path"]
        path.parent.mkdir(parents=True,exist_ok=True)
        if not path.exists() or path.read_text("utf-8")!=text:
            path.write_text(text,"utf-8")
        result.append(detail)
    result.sort(key=lambda x:x["episode_id"])
    summary={
       "schema":"night-court-source-reading-script-scaffolds/1",
       "series":"night-court-1984",
       "episodes_with_source_scaffold":len(result),
       "source_witnesses":len(sources),
       "timed_subtitle_scaffolds":sum(x["timed"] for x in result),
       "untimed_transcript_scaffolds":sum(not x["timed"] for x in result),
       "source_cues":sum(x["caption_cues"] for x in result),
       "caption_units":sum(x["unattributed_caption_units"] for x in result),
       "dialogue_gap_blocks":sum(x["candidate_conversation_blocks"] for x in result),
       "video_verified_production_scenes":0,
       "script_status":"SOURCE_ONLY_NOT_AV_VERIFIED",
       "original_caption_files_modified":False,
       "limits":["No source evidence of script scene locations or physical stage directions",
                 "Caption silence gap != camera cut or verified scene",
                 "Unknown speaker identities remain UNKNOWN",
                 "S09E19 original displayed paragraphs have no source timecodes",
                 "Rights and source-cut audiovisual completeness unverified"],
       "episodes":result
    }
    STATUS.write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n","utf-8")
    print(f"Reading scaffolds: {len(result)} original episodes; "
          f"{summary['timed_subtitle_scaffolds']} timed, "
          f"{summary['untimed_transcript_scaffolds']} untimed; "
          f"{summary['caption_units']} source-backed turns, no invented stage directions")

if __name__=="__main__":main()
