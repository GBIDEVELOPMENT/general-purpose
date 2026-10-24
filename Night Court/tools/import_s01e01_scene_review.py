#!/usr/bin/env python3
"""Import one specific private Actions scene packet into permanent repo evidence.

No FTP secret, no video/audio imports, no trusting unexpected artifact paths.
This is image and source-cue provenance, NOT AV-complete scene validation.
"""
from pathlib import Path
import json, hashlib, shutil, sys

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/"seasons/S01/S01E01/derived/scene-review-v1"
EXPECTED_MEDIA_SHA="5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962"
EXPECTED_SRT_SHA="aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496"
EXPECTED_SECONDS=[60,63,66,69,72,75,78,81,84,87]

def digest(data):
    return hashlib.sha256(data).hexdigest()

def main(source):
    witness=json.loads((source/"evidence.json").read_text("utf-8"))
    observations=json.loads((DEST/"visual-observations.json").read_text("utf-8"))
    if witness["schema"]!="night-court-s01e01-scene-evidence/1" or witness["episode_id"]!="S01E01":
        raise ValueError("Incompatible scene packet")
    if witness["source_media_sha256"]!=EXPECTED_MEDIA_SHA or witness["dialogue_source_sha256"]!=EXPECTED_SRT_SHA:
        raise ValueError("Source hashes changed")
    if witness["source_audio_window_ms"]!=[60000,90000]:
        raise ValueError("Wrong audio/video interval")
    if [f["video_time_ms"] for f in witness["frame_evidence"]] != [s*1000 for s in EXPECTED_SECONDS]:
        raise ValueError("Wrong frame sampling schedule")
    if len(witness["mixed_audio_windows"])!=5 or witness["completeness_verified"]:
        raise ValueError("Unexpected scene packet confidence state")
    if observations["source_media_sha256"]!=EXPECTED_MEDIA_SHA:
        raise ValueError("Review belongs to another source")
    if observations["cut_interval_ms"]!=witness["source_audio_window_ms"]:
        raise ValueError("Visual review and source windows disagree")
    allowed={"evidence.json","source-passage.md"}|{"frames/source-%04ds.jpg"%s for s in EXPECTED_SECONDS}
    actual={str(p.relative_to(source)) for p in source.rglob("*") if p.is_file()}
    if actual!=allowed:
        raise ValueError("Artifact contains unexpected files: "+str(actual.symmetric_difference(allowed)))
    for f in witness["frame_evidence"]:
        path=source/f["file"]
        content=path.read_bytes()
        if not content.startswith(b"\xff\xd8\xff") or len(content)>200000 or digest(content)!=f["sha256"]:
            raise ValueError("Frame evidence failed JPEG+SHA validation")
    # The source passage must contain each original caption text, not fabricated dialogue.
    text=(source/"source-passage.md").read_text("utf-8")
    if not all(x["text"] in text for x in witness["source_cues"]):
        raise ValueError("Some source cues absent from review page")
    for name in sorted(allowed):
        p=DEST/name
        if p.exists() and p.read_bytes()!=(source/name).read_bytes():
            raise ValueError("Refuse to overwrite changed retained source file: "+name)
        p.parent.mkdir(parents=True,exist_ok=True)
        if not p.exists():shutil.copyfile(source/name,p)
    print("Scene packet retained: 10 verified JPEG frames, source cue manuscript, audio evidence metadata")

if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("Need private reviewed artifact folder")
    main(Path(sys.argv[1]))
