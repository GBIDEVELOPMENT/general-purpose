#!/usr/bin/env python3
"""Validate sampled original S01E01 visual observations; NEVER grant script acceptance.

Full low-res JPEGs and canonical frame-index reside in the short-lived
owner-only Actions artifact. This permanently retained packet stores SHA-bound
selected frames and AI-described sampled image states, not frame/media bytes.
"""
from __future__ import annotations
import copy
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EP = ROOT / "seasons/S01/S01E01/derived"
PKT = EP / "visual-review-v3/expanded-sampled-observations.json"
MANIFEST = EP / "editorial-review-v1/review-cut-manifest.json"
SCENE = EP / "scene-review-v3/scene-evidence-map.json"
SHA = re.compile(r"^[0-9a-f]{64}$")
KINDS = {
 "change_between_adjacent_sampled_views",
 "sampled_stages_not_continuous_action",
 "overlapped_images_near_transition",
 "sequential_sampled_poses",
 "sequential_sampled_positions_at_excerpt_end",
}


def validate(packet=None, manifest=None, scene=None):
    p = copy.deepcopy(packet if packet is not None else json.loads(PKT.read_text("utf-8")))
    m = manifest if manifest is not None else json.loads(MANIFEST.read_text("utf-8"))
    s = scene if scene is not None else json.loads(SCENE.read_text("utf-8"))
    if (p.get("schema") != "night-court-s01e01-expanded-sampled-visual-observations/1"
        or p.get("episode_id") != "S01E01"
        or p.get("source_original_video_sha256") != m["source_video_sha256"]
        or p.get("source_original_video_sha256") != s["source_media_sha256"]
        or p.get("source_original_caption_sha256") != m["source_caption_sha256"]
        or p.get("source_original_caption_sha256") != s["original_subtitle_sha256"]):
        raise ValueError("Original S01E01 AVI/SRT source provenance mismatch")
    if (p.get("source_evidence_run") != 40065126174
        or p.get("source_artifact_id") != 12549082053
        or p.get("source_artifact_sha256") !=
            "a29f7bdbb869cacc81bcc13f26e35678fcdaee84ac3dc48dd3a4ebd20d367f28"
        or p.get("source_frame_index_sha256") !=
            "d041fc452cd1a8a2f97f95b92bd3313cdd6931c60b185f699c0bc8f66cd63347"):
        raise ValueError("Unrecognized actual original-source frame artifact evidence")
    if (p.get("source_window_ms") != [56912, 93074]
        or p.get("padded_visual_sampling_window_ms") != [56912, 93162]
        or p.get("sample_count") != 145
        or p.get("original_evidence_task_count") != len(m["tasks"])
        or len(m["tasks"]) != 17
        or p.get("independent_continuous_video_acceptances") != 0
        or p.get("independently_listened_voice_turns") != 0
        or p.get("finished_production_script") is not False):
        raise ValueError("Visual-only source scope or acceptance gate changed")
    contacts=p.get("contact_sheets")
    expected_contact_hashes=[
        "669fa0fc9fc48f81bf913c00fbab1210d907d04962bdd08ded64fe97aab84b91",
        "2d9e523823c3f8c52d45abecd636b555f0ff59d3317aeefde6b402d5d9482fe9",
        "22ce3b6d46f992ae212fb5631996fdd3c60577a48bdc4e5e2e8331f9480253e1",
        "7bffb3e095bdf0cbebe276866990c1f045a0406942ff4da57660af0d8ac68cd8",
    ]
    if (not isinstance(contacts,list) or len(contacts)!=4 or
        any(c.get("file")!=f"contact-{i:02d}.jpg"
            or c.get("sha256")!=expected_contact_hashes[i-1]
            for i,c in enumerate(contacts,1))):
        raise ValueError("Original source review contact sheet evidence missing")
    rows=p.get("observations")
    if not isinstance(rows,list) or len(rows)!=6:
        raise ValueError("Expected six new original-source sampled observations")
    seen=set()
    for i,obs in enumerate(rows,1):
        if obs.get("observation_id")!=f"S01-V3-{i:02d}" or obs["observation_id"] in seen:
            raise ValueError("Duplicate or missing new sampled observation")
        seen.add(obs["observation_id"])
        a,b=obs.get("nominal_interval_ms",[None,None])
        if (type(a) is not int or type(b) is not int
            or not 56912<=a<=b<=93162 or obs.get("class") not in KINDS
            or not isinstance(obs.get("description"),str) or len(obs["description"])<35):
            raise ValueError("Observation lacks bounded source visual description")
        if (obs.get("reviewer_state")!="ai_reviewed_sampled_frames_only"
            or any(obs.get(k) is not False for k in (
            "speaker_identity_verified","continuous_original_video_reviewed",
            "exact_action_onset_verified","source_subtitle_synchronization_verified"))):
            raise ValueError("A sampled still cannot certify source dialogue or continuous acting")
        frames=obs.get("frame_evidence")
        if not isinstance(frames,list) or len(frames)<2:
            raise ValueError("Missing actual image SHA anchors")
        previous=0
        for f in frames:
            n=f.get("sample_index")
            if (type(n) is not int or n<=previous or n>145 or
                f.get("nominal_video_time_ms")!=56912+(n-1)*250 or
                f.get("file")!=f"frames/frame-{n:03d}.jpg"
                or not SHA.fullmatch(f.get("sha256","")) or
                not a<=f["nominal_video_time_ms"]<=b):
                raise ValueError("Source frame index/hash/time evidence corrupted")
            previous=n
    return {"original_episode_id":"S01E01","source_sha_consistent":True,
            "source_frame_observations":6,"reviewed_contact_sheets":4,
            "independent_continuous_av_acceptances":0,
            "source_video_audio_or_image_bytes_stored":False}


if __name__ == "__main__":
    print(json.dumps(validate(),indent=2))
