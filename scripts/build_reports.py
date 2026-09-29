#!/usr/bin/env python3
import csv, json
from collections import Counter, defaultdict
from pathlib import Path
from datetime import datetime

ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/"audit"
REPORTS=ROOT/"reports"
REPORTS.mkdir(exist_ok=True)

records=[]
for p in sorted(AUDIT.glob("*/*/*/*.json")) if AUDIT.exists() else []:
    try:
        d=json.loads(p.read_text())
        d["_path"]=str(p.relative_to(ROOT))
        records.append(d)
    except Exception as e:
        print(f"skip {p}: {e}")

fields=["scheduled_at","started_at","finished_at","project","trigger","decision","outcome","decision_reason","blocker","retry_scheduled","retry_after_minutes","next_step","run_id","_path"]
with (REPORTS/"automation-runs.csv").open("w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=fields)
    w.writeheader()
    for r in records:
        w.writerow({k:r.get(k) for k in fields})

by_project=defaultdict(Counter)
outcomes=Counter()
for r in records:
    outcomes[r.get("outcome","unknown")]+=1
    by_project[r.get("project","unknown")][r.get("outcome","unknown")]+=1

lines=["# Automation audit summary","",f"Total recorded activations: **{len(records)}**",""]
if records:
    lines += ["## Outcomes",""]
    for k,v in outcomes.most_common():
        lines.append(f"- {k}: {v}")
    lines += ["","## By project",""]
    for project in sorted(by_project):
        lines.append(f"### {project}")
        for k,v in by_project[project].most_common():
            lines.append(f"- {k}: {v}")
        lines.append("")
else:
    lines.append("No run records yet.")

(REPORTS/"automation-summary.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
