#!/usr/bin/env python3
"""Reconcile original Night Court summary with actual checked-in dialogue holdings.

All counts originate from immutable dialogue index and canonical coverage.
Never infer "AV complete" from an SRT, transcript, or source-page pointer.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
def main():
    status_path=ROOT/"catalog"/"archive-status.json"
    status=json.loads(status_path.read_text("utf-8"))
    coverage=json.loads((ROOT/"catalog"/"dialogue-coverage.json").read_text("utf-8"))
    queue=json.loads((ROOT/"catalog"/"dialogue-source-queue.json").read_text("utf-8"))
    quality=json.loads((ROOT/"catalog"/"dialogue-quality.json").read_text("utf-8"))
    rows=[json.loads(x) for x in (ROOT/"catalog"/"dialogue-index.jsonl").read_text("utf-8").splitlines() if x.strip()]
    by_type={kind:sum(x["format"]==kind for x in rows) for kind in ("srt","vtt","txt")}
    timed=by_type["srt"]+by_type["vtt"]
    online=[x for x in rows if "subtitle cat" in x["edition"].casefold()]
    online_timed=sum(x["format"] in ("srt","vtt") for x in online)
    owner_timed=timed-online_timed
    held=coverage["episodes_with_held_dialogue"]
    independently_verified=coverage["independently_verified_complete_episodes"]
    if not (coverage["total_episodes"]==193 and len(rows)==coverage["held_dialogue_versions"]
            and held==quality["episodes_with_witnesses"]==193
            and quality["source_witnesses"]==len(rows)
            and not queue["ranked_missing_episode_ids"]
            and independently_verified==quality["independently_verified_complete_episodes"]
            and owner_timed==35 and online_timed==157 and by_type["txt"]==1):
        raise ValueError("Source counts do not reconcile against the original-series archive")
    status.update({
      "caption_files_stored":timed,
      "episodes_with_held_dialogue":held,
      "dialogue_versions_stored":len(rows),
      "independently_video_verified_complete_episodes":independently_verified,
      "dialogue_source_format_counts":by_type,
      "owner_supplied_original_seasons_1_2_timed_tracks":owner_timed,
      "third_party_source_page_timed_caption_tracks_held":online_timed,
      "third_party_source_page_untimed_dialogue_witnesses_held":by_type["txt"],
      "held_episodes_with_timecoded_dialogue":sum(
          r["held_timed_caption_tracks"]>0 for r in coverage["rows"]),
      "held_episodes_with_untimed_only_dialogue":sum(
          r["held_dialogue_versions"]>0 and r["held_timed_caption_tracks"]==0 for r in coverage["rows"]),
      "source_material_status":(
          "193 original-series episode dialogue witnesses held, comprising 192 timed English "
          "SRT sources (35 from owner-supplied S01-S02 archives, 157 externally acquired) "
          "plus S09E19 source-page-derived untimed original dialogue text. "
          "All sources have provenance; none have been independently AV-verified complete."
      ),
    })
    status["sources"]["subtitle_cat_subtitle_files_held"]=online_timed
    status["distinct_sources_warning"]=(
        f'{status["source_pointer_count_including_repeated_series_indexes"]} research references '
        "include repeated series/index links and must not be added to the count of physically "
        "held dialogue witnesses. Neither online source retention nor subtitle timestamps "
        "establish audiovisual completeness or speaker identity."
    )
    content=json.dumps(status,indent=2,ensure_ascii=False)+"\n"
    if not status_path.exists() or status_path.read_text("utf-8")!=content:
        status_path.write_text(content,encoding="utf-8")
    print(f"RECONCILED: {held}/193 episodes, {timed} timed witnesses, {by_type['txt']} untimed, "
          f"{independently_verified} AV-complete")

if __name__=="__main__":main()
