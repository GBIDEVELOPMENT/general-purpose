#!/usr/bin/env python3
"""One-shot, exact-path, owner-authorized FTP media deletion. No recursive deletion."""
import argparse
import ftplib
import json
import os
from pathlib import Path, PurePosixPath
from organize import connect, safe

MANIFEST = Path("media-organizer/review/ftp-selected-title-delete-2026-11-01.json")
OUT = Path("media-organizer/delete-selected-output/completed.json")
EXPECTED_BYTES = 463387620682
EXPECTED_COUNT = 289
EXPECTED_TITLES = 19

def load():
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if m.get("schema_version") != "review-only-2026-11-01-v1" or m.get("snapshot", {}).get("inventory_blob_sha") != "079f857e4c717c2801b76c2132e5b8a996b62fe0":
        raise ValueError("Wrong inventory or manifest version")
    t = m["totals"]
    if (t["files"], t["titles"], t["bytes"]) != (EXPECTED_COUNT, EXPECTED_TITLES, EXPECTED_BYTES): raise ValueError("Manifest totals changed")
    rows = [f for group in m["groups"] for f in group["files"]]
    if len(rows) != EXPECTED_COUNT or sum(f["size_bytes"] for f in rows) != EXPECTED_BYTES: raise ValueError("Manifest count/bytes mismatch")
    seen = set()
    for f in rows:
        if set(f) != {"path", "size_bytes", "modify_ftp"}: raise ValueError("Unexpected fields")
        p = safe(f["path"])
        if p in seen or p in ("/downloads/rtorrent", "/downloads/watch/rtorrent") or "/rtorrent/" in p or "/watch/rtorrent/" in p: raise ValueError("Unsafe or duplicate path")
        if not isinstance(f["size_bytes"], int) or isinstance(f["size_bytes"], bool) or f["size_bytes"] < 0: raise ValueError("Invalid size")
        mod = f["modify_ftp"]
        if mod is not None and (not isinstance(mod,str) or len(mod)!=14 or not mod.isdigit()): raise ValueError("Invalid MLSD modify")
        if not any(p.startswith(root + "/") for group in m["groups"] for root in group["matched_roots"]): raise ValueError("Outside approved roots")
        seen.add(p)
    return rows

def lookup(ftp, path):
    pp = PurePosixPath(path)
    try:
        ftp.cwd(str(pp.parent))
        entries = [(name, facts) for name, facts in ftp.mlsd() if name == pp.name]
    except ftplib.error_perm as error:
        if str(error).startswith("550"): return None
        raise
    if len(entries) > 1: raise ValueError("Ambiguous MLSD match " + path)
    return entries[0][1] if entries else None

def matches(facts, row):
    return (facts.get("type") == "file" and facts.get("size") == str(row["size_bytes"])
            and (row["modify_ftp"] is None or facts.get("modify") == row["modify_ftp"]))

def save(j):
    OUT.parent.mkdir(parents=True, exist_ok=True)
    temp = OUT.with_suffix(".tmp")
    with temp.open("w", encoding="utf-8") as fd:
        json.dump(j, fd, indent=2, ensure_ascii=False)
        fd.flush()
        os.fsync(fd.fileno())
    os.replace(temp, OUT)

def run(rows, apply=False):
    j = {"status":"preflight","expected_files":len(rows),"expected_bytes":EXPECTED_BYTES,"deleted":[],"absent":[],"blocked":[]}
    save(j)
    with connect() as ftp:
        eligible = []
        for row in rows:
            facts = lookup(ftp,row["path"])
            if facts is None:
                j["absent"].append(row["path"])
            elif not matches(facts,row):
                j["blocked"].append({"path":row["path"],"reason":"size/type/modify mismatch"})
            else: eligible.append(row)
        j["preflight_eligible"] = len(eligible)
        j["status"] = "preflight_failed" if j["blocked"] else "preflight_passed"
        save(j)
        if j["blocked"]: raise RuntimeError("Preflight refused changed or ambiguous files")
        if not apply: return j
        j["status"] = "deleting"
        save(j)
        try:
            for row in eligible:
                facts = lookup(ftp,row["path"])
                if facts is None:
                    j["absent"].append(row["path"])
                elif not matches(facts,row):
                    j["blocked"].append({"path":row["path"],"reason":"changed during execution"})
                    raise RuntimeError("Live changed-file guard blocked deletion")
                else:
                    ftp.delete(row["path"])
                    j["deleted"].append({"path":row["path"],"size_bytes":row["size_bytes"]})
                save(j)
        finally:
            j["status"] = "complete" if not j["blocked"] and len(j["deleted"])+len(j["absent"])==len(rows) else "partial"
            j["deleted_bytes"] = sum(x["size_bytes"] for x in j["deleted"])
            save(j)
    return j

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--apply",action="store_true")
    args=p.parse_args()
    rows=load()
    if not args.apply:
        print(json.dumps({"validated":len(rows),"bytes":EXPECTED_BYTES,"mode":"offline-only"}),flush=True)
        return
    result=run(rows,apply=True)
    print(json.dumps({"status":result["status"],"deleted":len(result["deleted"]),"absent":len(result["absent"]),"blocked":len(result["blocked"]),"deleted_bytes":result["deleted_bytes"]}),flush=True)
if __name__=="__main__":main()
