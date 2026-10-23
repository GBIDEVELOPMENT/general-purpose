#!/usr/bin/env python3
"""Import user-provided or authorized Night Court dialogue into the private corpus.

No network calls, web scraping, DRM bypass or automated acquisition. The bytes
provided to this tool are retained losslessly. Supports .srt, .vtt and .txt.
Versions coexist and keep source, rights declaration, edition and SHA-256.

Local:
  python "Night Court/tools/import_dialogue.py" --file ~/Downloads/Night.Court.S01E01.srt --episode S01E01 --edition dvd-en --rights-basis lawfully_obtained_research_copy --confirm-rights --complete

Inbox:
  Put S01E01.dvd.en.srt + S01E01.dvd.en.srt.meta.json in Night Court/incoming/
  python "Night Court/tools/import_dialogue.py" --inbox

Completeness always denotes the *submitter's assertion*, not independent QA.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
from urllib.parse import urlparse

ROOT = Path(os.environ.get("NIGHT_COURT_ROOT", str(Path(__file__).resolve().parents[1])))
SEASON_COUNTS = [13,22,22,22,22,22,24,24,22]
FILE_TYPES = {".srt":"srt",".vtt":"vtt",".txt":"txt"}
RIGHTS = {"user_provided","lawfully_obtained_research_copy",
          "licensed_copy","rights_holder_authorized","public_domain"}
EP_ID = re.compile(r"(?:^|[^A-Za-z0-9])S(\d{1,2})[\s._-]*E(\d{1,2})(?:[^0-9]|$)", re.I)
CLOCK = re.compile(r"(?:(\d{1,2}):)?(\d{1,2}):(\d{2})[,.](\d{3})")
MAX_FILE_BYTES = 20_000_000
MAX_CUES = 15_000

def serialise(obj):
    return json.dumps(obj,indent=2,ensure_ascii=False,sort_keys=True)+"\n"

def write_once(path:Path,content:bytes):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        if path.read_bytes()!=content:
            raise ValueError("Immutable artifact collision: "+str(path))
        return False
    path.write_bytes(content)
    return True

def write_if_changed(path:Path,value:str):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists() and path.read_text("utf-8")==value:
        return False
    path.write_text(value,"utf-8")
    return True

def episode_id(value):
    m=EP_ID.search(" "+str(value)+" ")
    if not m: raise ValueError("Missing SxxEyy episode identifier: "+str(value))
    s,n=int(m.group(1)),int(m.group(2))
    if not 1<=s<=9 or not 1<=n<=SEASON_COUNTS[s-1]:
        raise ValueError("Out-of-range original-series episode "+str(value))
    return f"S{s:02d}E{n:02d}"

def ms(clock):
    m=CLOCK.fullmatch(clock.strip())
    if not m:raise ValueError("Unrecognized timestamp "+repr(clock))
    hour=int(m.group(1) or 0)
    minute=int(m.group(2))
    second=int(m.group(3))
    millis=int(m.group(4))
    if minute>59 or second>59:raise ValueError("Bad clock "+clock)
    return ((hour*60+minute)*60+second)*1000+millis

def to_text(raw):
    """Decode captions without mistaking legacy 8-bit text for UTF-16.

    Python's UTF-16 codec accepts many even-length byte sequences without a
    BOM, turning Windows-1252 SRTs into plausible but nonsensical glyphs.
    Prefer UTF-8, accept UTF-16 when signalled by a BOM or NUL-byte pattern,
    then decode legacy Windows-1252. Preserve the original source bytes.
    """
    if raw.startswith((b"\xff\xfe",b"\xfe\xff")):
        # A real UTF-16 BOM takes priority over the NUL heuristic.
        try:
            return raw.decode("utf-16"),"utf-16"
        except UnicodeError as exc:
            raise ValueError("Invalid BOM-marked UTF-16 caption source") from exc
    try:
        text=raw.decode("utf-8-sig")
        if "\x00" not in text:
            return text,"utf-8-sig"
    except UnicodeError:
        pass
    # BOM-less UTF-16 SRTs tend to have NULs in every second byte.
    if len(raw)>=16 and raw.count(b"\x00")/len(raw)>=0.15:
        even=sum(raw[i]==0 for i in range(0,min(len(raw),4096),2))
        odd=sum(raw[i]==0 for i in range(1,min(len(raw),4096),2))
        codec="utf-16-le" if odd>even*3 else "utf-16-be" if even>odd*3 else None
        if codec:
            try:
                text=raw.decode(codec)
                if "\x00" not in text:
                    return text,codec
            except UnicodeError:
                pass
    for codec in ("cp1252","iso-8859-1"):
        try:
            text=raw.decode(codec)
            if "\x00" not in text:
                return text,codec
        except UnicodeError:
            continue
    raise ValueError("Unknown caption encoding; expected UTF-8, UTF-16, or legacy 8-bit text")

def parse_timed(text,typ):
    if typ=="vtt":
        if not text.lstrip("\ufeff \r\n").startswith("WEBVTT"):
            raise ValueError("VTT input lacks WEBVTT header")
    text=text.replace("\r\n","\n").replace("\r","\n").lstrip("\ufeff")
    blocks=re.split(r"\n\s*\n",text)
    entries=[]
    for block in blocks:
        lines=block.splitlines()
        if not lines:continue
        first=lines[0].strip()
        if typ=="vtt" and (first=="WEBVTT" or first.startswith(("NOTE","STYLE","REGION"))):
            continue
        pos=next((i for i,line in enumerate(lines[:3]) if "-->" in line),None)
        if pos is None:
            if typ=="srt":
                raise ValueError("SRT contains a non-caption block: "+repr(first[:70]))
            continue
        start_time,rest=lines[pos].split("-->",1)
        end_time=rest.strip().split()[0]
        beginning,ending=ms(start_time),ms(end_time)
        if ending<beginning:raise ValueError("Cue end precedes start")
        payload="\n".join(lines[pos+1:]).strip()
        if not payload:continue
        entries.append({"cue":len(entries)+1,"start_ms":beginning,
                        "end_ms":ending,"text":payload,"kind":"source_caption"})
    if not entries:raise ValueError("No timed subtitle cues found")
    if len(entries)>MAX_CUES:raise ValueError("Excessive cue count")
    return entries

def parse_plain(text):
    text=text.replace("\r\n","\n").replace("\r","\n").strip()
    blocks=[b.strip() for b in re.split(r"\n\s*\n",text) if b.strip()]
    if not blocks:raise ValueError("Empty source text")
    if len(blocks)>MAX_CUES:raise ValueError("Excessive text paragraph count")
    return [{"cue":i+1,"start_ms":None,"end_ms":None,
             "text":b,"kind":"source_transcript_text"}
            for i,b in enumerate(blocks)]

def prepare(file:Path,opts:dict):
    if file.suffix.lower() not in FILE_TYPES:
        raise ValueError("Unsupported format: "+file.suffix)
    if not file.is_file() or file.stat().st_size>MAX_FILE_BYTES:
        raise ValueError("File absent or exceeds 20 MB")
    rights=opts.get("rights_basis")
    if rights not in RIGHTS:
        raise ValueError("Declare rights_basis: "+", ".join(sorted(RIGHTS)))
    if opts.get("confirmed") is not True:
        raise ValueError("Explicit rights/source confirmation required")
    key=episode_id(opts.get("episode") or file.name)
    edir=ROOT/"seasons"/key[:3]/key
    ep_path=edir/"episode.json"
    if not ep_path.exists():
        raise ValueError("Episode does not exist in original corpus: "+key)
    edition=(opts.get("edition") or "").strip()
    if not edition or len(edition)>120:
        raise ValueError("Specify a short release/edition/variant label")
    slug=re.sub(r"[^a-z0-9]+","-",edition.lower()).strip("-")[:48]
    if not slug:raise ValueError("Invalid edition")
    language=(opts.get("language") or "en").strip()
    if not re.fullmatch(r"[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8}){0,3}",language):
        raise ValueError("Invalid language code")
    source_url=opts.get("source_url")
    if source_url and urlparse(source_url).scheme not in ("http","https"):
        raise ValueError("Invalid source URL")
    raw=file.read_bytes()
    checksum=hashlib.sha256(raw).hexdigest()
    text,codec=to_text(raw)
    kind=FILE_TYPES[file.suffix.lower()]
    cues=parse_plain(text) if kind=="txt" else parse_timed(text,kind)
    stem=f"{slug}--{checksum[:16]}"
    folder=edir/"dialogue"/"versions"/stem
    original=folder/("original"+file.suffix.lower())
    segments=folder/"segments.jsonl"
    plain=folder/"readable.txt"
    manifest=folder/"manifest.json"
    metadata={
       "schema":"night-court-dialogue-witness/1",
       "series":"night-court-1984","episode_id":key,
       "edition":edition,"language":language,"format":kind,
       "rights_basis_declared":rights,
       "rights_attestation":"Source was supplied/identified by the user for private research; legal determination not made by importer.",
       "source_name":str(opts.get("source_name") or file.name),
       "source_url":source_url,
       "source_notes":opts.get("notes") or None,
       "declared_complete":opts.get("complete") is True,
       "completeness_status":"submitter_declared_complete_unverified" if opts.get("complete") else "unknown_unverified",
       "version_id":stem,
       "sha256":checksum,
       "encoding":codec,
       "original_path":str(original.relative_to(edir)),
       "segments_path":str(segments.relative_to(edir)),
       "readable_path":str(plain.relative_to(edir)),
       "cue_count":len(cues),
       "timecoded":kind!="txt",
       "first_start_ms":cues[0]["start_ms"],
       "last_end_ms":cues[-1]["end_ms"],
       "tokens_approx":sum(len(re.findall(r"\b[\w']+\b",c["text"])) for c in cues),
       "epistemic_limit":"Dialogue, caption quality and episode completeness have not been authenticated against video."
    }
    return key,edir,ep_path,original,segments,plain,manifest,raw,cues,metadata

def import_one(file:Path,opts:dict):
    (key,edir,ep_path,original,segments,plain,manifest,raw,cues,metadata)=prepare(file,opts)
    # Write immutable original and canonical representations before attaching to episode.
    write_once(original,raw)
    write_once(segments,("\n".join(json.dumps(c,ensure_ascii=False,sort_keys=True)
                               for c in cues)+"\n").encode("utf-8"))
    readtext="\n".join(c["text"].replace("\n"," ") for c in cues)+"\n"
    write_once(plain,readtext.encode("utf-8"))
    write_once(manifest,serialise(metadata).encode("utf-8"))
    episode=json.loads(ep_path.read_text("utf-8"))
    holding_type="caption_files" if metadata["timecoded"] else "full_transcripts"
    holding={
      "version_id":metadata["version_id"],
      "file":metadata["original_path"],
      "manifest_file":str(manifest.relative_to(edir)),
      "sha256":metadata["sha256"],
      "source":"user_imported",
      "rights_basis_declared":metadata["rights_basis_declared"],
      "completeness_status":metadata["completeness_status"]}
    if holding_type=="full_transcripts" and not metadata["declared_complete"]:
        # Plain text can be an excerpt, not an entire episode's transcript.
        holding_type="other"
    if not any(x.get("version_id")==holding["version_id"]
               for x in episode["holdings"][holding_type]):
        episode["holdings"][holding_type].append(holding)
        write_if_changed(ep_path,serialise(episode))
    print(f"Imported {key}, edition {metadata['edition']!r}: {len(cues)} source segments, sha256 {metadata['sha256'][:16]}")
    return key

def rebuild_index():
    rows=[]
    for f in sorted((ROOT/"seasons").glob("S*/S*/dialogue/versions/*/manifest.json")):
        meta=json.loads(f.read_text("utf-8"))
        epdir=f.parents[3]
        original=epdir/meta["original_path"]
        if not original.exists() or hashlib.sha256(original.read_bytes()).hexdigest()!=meta["sha256"]:
            raise ValueError("Dialogue content checksum mismatch: "+str(f))
        rows.append({"episode_id":meta["episode_id"],"version_id":meta["version_id"],
            "format":meta["format"],"edition":meta["edition"],"language":meta["language"],
            "cue_count":meta["cue_count"],"declared_complete":meta["declared_complete"],
            "sha256":meta["sha256"],
            "rights_basis_declared":meta["rights_basis_declared"],
            "manifest":str(f.relative_to(ROOT))})
    write_if_changed(ROOT/"catalog"/"dialogue-index.jsonl",
                     "\n".join(json.dumps(x,ensure_ascii=False,sort_keys=True) for x in rows)+("\n" if rows else ""))
    print("Indexed",len(rows),"held dialogue witnesses across",len({r["episode_id"] for r in rows}),"episodes")
    return rows

def inbox(dirpath:Path):
    if not dirpath.exists():
        print("No inbox at",dirpath)
        rebuild_index()
        return
    candidates=sorted(p for p in dirpath.rglob("*") if p.is_file() and p.suffix.lower() in FILE_TYPES)
    imported=0
    for file in candidates:
        sidecar=Path(str(file)+".meta.json")
        if not sidecar.exists():
            print("SKIP (missing .meta.json):",file.name)
            continue
        opts=json.loads(sidecar.read_text("utf-8"))
        try:
            import_one(file,opts)
            imported+=1
        except (ValueError,OSError,KeyError) as exc:
            print("ERROR:",file.name,exc,file=sys.stderr)
            raise
    print("Inbox imported",imported,"tracks")
    rebuild_index()

def main():
    p=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--file",type=Path)
    mode.add_argument("--inbox",type=Path,nargs="?",const=ROOT/"incoming")
    p.add_argument("--episode",help="SxxEyy, inferred from filename when omitted")
    p.add_argument("--edition",help="e.g. dvd-480p-english or personal-transcription-v1")
    p.add_argument("--language",default="en")
    p.add_argument("--source-name")
    p.add_argument("--source-url")
    p.add_argument("--notes")
    p.add_argument("--rights-basis",choices=sorted(RIGHTS))
    p.add_argument("--confirm-rights",action="store_true",
                   help="Confirm provenance and authority to supply the material")
    p.add_argument("--complete",action="store_true",
                   help="Mark as submitter-claimed complete; NOT independent QA")
    args=p.parse_args()
    if args.inbox is not None:
        inbox(args.inbox)
    else:
        opts={"episode":args.episode,"edition":args.edition,"language":args.language,
              "source_name":args.source_name,"source_url":args.source_url,"notes":args.notes,
              "rights_basis":args.rights_basis,"confirmed":args.confirm_rights,"complete":args.complete}
        import_one(args.file,opts)
        rebuild_index()

if __name__=="__main__":
    main()
