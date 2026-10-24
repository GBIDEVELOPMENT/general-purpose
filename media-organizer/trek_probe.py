#!/usr/bin/env python3
"""Read-only bounded ffprobe against exact FTP Trek media files, no media downloads saved."""
from __future__ import annotations
import argparse,ftplib,json,os,re,subprocess
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

def inspect(x):
    user=os.environ["FTP_USER"];password=os.environ["FTP_PASSWORD"];host=os.environ["FTP_HOST"]
    url="ftp://"+quote(user,safe="")+":"+quote(password,safe="")+"@"+host+quote(x["from"],safe="/")
    command=["ffprobe","-hide_banner","-loglevel","error",
             "-probesize","131072","-analyzeduration","1000000",
             "-select_streams","v:0","-show_entries",
             "stream=codec_name,profile,pix_fmt,width,height,color_range,color_space,color_transfer,color_primaries,side_data_list",
             "-of","json",url]
    try:
        response=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=40,check=False)
        if response.returncode!=0:
            message=response.stderr.decode("utf-8",errors="replace").lower()
            if "protocol not found" in message or "unknown protocol" in message:
                reason="unsupported_input_protocol"
            elif "530 " in message or "login incorrect" in message or "authentication" in message:
                reason="ftp_authentication"
            elif "550 " in message or "no such file" in message:
                reason="ftp_path_unavailable"
            elif "invalid data" in message or "invalid argument" in message:
                reason="media_input_or_url_invalid"
            elif "connection refused" in message or "timed out" in message:
                reason="network"
            elif "end of file" in message:
                reason="unexpected_eof"
            else:reason="other_input_error"
            return {"status":"probe_failed","exit_code":response.returncode,"error_class":reason}
        data=json.loads(response.stdout.decode("utf-8"))
        streams=data.get("streams",[])
        if not streams:return {"status":"no_video_metadata"}
        stream=streams[0]
        return {"status":"probed","stream":{k:stream.get(k) for k in
            ("codec_name","profile","pix_fmt","width","height","color_range","color_space","color_transfer","color_primaries","side_data_list") if k in stream}}
    except subprocess.TimeoutExpired:return {"status":"timeout"}
    except (OSError,UnicodeError,ValueError):return {"status":"probe_error"}

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
