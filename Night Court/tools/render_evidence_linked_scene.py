#!/usr/bin/env python3
"""Render caption and visually observed evidence without inventing story facts.

Narrative layers are never trusted to alter original caption words; a line
with no independently accepted speaker appears as UNATTRIBUTED VOICE.
"""
import argparse,json,re
from pathlib import Path

def read(p):
    return json.loads(p.read_text("utf-8"))

def timecode(ms):
    if not isinstance(ms,int) or ms<0:raise ValueError("Invalid media timestamp")
    return f"{ms//60000:02d}:{ms//1000%60:02d}.{ms%1000:03d}"

def render(packet,review):
    if packet.get("episode_id")!=review.get("episode_id") or packet.get("source_media_sha256")!=review.get("source_media_sha256"):
        raise ValueError("Review and evidence do not share episode and source identity")
    if not packet.get("source_cues") or not packet.get("frame_evidence"):
        raise ValueError("Need original captions and actual frame evidence")
    if review.get("audiovisual_completeness_verified"):
        raise ValueError("Renderer cannot certify a scene")
    known_frames={f["file"] for f in packet["frame_evidence"]}
    events=[]
    for c in packet["source_cues"]:
        if not isinstance(c.get("text"),str) or not c["text"].strip():
            raise ValueError("Caption source text is missing")
        events.append((c["start_ms"],1,c))
    for obs in review.get("time_bounded_observations",[]):
        if set(obs.get("evidence",[]))-known_frames:
            raise ValueError("Visual observation refers to uncollected source frame")
        if obs.get("motion_inference") is not False:
            raise ValueError("Motion claims cannot be inferred from isolated source stills")
        events.append((obs["time_ms"],0,obs))
    events.sort(key=lambda x:(x[0],x[1]))
    title=review.get("scene_heading_candidate","")
    if not title or "\n" in title:raise ValueError("Provisional scene heading missing")
    out=[f"# {packet['episode_id']} · evidence-linked scene candidate",
         "",f"## {title}","",
         "> **PROVISIONAL.** Original captions are not confirmed synchronized to the video.",
         "> Still-frame evidence is not continuous motion; all speakers remain unattributed.",
         "",f"Source episode SHA-256: \`{packet['source_media_sha256']}\`",
         f"Original caption SHA-256: \`{packet['dialogue_source_sha256']}\`",
         f"Video interval: {timecode(packet['source_audio_window_ms'][0])}–{timecode(packet['source_audio_window_ms'][1])}",
         "", "### Timeline (dialogue and verified single-frame observations)",""]
    for ms,kind,obj in events:
        if kind==0:
            out.append(f"**[{timecode(ms)} | VISUAL STILL]** {obj['description']}")
            out.append("Evidence: "+", ".join(f"\`{p}\`" for p in obj["evidence"]))
        else:
            out.append(f"**[{timecode(ms)} | CAPTION C{obj['cue']:04d} | UNATTRIBUTED VOICE]**")
            out.append(obj["text"])
        out.append("")
    out.extend(["### Scene and interpretation notes","",
        "The scene heading is a provisional, visually observed working setting.",
        "Speaker identities, inferred motivations, comic mechanism, delivery, shot transitions",
        "and movements between images remain separate hypotheses until verified.",
        "",f"Source audio SHA-256: \`{packet['source_audio_wav_sha256']}\`",
        "", "**AV completeness certified:** No"])
    return "\n".join(out)+"\n"

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--evidence",required=True,type=Path)
    a.add_argument("--observations",required=True,type=Path)
    a.add_argument("--output",required=True,type=Path)
    args=a.parse_args()
    s=render(read(args.evidence),read(args.observations))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    if args.output.exists() and args.output.read_text("utf-8")!=s:
        raise ValueError("Refuse overwrite of independently edited scene script")
    args.output.write_text(s,"utf-8")
    print("Evidence-linked scene draft rendered without character/scene completeness assertions")

if __name__=="__main__":main()
