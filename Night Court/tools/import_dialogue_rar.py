#!/usr/bin/env python3
"""Owner-provided Night Court S01/S02 RAR ingestion; no network retrieval.

Extract only validated SRT members. Preserve byte-exact RAR originals and
per-episode SRT witnesses, and record checksums, origin and edition. Uses
Python rarfile plus a locally installed unar or unrar extraction executable.
"""
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
import argparse
import hashlib
import json
import zlib

import import_dialogue as D
import rarfile

ROOT=D.ROOT
SOURCE_DIR=ROOT/"research"/"source-archives"
REPORT=ROOT/"catalog"/"rar-ingestion-manifest.json"
SPECS=[
 {"name":"night-court-first-season_english-365733.rar","season":1,"count":13,
  "sha256":"e02c7c529662ff1e8354dcdc42393879c2535df10aecf7b5b5e7ce8f0e0bdc65",
  "edition":"S01 iNTERNAL DVDRip XviD SPRiNTER English"},
 {"name":"night-court-second-season_english-365736.rar","season":2,"count":22,
  "sha256":"fecd355b278d4b6ce4a7c461f441403b73da82889833edaca98b93b7a19588d1",
  "edition":"S02 DVDRip XviD OSiTV English"}
]
MAX_UNPACKED=20_000_000

def validate_members(info,spec):
    if len(info)!=spec["count"]:raise ValueError("Unexpected archive member count")
    assigned={};total=0
    for member in info:
        name=member.filename.replace("\\","/")
        parts=PurePosixPath(name)
        if (not name or parts.is_absolute() or len(parts.parts)!=1
            or any(p in (".","..") for p in parts.parts) or ":" in name
            or parts.suffix.lower()!=".srt" or member.isdir()
            or member.is_symlink() or getattr(member,"file_redir",None)):
            raise ValueError("Unexpected RAR member path/type: "+repr(name))
        if member.file_size<=0 or member.file_size>1_000_000:
            raise ValueError("RAR member too large/empty: "+repr(name))
        total+=member.file_size
        if total>MAX_UNPACKED or member.compress_size<=0 or member.file_size/member.compress_size>350:
            raise ValueError("RAR size/compression bounds exceeded")
        ep=D.episode_id(parts.name)
        if int(ep[1:3])!=spec["season"] or ep in assigned:
            raise ValueError("Cross-season or duplicate episode mapping: "+name)
        assigned[ep]=member
    expected={f"S{spec['season']:02d}E{n:02d}" for n in range(1,spec["count"]+1)}
    if set(assigned)!=expected:
        raise ValueError("Missing/extra episode IDs: "+repr(sorted(expected-set(assigned))))
    return assigned

def file_sha(path):
    if not path.is_file() or path.stat().st_size>2_000_000:
        raise ValueError("Missing/oversized RAR: "+str(path))
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run_one(spec,dry_run=False):
    raw=ROOT/spec["name"];archived=SOURCE_DIR/spec["name"]
    if raw.exists() and archived.exists():raise ValueError("Ambiguous duplicate archive")
    path=archived if archived.exists() else raw
    if file_sha(path)!=spec["sha256"]:raise ValueError("RAR archive checksum mismatched: "+spec["name"])
    rows=[]
    with rarfile.RarFile(path) as rar:
        files=validate_members(rar.infolist(),spec)
        if not dry_run:
            with TemporaryDirectory(prefix="nc-rar-") as tmp:
                for ep,member in sorted(files.items()):
                    with rar.open(member) as fh:
                        data=fh.read(1_000_001)
                    if len(data)!=member.file_size or (zlib.crc32(data)&0xffffffff)!=member.CRC:
                        raise ValueError("RAR member CRC/size mismatch: "+member.filename)
                    target=Path(tmp)/f"{ep}.srt"
                    target.write_bytes(data)
                    meta={
                        "episode":ep,"edition":spec["edition"],"language":"en",
                        "rights_basis":"user_provided","confirmed":True,
                        "complete":False,
                        "source_name":f"{archived.relative_to(ROOT)}::{member.filename}",
                        "notes":(
                            f"Repository owner supplied {spec['name']} for original series research. "
                            f"RAR SHA256 {spec['sha256']}, member CRC32 {member.CRC:08x}. "
                            "Label indicates DVD rip but edition authenticity and episode completeness unverified."
                        )
                    }
                    D.import_one(target,meta)
                    rows.append({
                        "episode_id":ep,"original_member_filename":member.filename,
                        "source_size_bytes":len(data),
                        "source_sha256":hashlib.sha256(data).hexdigest(),
                        "rar_member_crc32":f"{member.CRC:08x}",
                        "declared_complete":False})
        else:
            rows=[{"episode_id":ep,"original_member_filename":mem.filename,
                   "source_size_bytes":mem.file_size} for ep,mem in sorted(files.items())]
    if not dry_run and path==raw:
        archived.parent.mkdir(parents=True,exist_ok=True)
        raw.rename(archived)
    print(spec["name"],"validated",len(rows),"separately numbered English SRTs.")
    return {"archive_file":str(archived.relative_to(ROOT)),
            "archive_sha256":spec["sha256"],
            "season":spec["season"],"edition":spec["edition"],
            "members":rows,"member_count":len(rows)}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dry-run",action="store_true")
    args=p.parse_args()
    results=[run_one(spec,args.dry_run) for spec in SPECS]
    if args.dry_run:return
    D.rebuild_index()
    ids=[m["episode_id"] for r in results for m in r["members"]]
    if len(ids)!=35 or len(set(ids))!=35:
        raise ValueError("Expected exactly 35 original-series episode witnesses")
    report={"series_id":"night-court-1984",
            "source":"owner_uploaded_source_archives",
            "source_reuse_note":"User supplied these archives for private research. Importer does not make legal determinations.",
            "archive_count":2,
            "witness_count":35,
            "episodes_with_new_source":35,
            "all_source_complete_status":"unverified_against_audiovisual_editions",
            "archives":results}
    contents=json.dumps(report,indent=2,ensure_ascii=False,sort_keys=True)+"\n"
    if not REPORT.exists() or REPORT.read_text("utf-8")!=contents:
        REPORT.parent.mkdir(parents=True,exist_ok=True)
        REPORT.write_text(contents,"utf-8")
    print("COMPLETE: catalogued 35 original SRT witnesses, with two RAR originals retained.")

if __name__=="__main__":
    main()
