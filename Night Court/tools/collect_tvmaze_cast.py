#!/usr/bin/env python3
"""Collect original Night Court (show ID 1489) cast/crew and episode guest credits.

Uses documented CC BY-SA TVmaze API. Names/roles are *credits*, not guaranteed
onscreen appearances. Preserve series credits separately from episode credits.
Nine season-level embedded guestcast requests avoid 193 individual calls.
"""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import json
import time

ROOT=Path(__file__).resolve().parents[1]
API="https://api.tvmaze.com"
UA="NightCourtPrivateResearch/0.2 (archival factual metadata; TVmaze attribution)"
SHOW=1489

def request(path):
    url=API+path
    for attempt in range(3):
        try:
            with urlopen(Request(url,headers={"User-Agent":UA,"Accept":"application/json"}),timeout=20) as response:
                return json.load(response)
        except HTTPError as e:
            if e.code not in (429,500,502,503,504) or attempt==2:
                raise
        except (URLError,TimeoutError):
            if attempt==2:raise
        time.sleep(2*(attempt+1))

def slim_person(item):
    if not isinstance(item,dict):return None
    return {"tvmaze_id":item.get("id"),"name":item.get("name"),"url":item.get("url")}

def role_record(item):
    return {"person":slim_person(item.get("person")),
            "character":slim_person(item.get("character"))}

def write_if_changed(path,obj):
    new=json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+"\n"
    if path.exists() and path.read_text("utf-8")==new:return False
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(new,encoding="utf-8")
    return True

def main():
    try:
        maincast=request(f"/shows/{SHOW}/cast")
        crew=request(f"/shows/{SHOW}/crew")
        seasons=request(f"/shows/{SHOW}/seasons")
    except Exception as exc:
        print("TVmaze series-level request failed, retaining existing archive:",str(exc))
        return
    if not isinstance(maincast,list) or not isinstance(crew,list) or not isinstance(seasons,list):
        print("Unexpected API response; refusing to overwrite")
        return

    cast=[role_record(x) for x in maincast if isinstance(x,dict)]
    main_crew=[{"person":slim_person(x.get("person")),"type":x.get("type")} for x in crew if isinstance(x,dict)]
    attribution={"source":"TVmaze","show_id":SHOW,"api_docs":"https://www.tvmaze.com/api",
        "licensing":"CC BY-SA (see TVmaze API license)","retrieval_strategy":"show cast, show crew, season episodes with embedded guestcast",
        "warning":"Series cast data does not establish participation in each episode"}
    changed=0
    changed+=write_if_changed(ROOT/"catalog"/"tvmaze-main-cast.json",{"attribution":attribution,"credits":cast})
    changed+=write_if_changed(ROOT/"catalog"/"tvmaze-main-crew.json",{"attribution":attribution,"credits":main_crew})
    counts={"seasons_attempted":0,"seasons_succeeded":0,"episode_records_with_embedding":0,
            "episode_records_empty_guestcast":0,"episode_records_with_guests":0,
            "guest_credit_edges":0,"episode_mismatches":[],"season_errors":{}}
    for row in seasons:
        season=row.get("number")
        season_id=row.get("id")
        if not isinstance(season,int) or season<1 or season>9 or not isinstance(season_id,int):
            continue
        counts["seasons_attempted"]+=1
        try:
            episodes=request(f"/seasons/{season_id}/episodes?embed=guestcast")
            if not isinstance(episodes,list):raise ValueError("expected list")
        except Exception as exc:
            counts["season_errors"][str(season)]=str(exc)
            continue
        counts["seasons_succeeded"]+=1
        for ep in episodes:
            nr=ep.get("number") if isinstance(ep,dict) else None
            if not isinstance(nr,int) or nr<1:continue
            key=f"S{season:02d}E{nr:02d}"
            dest=ROOT/"seasons"/f"S{season:02d}"/key/"episode.json"
            if not dest.exists():continue
            e=json.loads(dest.read_text("utf-8"))
            if e.get("tvmaze_episode_id")!=ep.get("id"):
                counts["episode_mismatches"].append({"id":key,"local":e.get("tvmaze_episode_id"),"remote":ep.get("id")})
                continue
            embedded=ep.get("_embedded",{})
            if "guestcast" not in embedded:continue
            raw=embedded["guestcast"]
            if not isinstance(raw,list):continue
            guest=[role_record(x) for x in raw if isinstance(x,dict)]
            e.setdefault("credits",{})["guest_cast"]=guest
            e["credits"]["guest_cast_source"]={
                "provider":"TVmaze","url":f"https://www.tvmaze.com/episodes/{ep['id']}",
                "endpoint":f"{API}/seasons/{season_id}/episodes?embed=guestcast",
                "license":"CC BY-SA (TVmaze published terms)",
                "status":"explicit_guestcast_collection"}
            counts["episode_records_with_embedding"]+=1
            counts["guest_credit_edges"]+=len(guest)
            counts["episode_records_empty_guestcast" if not guest else "episode_records_with_guests"]+=1
            changed+=write_if_changed(dest,e)
        time.sleep(0.4)
    report={"source":attribution,"counts":counts,
       "note":"Coverage count is for explicit API embeddings only, not proof that an episode had no uncredited guests."}
    changed+=write_if_changed(ROOT/"catalog"/"tvmaze-guestcast-coverage.json",report)
    print("Updated",changed,"files. Guestcast embedding coverage:",counts["episode_records_with_embedding"],
          "episodes, guest credit edges:",counts["guest_credit_edges"],
          "season failures:",counts["season_errors"],"mismatches:",len(counts["episode_mismatches"]))

if __name__=="__main__":main()
