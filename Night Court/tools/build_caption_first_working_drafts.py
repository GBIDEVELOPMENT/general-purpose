#!/usr/bin/env python3
"""Caption-first complete-dialogue *working drafts* for the two Night Court pilots.

This is a fast editorial product, not source-audio-certified archival output.
Never replace subtitle wording with a speech-recognizer hypothesis. Preserve
source cue/paragraph order, and enrich only with existing bounded AV evidence.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from build_caption_turns import build as caption_turns

ROOT=Path(__file__).resolve().parents[1]
PILOTS=("S01E01","S09E19")
OUTPUT_NAME="caption-first-working-draft-v1"
CONFLICT_SOURCE=("seasons/S01/S01E01/derived/three-witness-v1/"
                 "targeted-audio-review-queue.json")
EVIDENCE={
 "S01E01":"seasons/S01/S01E01/derived/scene-review-v3/scene-evidence-map.json",
 "S09E19":"seasons/S09/S09E19/derived/scene-review-v1/source-linked-scene.json"
}
CAPS={"S01E01":336,"S09E19":347}
SOURCE_SHA={
 "S01E01":"aa9f77600cd9f2b6f317e4b74ebb98273f632cee1337665e03f0fe712f936496",
 "S09E19":"659beb9c50fabdd1028aac9570999d9a16b36e6d582938e10809cc0c664530b2"
}
SAMPLE_COUNT=8


def read_json(path):
    return json.loads(path.read_text("utf-8"))


def read_jsonl(path):
    return [json.loads(s) for s in path.read_text("utf-8").splitlines() if s.strip()]


def time_label(ms):
    if ms is None:return "untimed"
    return f"{ms//60000:02d}:{ms%60000/1000:06.3f}"


def sample_indices(total, count=SAMPLE_COUNT):
    """Deterministic source-spread controls, not claimed representative statistics."""
    return sorted({1+round(i*(total-1)/(count-1)) for i in range(count)})


def witness(episode, root=ROOT):
    if episode not in PILOTS:raise ValueError("Unknown pilot")
    index=[x for x in read_jsonl(root/"catalog/dialogue-index.jsonl")
           if x["episode_id"]==episode]
    if len(index)!=1:raise ValueError("Missing or duplicate source edition")
    item=index[0]
    path=root/item["manifest"]
    metadata=read_json(path)
    originals=(root/"seasons"/episode[:3]/episode/metadata["original_path"])
    if (metadata["episode_id"]!=episode or
        item["sha256"]!=metadata["sha256"] or
        metadata["sha256"]!=SOURCE_SHA[episode] or
        hashlib.sha256(originals.read_bytes()).hexdigest()!=SOURCE_SHA[episode] or
        metadata["cue_count"]!=CAPS[episode] or
        metadata["declared_complete"] is not False):
        raise ValueError("Wrong, changed, or promoted original source caption witness")
    segments=read_jsonl(root/"seasons"/episode[:3]/episode/metadata["segments_path"])
    if (len(segments)!=CAPS[episode] or
        [c["cue"] for c in segments]!=list(range(1,CAPS[episode]+1)) or
        any(not isinstance(c.get("text"),str) or not c["text"].strip()
                for c in segments)):
        raise ValueError("Missing, empty or reordered source paragraphs")
    timed=episode=="S01E01"
    if metadata["timecoded"] is not timed:
        raise ValueError("No invented timecodes for untimed original")
    if timed and any(type(c["start_ms"]) is not int or
                     type(c["end_ms"]) is not int or
                     not 0<=c["start_ms"]<c["end_ms"]<=1800000
                     for c in segments):
        raise ValueError("Broken source SRT timing")
    if not timed and any(c["start_ms"] is not None or c["end_ms"] is not None
                         for c in segments):
        raise ValueError("Untimed source was assigned fictional original timing")
    units,packets=caption_turns(metadata,segments)
    if sorted({u["cue"] for u in units})!=list(range(1,CAPS[episode]+1)):
        raise ValueError("Candidate turn splitting lost original source caption")
    return item,metadata,segments,units,packets


def review_queue(episode,segments,root=ROOT):
    # Original captions are used as draft dialogue even when models disagree.
    # A mismatch means 'check this passage', NOT 'replace the caption'.
    rows=[]
    marked=set()
    if episode=="S01E01":
        cases=read_json(root/CONFLICT_SOURCE)
        if len(cases)!=16:raise ValueError("Unexpected existing pilot conflict study")
        for case in cases:
            cues=case["original_srt_cue_ids"]
            if (not cues or any(type(c) is not int or not 1<=c<=len(segments) for c in cues)
                or case.get("model_error_or_srt_error_determined") is not False):
                raise ValueError("False model adjudication")
            marked.update(cues)
            rows.append({"priority":"meaningful_model_caption_disagreement",
                         "source_cues":cues,
                         "source_audio_time_proposal_ms":
                            case["original_source_audio_time_ms"],
                         "original_text_preserved":True,
                         "original_audio_listened_to_resolve":False})
    for cue in sample_indices(len(segments)):
        if cue in marked:continue
        rows.append({"priority":"source_spread_agreement_control",
                     "source_cues":[cue],
                     "source_audio_time_proposal_ms":None,
                     "original_text_preserved":True,
                     "original_audio_listened_to_resolve":False})
    return rows


def visual_material(episode,root=ROOT):
    data=read_json(root/EVIDENCE[episode])
    if data["episode_id"]!=episode or data["source_media_sha256"]=="":
        raise ValueError("Wrong original-video evidence edition")
    if episode=="S01E01":
        if (data["original_subtitle_sha256"]!=SOURCE_SHA[episode] or
            data["counts_and_gates"]["source_window_ms"]!=[60000,90000] or
            data["counts_and_gates"]["scene_audiovisual_complete"] is not False):
            raise ValueError("Unreliable original source frame observation")
        observations=[e for e in data["events"] if e["source_kind"] in (
                      "reviewed_static_frame","reviewed_sampled_sequence")]
        if len(observations)!=11:raise ValueError("Observed picture evidence drift")
        return data,observations
    if (data["source_original_untimed_text_sha256"]!=SOURCE_SHA[episode] or
        data["observed_video_excerpt_ms"]!=[900000,925000] or
        data["original_source_paragraphs_still_untimed"] is not True or
        data["original_episode_audiovisual_complete"] is not False):
        raise ValueError("Unreliable untimed-source video evidence")
    observations=[e for e in data["events"] if
                  e["source_kind"]=="sampled_original_video_observation"]
    if len(observations)!=6:raise ValueError("Observed S09 still picture count drift")
    return data,observations


def render_episode(episode,root=ROOT):
    item,metadata,segments,units,packets=witness(episode,root)
    av,observations=visual_material(episode,root)
    queue=review_queue(episode,segments,root)
    ep=read_json(root/"seasons"/episode[:3]/episode/"episode.json")
    if ep["id"]!=episode:raise ValueError("Different episode title metadata")
    timed=bool(metadata["timecoded"])
    pieces=[
      f"# {episode} · {ep['title']}",
      "",
      "CAPTION-FIRST WORKING SCREENPLAY DRAFT  |  EDITORIAL PASS 1",
      "",
      "Original caption dialogue is preserved as the presumptive spoken text.",
      "All held source cues/paragraphs are included in order. This is NOT an",
      "independently verified screenplay or a guarantee of missing-dialogue coverage.",
      "Speaker labels are assigned only when explicitly printed in the source.",
      "Other speakers and most locations require normal editorial reconstruction.",
      "Picture directions below describe only sampled original-image evidence;",
      "no action outside those windows is implied to have been reviewed.",
      "",
      f"Source caption SHA-256: \`{item['sha256']}\`",
      f"Source AVI SHA-256 (visual witness): \`{av['source_media_sha256']}\`",
      f"Source cues: {len(segments)}; subtitle-derived speaking units: {len(units)}",
      f"Dialogue timing: {'original SRT cues' if timed else 'UNTIMED source paragraphs; positions NOT assigned'}",
      f"ASR/caption disputes to review: {16 if timed else 0}; ",
      "",
      "## Working episode dialogue",
      "",
    ]
    # The 12-second gaps are editing navigators; never call them verified scenes.
    grouped={}
    for u in units:grouped.setdefault(u["cue"],[]).append(u)
    source_cues_used=[]
    visual_refs_used=[]
    observation_by_cue={}
    if timed:
        for o in observations:
            if o["source_kind"]=="reviewed_sampled_sequence":
                # Insert after the last original caption whose start precedes
                # the midpoint of the sampled action. No invented speaker link.
                anchor=(o["start_ms"]+o["end_ms"])//2
                eligible=[c["cue"] for c in segments if c["start_ms"]<=anchor]
                if eligible:
                    observation_by_cue.setdefault(eligible[-1],[]).append(o)
    else:
        # Source paragraph 240 is a high-lexical anchor PROPOSAL, not original
        # caption timing. A shared visual passage note is safe, not a claim
        # that paragraph 240 was spoken precisely at 15:00.
        observation_by_cue[240]=observations

    packet_for={}
    for i,p in enumerate(packets,1):
        for uid in p["units"]:packet_for[uid]=(i,p)
    last_packet=None
    if timed:
        pieces.extend(["### OPENING · SETTING REQUIRES PICTURE REVIEW","",
                       "*Dialogue begins in the source captions; this heading does",
                       "not assert a visually confirmed opening location.*",""])
    else:
        pieces.extend(["### OPENING · SETTING REQUIRES PICTURE REVIEW","",
                       "*Original source has no timestamps; paragraph order is retained.*",""])
    visual_started=False
    for c in segments:
        ulist=grouped.get(c["cue"])
        if not ulist:raise ValueError("No dialogue unit for original cue")
        packet_idx,packet=packet_for[ulist[0]["unit_id"]]
        if packet_idx!=last_packet:
            last_packet=packet_idx
            pieces.extend([f"#### Dialogue passage {packet_idx:02d} · "
                           +(f"{time_label(packet['first_start_ms'])} original SRT"
                             if timed else "UNTIMED source order"),
                           "",
                           "*Possible scene break only; based on source-dialogue spacing,"
                           " not on observed camera/location continuity.*" if packet_idx>1
                           else "*Working dialogue passage, not a verified scene boundary.*",
                           ""])
        if timed and not visual_started and c["start_ms"]>=60000:
            visual_started=True
            pieces.extend(["### INT. BOOK-LINED COURT OFFICE · TIME OF DAY UNCONFIRMED","",
                           "*Sampled 01:00–01:30 picture: a desk with papers and",
                           "a telephone, bookcases, a person in lavender and an",
                           "adult in a dark uniform. Names and speakers remain",
                           "unassigned; sampled frames are not continuous action.*",
                           f"Picture research: \`{EVIDENCE[episode]}\`",""])
        for u in ulist:
            source_cues_used.append(u["cue"])
            original=u["source_text"].strip().replace("\r","")
            label=(u["speaker_label_from_source"] or
                   "VOICE · CHARACTER TO IDENTIFY")
            prefix=(f"C{c['cue']:03d}.{u['part']} · "
                    + (time_label(c["start_ms"]) if timed else "UNTIMED"))
            pieces.extend([f"**{label}**  *[{prefix}]*",
                           original,""])
        for observation in observation_by_cue.get(c["cue"],[]):
            if timed:
                pieces.extend([f"*PIC NOTE [{time_label(observation['start_ms'])}"
                               f"–{time_label(observation['end_ms'])}]: "
                               f"{observation['text']}*",
                               f"*Evidence: \`{EVIDENCE[episode]}\`, "
                               f"observation {observation['id']}. "
                               "Sampled frames, not a claimed speaker/action cause.*",""])
                visual_refs_used.append(observation["id"])
            else:
                if not visual_started:
                    visual_started=True
                    pieces.extend(["### INT. SHARED INTERIOR WITH COUNTER AND TABLES · VENUE UNCONFIRMED","",
                                   "*The following picture notes belong to a separate",
                                   "15:00–15:25 sampled source-video passage. Alignment",
                                   "to nearby untimed paragraphs is a lexical proposal.*",""])
                pieces.extend([f"*PIC NOTE [source 15:00–15:25, sampled]: "
                               f"{observation['description']}*",
                               f"*Evidence: \`{EVIDENCE[episode]}\`, "
                               f"{observation['visual_id']}; "
                               "paragraph time and speaker NOT confirmed.*",""])
                visual_refs_used.append(observation["visual_id"])
    if timed and len(visual_refs_used)!=6:raise ValueError("Timed sample action notes lost")
    if not timed and len(visual_refs_used)!=6:raise ValueError("Untimed sample notes lost")
    if sorted(set(source_cues_used))!=list(range(1,len(segments)+1)):
        raise ValueError("An original caption was omitted in screenplay render")
    pieces.extend([
        "## Draft editorial checklist",
        "",
        f"- Original source paragraphs/cues retained: {len(segments)}/{len(segments)}.",
        f"- ASR/SRT mismatch requests: {16 if timed else 0}. "
        "Caption wording is not automatically changed.",
        f"- Source-spread control samples: "
        f"{sum(q['priority']=='source_spread_agreement_control' for q in queue)}.",
        "- All episode location/shot boundaries, named speaker assignments",
        "  and significant physical comedy outside sampled AV windows need editing.",
        "- Full synchronized audiovisual scene audit: NOT DONE.",
        "- Working draft: dialogue-first editorial material; NOT an accepted",
        "  source-complete audiovisual screenplay.",
        ""
    ])
    text="\n".join(pieces)
    manifest={
      "schema":"night-court-caption-first-complete-source-dialogue-working-draft/1",
      "episode_id":episode,"title":ep["title"],
      "original_caption_sha256":SOURCE_SHA[episode],
      "original_video_sha256_for_bounded_visual_sample":av["source_media_sha256"],
      "caption_source_is_default_dialogue":True,
      "asr_may_override_original_caption_automatically":False,
      "source_caption_cues":len(segments),
      "original_source_cue_ids_in_order":list(range(1,len(segments)+1)),
      "written_source_cue_ids_in_order":sorted(set(source_cues_used)),
      "original_source_caption_units":len(units),
      "timed_original_source":timed,
      "source_paragraph_timestamps_invented":False,
      "embedded_source_video_sampled_action_notes":len(visual_refs_used),
      "sampled_visual_evidence_path":EVIDENCE[episode],
      "targeted_original_audio_review_requests":len(queue),
      "targeted_asr_disagreement_requests":sum(
          q["priority"]=="meaningful_model_caption_disagreement" for q in queue),
      "targeted_spread_samples":sum(
          q["priority"]=="source_spread_agreement_control" for q in queue),
      "srt_is_assumed_likely_reliable_not_verified_complete":True,
      "all_source_dialogue_included_in_readable_editing_draft":True,
      "named_speakers_assigned_by_unconfirmed_model":False,
      "scene_spatial_and_physical_comedy_coverage_complete":False,
      "whole_episode_audiovisual_screenplay_accepted":False,
      "quality_state":"COMPLETE_HELD_DIALOGUE_WORKING_DRAFT_VISUAL_AND_SPEAKER_EDIT_PENDING",
      "derived_script_path":f"seasons/{episode[:3]}/{episode}/derived/{OUTPUT_NAME}/screenplay-draft.md",
      "review_request_path":f"seasons/{episode[:3]}/{episode}/derived/{OUTPUT_NAME}/targeted-review.json",
      "source_input_release_limit":"owner-directed source research; redistribution rights not independently established"
    }
    return text,manifest,queue


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--episode",choices=PILOTS,required=True)
    p.add_argument("--output-root",type=Path,default=ROOT)
    p.add_argument("--check",action="store_true")
    a=p.parse_args()
    script,manifest,queue=render_episode(a.episode)
    base=(a.output_root/"seasons"/a.episode[:3]/a.episode/
          "derived"/OUTPUT_NAME)
    outputs={
      "screenplay-draft.md":script+"\n",
      "draft-manifest.json":json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",
      "targeted-review.json":json.dumps(queue,indent=2,ensure_ascii=False)+"\n"
    }
    if a.check:
        for name,content in outputs.items():
            f=base/name
            if not f.is_file() or f.read_text("utf-8")!=content:
                raise ValueError("Stale/missing checked-in caption-first output: "+str(f))
    else:
        base.mkdir(parents=True,exist_ok=True)
        for name,content in outputs.items():
            (base/name).write_text(content,encoding="utf-8")
    print(f"{a.episode}: {manifest['source_caption_cues']} complete source cues, "
          f"{manifest['targeted_original_audio_review_requests']} targeted checks, "
          "unaccepted working script; no automatic audio/scene claims")


if __name__=="__main__":
    main()
