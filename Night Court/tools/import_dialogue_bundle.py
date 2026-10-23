#!/usr/bin/env python3
"""Import a bounded user-supplied ZIP of Night Court 1984 subtitle/transcript files.

No fetching, no archive-wide arbitrary extraction, no executable members.
Each SxxEyy source is preserved by the existing immutable episode importer.

Example:
  python "Night Court/tools/import_dialogue_bundle.py" \
    --bundle "Night Court/incoming/dvd-english.zip" \
    --metadata "Night Court/incoming/dvd-english.zip.meta.json"

Sidecar:
  {"edition":"personal DVD captions","language":"en",
   "rights_basis":"lawfully_obtained_research_copy","confirmed":true,
   "complete":false,"source_name":"Personal original series subtitles"}
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
from tempfile import TemporaryDirectory
import zipfile

import import_dialogue as D

MAX_ZIP_BYTES=90_000_000
MAX_TOTAL_UNCOMPRESSED=180_000_000
MAX_MEMBERS=500
MAX_COMPRESSION_RATIO=300
ALLOWED_OVERRIDES={"edition","language","complete","notes"}

def inspect(path:Path):
    if not path.is_file() or path.stat().st_size>MAX_ZIP_BYTES:
        raise ValueError("ZIP missing or larger than 90 MB")
    candidates=[];total=0
    with zipfile.ZipFile(path) as z:
        infos=z.infolist()
        if len(infos)>MAX_MEMBERS+100:
            raise ValueError("Archive contains too many entries")
        for info in infos:
            normalized=info.filename.replace("\\","/")
            parts=PurePosixPath(normalized)
            if (parts.is_absolute() or not normalized or any(p in (".","..") for p in parts.parts)
                or not parts.parts or ":" in parts.parts[0] or normalized.startswith("//")):
                raise ValueError("Unsafe archive member path "+repr(info.filename))
            mode=(info.external_attr>>16)
            if stat.S_ISLNK(mode):
                raise ValueError("Archive contains symlink "+repr(info.filename))
            if info.is_dir():continue
            if info.file_size<0 or info.file_size>D.MAX_FILE_BYTES:
                raise ValueError("Oversized source member "+repr(info.filename))
            total+=info.file_size
            if total>MAX_TOTAL_UNCOMPRESSED:
                raise ValueError("Archive uncompressed size limit exceeded")
            if info.file_size and info.file_size/max(1,info.compress_size)>MAX_COMPRESSION_RATIO:
                raise ValueError("Suspicious compressed member "+repr(info.filename))
            if parts.suffix.lower() not in D.FILE_TYPES:
                continue
            # Episode identity is from member name, NOT from the name of the ZIP.
            key=D.episode_id(normalized)
            candidates.append((info,key))
        if not candidates:
            raise ValueError("ZIP contains no SxxEyy identified SRT, VTT or TXT files")
        if len(candidates)>MAX_MEMBERS:
            raise ValueError("Too many transcript/caption files for one import")
    return candidates

def bundle_options(meta,episode,source,archive_hash,info):
    overrides=meta.get("overrides",{})
    if not isinstance(overrides,dict):raise ValueError("overrides must be an object")
    variant=overrides.get(info.filename,{})
    if not isinstance(variant,dict) or set(variant)-ALLOWED_OVERRIDES:
        raise ValueError("Unknown or invalid per-member metadata override")
    edition=variant.get("edition",meta.get("edition"))
    notes=variant.get("notes",meta.get("notes") or "")
    return {
      "episode":episode,"edition":edition,
      "language":variant.get("language",meta.get("language","en")),
      "rights_basis":meta.get("rights_basis"),
      "confirmed":meta.get("confirmed") is True,
      "complete":variant.get("complete",meta.get("complete",False)) is True,
      "source_name":f"{source.name}::{info.filename}",
      "source_url":meta.get("source_url"),
      "notes":f"{meta.get('source_name', 'Bundled user-provided subtitles')}; {notes} [ZIP SHA-256 {archive_hash}; source member CRC32 {info.CRC:08x}]"
    }

def import_bundle(path:Path,meta:dict,dry_run=False):
    if not isinstance(meta,dict):raise ValueError("Metadata is not an object")
    if not dry_run and (meta.get("confirmed") is not True
                        or meta.get("rights_basis") not in D.RIGHTS):
        raise ValueError("Explicit confirmed rights/source declaration required")
    candidates=inspect(path)
    content_hash=hashlib.sha256(path.read_bytes()).hexdigest()
    summary={"archive":path.name,"archive_sha256":content_hash,
             "eligible_members":len(candidates),
             "episodes":sorted({ep for _,ep in candidates}),
             "dry_run":dry_run}
    if dry_run:
        print(json.dumps(summary,indent=2))
        return summary
    with TemporaryDirectory(prefix="night-court-dialogue-bundle-") as temp:
        with zipfile.ZipFile(path) as z:
            for i,(info,ep) in enumerate(candidates):
                suffix=PurePosixPath(info.filename.replace("\\","/")).suffix.lower()
                target=Path(temp)/f"{i:04d}-{ep}{suffix}"
                # Individual bounded read, no extractall and no symlink following.
                raw=z.read(info)
                if len(raw)>D.MAX_FILE_BYTES:
                    raise ValueError("Decompression size mismatch")
                target.write_bytes(raw)
                D.import_one(target,bundle_options(meta,ep,path,content_hash,info))
    D.rebuild_index()
    print(f"Imported {len(candidates)} separately preserved caption/transcript sources from {path.name}")
    return summary

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    mode=ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--bundle",type=Path,help="local ZIP package")
    mode.add_argument("--inbox",type=Path,help="scan a research branch incoming folder for ZIP packages")
    ap.add_argument("--metadata",type=Path,help="JSON sidecar for a single ZIP")
    ap.add_argument("--dry-run",action="store_true")
    args=ap.parse_args()
    if args.inbox:
        if not args.inbox.exists():
            print("No ZIP inbox:",args.inbox)
            D.rebuild_index()
            return
        bundles=sorted(args.inbox.rglob("*.zip"))
        if len(bundles)>12:ap.error("At most 12 source ZIPs per inbox import")
    else:
        bundles=[args.bundle]
    for zip_path in bundles:
        sidecar=args.metadata if args.metadata and not args.inbox else Path(str(zip_path)+".meta.json")
        if not sidecar.exists():
            if args.dry_run:
                print("Preview ZIP with missing sidecar:",zip_path.name)
                import_bundle(zip_path,{},dry_run=True)
                continue
            raise ValueError(f"Metadata sidecar missing: {sidecar}")
        meta=json.loads(sidecar.read_text("utf-8"))
        import_bundle(zip_path,meta,dry_run=args.dry_run)
    D.rebuild_index()

if __name__=="__main__":
    main()
