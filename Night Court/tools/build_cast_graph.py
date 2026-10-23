#!/usr/bin/env python3
"""Build TVmaze credited person/character relationships and production pairings.

Main-series cast is show-wide; guest credits are episode-scoped. Never label
either as witnessed on-screen appearances. Credits can be incomplete.
"""
from collections import Counter,defaultdict
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
COUNTS=[13,22,22,22,22,22,24,24,22]

def dump(path,obj):
    if isinstance(obj,(dict,list)):obj=json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+"\n"
    if not path.exists() or path.read_text("utf-8")!=obj:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(obj,"utf-8")

def main():
    castfile=ROOT/"catalog"/"tvmaze-main-cast.json"
    crewfile=ROOT/"catalog"/"tvmaze-main-crew.json"
    if not castfile.exists():
        print("TVmaze cast collection unavailable; no inferred replacements")
        return
    cast=json.loads(castfile.read_text("utf-8"))
    crew=json.loads(crewfile.read_text("utf-8")) if crewfile.exists() else {"credits":[]}
    people={}
    characters={}
    edges=[]
    per_person=defaultdict(set)
    per_character=defaultdict(set)
    writing=Counter()
    direction=Counter()
    pairings=Counter()
    missing=0

    def add_entity(place,source):
        if not isinstance(source,dict) or source.get("tvmaze_id") is None:return None
        key=f"tvmaze:{source['tvmaze_id']}"
        place[key]={"id":key,"display_name":source.get("name"),"url":source.get("url")}
        return key

    def edge(actor,role,scope,episode=None):
        p=add_entity(people,actor)
        c=add_entity(characters,role)
        if not p or not c:return
        item={"person_id":p,"character_id":c,"credit_scope":scope,
              "source":"TVmaze","evidence_url":actor.get("url")}
        if episode is not None:
            item["episode_id"]=episode
            per_person[p].add(episode)
            per_character[c].add(episode)
        edges.append(item)
    for row in cast["credits"]:
        edge(row.get("person"),row.get("character"),"series_main_cast")
    for s,total in enumerate(COUNTS,1):
        for ep in range(1,total+1):
            key=f"S{s:02d}E{ep:02d}"
            data=json.loads((ROOT/"seasons"/f"S{s:02d}"/key/"episode.json").read_text("utf-8"))
            director=data.get("credits",{}).get("director")
            writer=data.get("credits",{}).get("writer_credit_display")
            if director:direction[director]+=1
            if writer:writing[writer]+=1
            if director and writer:pairings[(director,writer)]+=1
            if "guest_cast_source" not in data.get("credits",{}):
                missing+=1
                continue
            for row in data["credits"]["guest_cast"]:
                edge(row.get("person"),row.get("character"),"episode_guest_cast",key)
    graph={
       "source":"TVmaze public CC BY-SA API /shows/1489/cast and season episode guestcast",
       "source_url":"https://www.tvmaze.com/api",
       "show_id":1489,
       "series_main_cast_credits":sum(x["credit_scope"]=="series_main_cast" for x in edges),
       "episode_guest_cast_credits":sum(x["credit_scope"]=="episode_guest_cast" for x in edges),
       "missing_guest_cast_collections":missing,
       "persons":dict(sorted(people.items())),
       "characters":dict(sorted(characters.items())),
       "credits":edges,
       "person_episode_guest_credit_index":{k:sorted(v) for k,v in sorted(per_person.items())},
       "character_episode_guest_credit_index":{k:sorted(v) for k,v in sorted(per_character.items())},
       "main_crew_source":crew["credits"],
       "qualifications":[
         "Main-series cast credit never implies appearance in a particular episode",
         "Guest credits are credited role links, not proof of an on-screen performance",
         "Actor and character identities are distinct entities",
         "Wikipedia production credit display strings are kept separate from TVmaze person IDs"
       ]
    }
    dump(ROOT/"catalog"/"cast-relationship-graph.json",graph)
    dump(ROOT/"catalog"/"guestcast-edges.jsonl","\n".join(json.dumps(e,sort_keys=True) for e in edges if e["credit_scope"]=="episode_guest_cast")+"\n")
    production={
       "source_file":"research/licensed-wiki/List-of-Night-Court-episodes.wikitext",
       "source_license":"CC BY-SA 4.0, Wikipedia contributors",
       "basis":"episode-part credit lines, NOT distinct writers normalized to persons",
       "directed_episodes":dict(direction.most_common()),
       "writer_credit_lines":dict(writing.most_common()),
       "director_and_writer_credit_pairings":[
          {"director":d,"writer_credit_line":w,"credited_episode_parts":n}
          for (d,w),n in sorted(pairings.items(),key=lambda x:(-x[1],x[0]))],
       "limitations":"A co-writer credit string is not a single person; scenes cannot be attributed to writers without more evidence."
    }
    dump(ROOT/"catalog"/"production-relationships.json",production)
    print("Built cast graph:",len(people),"distinct credited people,",len(characters),
          "distinct TVmaze characters,",graph["episode_guest_cast_credits"],"episode guest role credits")

if __name__=="__main__":main()
