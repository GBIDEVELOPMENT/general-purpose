#!/usr/bin/env python3
"""Preserve immutable source-revision copies of licensed Wikipedia articles.

Safeguards:
- old revision is never overwritten or silently relabelled
- source revision id + SHA256 are checked each run
- untracked latest files and historical snapshots produce index records
- works offline on the repository's already-held licensed wikitext
- snapshots include original attribution/license metadata, not media
"""
from __future__ import annotations
from pathlib import Path
from hashlib import sha256
import json

ROOT=Path(__file__).resolve().parents[1]
WIKI=ROOT/"research"/"licensed-wiki"
HISTORY=WIKI/"revisions"
CATALOG=ROOT/"catalog"/"wiki-revision-archive.json"

def read(path):return path.read_bytes()
def hashdata(data):return sha256(data).hexdigest()
def dump(obj):return json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+"\n"

def store_immutable(path,data):
    if path.exists():
        if read(path)!=data:raise ValueError(f"Immutable revision collision: {path}")
        return False
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(data)
    return True

def source_pages():
    return sorted([*WIKI.glob("*.wikitext"),*(WIKI/"context").glob("*.wikitext")])

def main():
    HISTORY.mkdir(parents=True,exist_ok=True)
    new_files=0
    for file in source_pages():
        meta=file.with_suffix(".provenance.json")
        if not meta.exists():
            raise ValueError(f"Source lacks rights/revision provenance: {file}")
        provenance=json.loads(meta.read_text("utf-8"))
        revision=provenance.get("revision_id",provenance.get("revision"))
        if not isinstance(revision,int) or revision<1:
            raise ValueError(f"Missing numeric immutable Wikipedia revision: {meta}")
        license_value=provenance.get("license","")
        if "BY-SA" not in license_value and "Attribution-ShareAlike" not in license_value:
            raise ValueError(f"Unexpected rights basis: {meta}")
        body=read(file)
        digest=hashdata(body)
        prelisted=provenance.get("sha256")
        if prelisted and prelisted!=digest:
            raise ValueError(f"Stored wiki source hash mismatches provenance: {file}")
        stem=file.stem
        if file.parent.name=="context":stem="context-"+stem
        directory=HISTORY/stem
        snapshot=directory/(str(revision)+".wikitext")
        proof=directory/(str(revision)+".provenance.json")
        # Do not mutate the original provenance. Make a revision-specific,
        # attribution-preserving manifest with a checksum even if original omits it.
        archive={
            "source_file":str(file.relative_to(ROOT)),
            "original_provenance":str(meta.relative_to(ROOT)),
            "source_revision":revision,
            "sha256":digest,
            "content_bytes":len(body),
            "license":license_value,
            "source_attribution":provenance.get("attribution",provenance.get("author_attribution")),
            "source_permalink":provenance.get("permalink"),
            "media_excluded":True,
            "immutable_revision":True
        }
        new_files+=store_immutable(snapshot,body)
        new_files+=store_immutable(proof,dump(archive).encode("utf-8"))
    # The manifest is reconstructed from immutable stored records and does not
    # claim that historical revisions absent from the repository have been saved.
    items=[]
    for p in sorted(HISTORY.glob("*/*.provenance.json")):
        x=json.loads(p.read_text("utf-8"))
        textfile=p.with_suffix("").with_suffix(".wikitext")
        if not textfile.exists():raise ValueError(f"Missing immutable wiki text: {p}")
        if hashdata(read(textfile))!=x["sha256"]:
            raise ValueError(f"Tampered Wikipedia revision: {textfile}")
        items.append({"source":x["source_file"],
             "snapshot_path":str(textfile.relative_to(ROOT)),
             "provenance_path":str(p.relative_to(ROOT)),
             "revision":x["source_revision"],
             "sha256":x["sha256"],
             "license":x["license"],
             "source_permalink":x["source_permalink"]})
    index={
        "series":"night-court-1984",
        "type":"immutable_wikipedia_source_revision_archive",
        "snapshot_count":len(items),
        "policy":"Every held licensed source revision is retained at a stable SHA-verified path. Do not delete older revisions when latest updates.",
        "scope_limits":"Only revisions encountered and saved by this repository; not every historical Wikipedia revision.",
        "snapshots":items
    }
    text=dump(index)
    if not CATALOG.exists() or CATALOG.read_text("utf-8")!=text:
        CATALOG.write_text(text,"utf-8")
    print("Preserved",len(items),"immutable wiki revision snapshots;",
         new_files,"new archival snapshot/provenance files")

if __name__=="__main__":main()
