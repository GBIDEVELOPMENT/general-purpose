#!/usr/bin/env python3
"""Read-only bounded ffprobe against exact FTP Trek media files, no media downloads saved."""
from __future__ import annotations
import argparse,ftplib,json,os,re,subprocess,tempfile
from pathlib import Path,PurePosixPath
from urllib.parse import quote
from organize import ROOT,connect,safe

def validate(m):
    if set(m)!={"root","targets","description"} or m["root"]!=ROOT:raise ValueError("Invalid probe manifest")
    if not isinstance(m["description"],str) or len(m["description"])<20:raise ValueError("Explain purpose")
    if not isinstance(m["targets"],list) or not 1<=len(m["targets"])<=12:raise ValueError("Probe max 12 bounded targets")
    seen=set()
    for x in m["targets"]:
        if set(x)!={"from","size","modify"}:raise ValueError("Incorrect target fields")
        p=PurePosixPath(safe(x["from"]))
        if p.suffix.lower() not in (".mkv",".mp4",".avi"):raise ValueError("Video only")
        if not re.search(r"(?i)star[ ._\\-]+trek",str(p)):raise ValueError("Trek only")
        if not isinstance(x["size"],int) or x["size"]<100000:raise ValueError("Invalid size")
        if not isinstance(x["modify"],str) or not re.fullmatch(r"\d{14}",x["modify"]):raise ValueError("Missing precise mtime")
        if str(p).casefold() in seen:raise ValueError("Duplicate probe target")
        seen.add(str(p).casefold())
    return m["targets"]

def assert_unchanged(ftp,x):
    p=PurePosixPath(x["from"]);ftp.cwd(str(p.parent))
    matches=[facts for name,facts in ftp.mlsd() if name==p.name]
    if len(matches)!=1 or matches[0].get("type")!="file":raise ValueError("Missing or ambiguous source")
    if str(matches[0].get("size"))!=str(x["size"]) or matches[0].get("modify")!=x["modify"]:
        raise ValueError("Changed metadata")

class HeaderLimitReached(Exception):pass
MAX_HEADER_BYTES=8*1024*1024

def read_header(x,filename):
    received=0
    ftp=connect()
    try:
        assert_unchanged(ftp,x)
        with open(filename,"wb") as out:
            def block(data):
                nonlocal received
                needed=MAX_HEADER_BYTES-received
                if needed<=0:raise HeaderLimitReached()
                out.write(data[:needed])
                received+=min(len(data),needed)
                if received>=MAX_HEADER_BYTES:raise HeaderLimitReached()
            try:ftp.retrbinary("RETR "+x["from"],block,blocksize=65536)
            except HeaderLimitReached:pass
    finally:
        # Close rather than QUIT: this transfer may have been intentionally cut short.
        ftp.close()
    return received

class PrefixComplete(Exception):
    """Stop FTP RETR after a hard byte limit; caller closes data connection."""

def read_prefix(x, limit=8*1024*1024):
    """Read a bounded prefix directly via authenticated FTP, never the whole video."""
    import tempfile
    from pathlib import Path
    received=0
    with tempfile.TemporaryDirectory(prefix="trek-stream-") as folder:
        local=Path(folder)/("video"+PurePosixPath(x["from"]).suffix)
        ftp=connect()
        try:
            with local.open("wb") as destination:
                def chunk(data):
                    nonlocal received
                    left=limit-received
                    if left>0:
                        destination.write(data[:left])
                        received+=min(len(data),left)
                    if received>=limit:raise PrefixComplete()
                try:
                    ftp.retrbinary("RETR "+x["from"],chunk,blocksize=65536)
                except PrefixComplete:
                    pass
        finally:
            ftp.close()
        result=subprocess.run(["ffprobe","-hide_banner","-loglevel","error",
            "-probesize","4000000","-analyzeduration","1500000",
            "-select_streams","v:0","-show_entries",
            "stream=codec_name,profile,pix_fmt,width,height,color_range,color_space,color_transfer,color_primaries,side_data_list",
            "-of","json",str(local)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,
            timeout=35,check=False)
        try:
            streams=json.loads(result.stdout.decode("utf-8",errors="replace")).get("streams",[])
        except ValueError:
            streams=[]
        if not streams:
            return {"status":"prefix_no_video_metadata","bytes_examined":received,
                    "exit_code":result.returncode}
        stream=streams[0]
        return {"status":"prefix_probed","bytes_examined":received,"stream":{
            k:stream[k] for k in ("codec_name","profile","pix_fmt","width","height",
              "color_range","color_space","color_transfer","color_primaries","side_data_list")
            if k in stream}}

def inspect(x):
    try:
        return read_prefix(x)
    except subprocess.TimeoutExpired:
        return {"status":"timeout"}
    except (OSError,ftplib.all_errors,ValueError) as error:
        return {"status":"probe_failed","error_class":type(error).__name__}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--manifest",default="media-organizer/trek-probe-targets.json")
    parser.add_argument("--output",default="media-organizer/probe-output/observations.json")
    parser.add_argument("--apply",action="store_true")
    args=parser.parse_args()
    m=json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    targets=validate(m)
    print("Validated",len(targets),"private Trek ffprobe target(s)")
    if not args.apply:return
    observations=[]
    with connect() as ftp:
        for target in targets:assert_unchanged(ftp,target)
        for target in targets:
            checked=inspect(target)
            observations.append({"from":target["from"],"size":target["size"],"modify":target["modify"],**checked})
            print("STREAM_PROBE",len(observations),checked["status"],flush=True)
    path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps({"targets":observations,"mode":"read_only","secrets_in_output":False},indent=2)+"\n",encoding="utf-8")
if __name__=="__main__":main()
