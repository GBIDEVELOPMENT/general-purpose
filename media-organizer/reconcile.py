#!/usr/bin/env python3
"""Independent, read-only reconciliation of an exact approved FTP move manifest."""
import argparse
from collections import Counter
import json
from pathlib import Path

def compare(inventory,plan):
    if inventory.get("root")!="/downloads" or plan.get("root")!="/downloads":
        raise ValueError("Only matching /downloads inventories and plans are allowed")
    rows=inventory.get("files")
    moves=plan.get("moves")
    if not isinstance(rows,list) or not isinstance(moves,list):
        raise ValueError("Missing inventory files or approved moves")
    indexed={x["path"].casefold():x for x in rows}
    records=[]
    for op in moves:
        source=op["from"];dest=op["to"];expected=op["size"]
        a=indexed.get(source.casefold());b=indexed.get(dest.casefold())
        if a and b:state="both_present"
        elif b:state="moved" if b.get("size")==expected else "destination_size_mismatch"
        elif a:state="not_moved" if a.get("size")==expected else "source_size_mismatch"
        else:state="neither_found"
        records.append({"from":source,"to":dest,"expected_size":expected,"status":state})
    counts=dict(Counter(row["status"] for row in records))
    complete=not inventory.get("truncated") and not inventory.get("failures")
    return {"batch_id":plan.get("batch_id"),"scan_complete":bool(complete),
            "counts":counts,"total_moves":len(records),"records":records,
            "authoritative":bool(complete),
            "warning":None if complete else "Incomplete inventory: missing paths are not definitive"}
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--inventory",required=True)
    ap.add_argument("--manifest",required=True)
    ap.add_argument("--output",required=True)
    args=ap.parse_args()
    report=compare(json.loads(Path(args.inventory).read_text()),json.loads(Path(args.manifest).read_text()))
    dest=Path(args.output);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(report,indent=2,ensure_ascii=False))
    print("FTP_MANIFEST_RECONCILIATION",json.dumps({"batch":report["batch_id"],"complete":report["scan_complete"],"counts":report["counts"]}))
if __name__=="__main__":main()
