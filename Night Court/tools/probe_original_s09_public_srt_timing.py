#!/usr/bin/env python3
"""Recover an *independent secondary* S09 subtitle timing witness, if verifiable.

The held 347-paragraph Night Court text remains immutable and UNTIMED.
Candidate times from a public secondary source are never original-video PTS,
speech timecodes, or certification until compared against verified video.
Fail closed: partial, altered or inaccessible pages yield an abstention report.
No AV/ASR/model work required.
"""
from __future__ import annotations
import argparse,hashlib,html,json,re,urllib.request
from difflib import SequenceMatcher
from html.parser import HTMLParser
from pathlib import Path
from build_caption_first_working_drafts import ROOT,SOURCE_SHA,witness

EP="S09E19"
URL="https://www.subtitlecat.com/subs/1592/S09E19%20-%20PS%20Do%20i%20know%20you.html"
MAX_BYTES=5_000_000
MARK=re.compile(r"(?<!\d)(?P<cue>\d{1,3})\s+(?P<a>\d{2}:\d{2}:\d{2}[.,]\d{3})\s*-->\s*(?P<b>\d{2}:\d{2}:\d{2}[.,]\d{3})")
HTML_TAGS=re.compile(r"(?s)<[^>]{1,1000}>")
CONTROL=re.compile(r"\s+")


class AllText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.text=[]
    def handle_data(self,data):self.text.append(data)


def norm(s):
    return CONTROL.sub(" ",html.unescape(s).replace("\r","").strip()).strip()


def clock(s):
    h,m,t=s.replace(",",".").split(":")
    whole,frac=t.split(".")
    fields=[int(h),int(m),int(whole),int(frac)]
    if fields[1]>59 or fields[2]>59 or fields[3]>999:
        raise ValueError("Malformed source time")
    return ((fields[0]*60+fields[1])*60+fields[2])*1000+fields[3]


def clean_source_candidate(raw):
    raw=html.unescape(raw)
    raw=raw.replace("\\n","\n").replace("\\r"," ").replace("\\t"," ")
    raw=HTML_TAGS.sub(" ",raw)
    raw=re.sub(r"(?m)^\s*\d{1,3}\s*$"," ",raw)
    return norm(raw)


def candidates_from_visible_text(text,source_rows):
    spans=list(MARK.finditer(text))
    if not spans:
        return None,{"raw_time_markers":0,"candidate_numbered_time_markers":0,
                     "exact_source_text_matches":0,"accepted":False,
                     "reason":"no_public_html_srt_time_markers"}
    by_id={}
    for idx,m in enumerate(spans):
        n=int(m["cue"])
        if not 1<=n<=len(source_rows):continue
        start,end=clock(m["a"]),clock(m["b"])
        after=text[m.end():(spans[idx+1].start() if idx+1<len(spans) else len(text))]
        clean=clean_source_candidate(after)
        expected=norm(source_rows[n-1]["text"])
        # Secondary source must match the held witness exactly (not merely
        # ASR/lexical similarity). External timing drift remains unresolved.
        same=clean==expected
        if not same and clean and len(clean)<1500:
            # Some pages have interface/footer text after the last cue,
            # never silently accept that as source dialogue.
            ratio=SequenceMatcher(None,clean,expected).ratio()
        else:ratio=1.0 if same else 0
        by_id.setdefault(n,[]).append({
            "cue":n,"candidate_start_ms":start,"candidate_end_ms":end,
            "witness_text_exact_match":same,"similarity":round(ratio,4)})
    selected=[]
    for n in range(1,len(source_rows)+1):
        row=by_id.get(n,[])
        good=[x for x in row if x["witness_text_exact_match"]
              and x["candidate_start_ms"]<x["candidate_end_ms"]
              and x["candidate_end_ms"]<=1_800_000]
        if len(good)!=1:
            return None,{"raw_time_markers":len(spans),"candidate_numbered_time_markers":sum(map(len,by_id.values())),
                         "exact_source_text_matches":sum(any(x["witness_text_exact_match"] for x in z) for z in by_id.values()),
                         "accepted":False,"reason":"missing_duplicate_or_nonexact_source_time_pairs",
                         "first_unresolved_source_cue":n}
        selected.append({k:good[0][k] for k in ("cue","candidate_start_ms","candidate_end_ms")})
    if any(b["candidate_start_ms"]<a["candidate_start_ms"] or
           b["candidate_end_ms"]<a["candidate_end_ms"]
           for a,b in zip(selected,selected[1:])):
        return None,{"raw_time_markers":len(spans),
                     "exact_source_text_matches":len(selected),"accepted":False,
                     "reason":"nonmonotonic_external_subtitle_times"}
    return selected,{"raw_time_markers":len(spans),"exact_source_text_matches":len(selected),
                     "accepted":True,"reason":"all_original_witness_paragraphs_exactly_matched"}


def probe_download(timeout=15):
    headers={"User-Agent":"Mozilla/5.0 (compatible; OriginalCaptionResearch/1.0)",
             "Accept":"text/html"}
    request=urllib.request.Request(URL,headers=headers)
    with urllib.request.urlopen(request,timeout=timeout) as response:
        if response.geturl()!=URL:
            raise ValueError("Unexpected redirect from hardcoded public subtitle host")
        size=response.headers.get("Content-Length")
        if size and int(size)>MAX_BYTES:
            raise ValueError("Public page exceeds source-text read budget")
        body=response.read(MAX_BYTES+1)
        if len(body)>MAX_BYTES:raise ValueError("Public subtitle page exceeds byte cap")
        if response.status!=200:raise ValueError("Public subtitle page unsuccessful")
    return body


def analyze(raw:bytes,source_rows):
    decoded=raw.decode("utf-8","replace")
    markup_plain=clean_source_candidate(decoded)
    parser=AllText();parser.feed(decoded)
    # Several public page builds expose timing in script or JSON while their
    # rendered original-language subtitle view omits it. Probe both, require
    # the same all-347 original paragraph identity before promoting any time.
    variants=[("html_text_and_scripts_flattened",markup_plain),
              ("rendered_html_visible_text",norm(" ".join(parser.text))),
              ("source_unescaped_raw",html.unescape(decoded))]
    attempts=[]
    for mode,txt in variants:
        try:
            rows,meta=candidates_from_visible_text(txt,source_rows)
        except ValueError as exc:
            attempts.append({"method":mode,"accepted":False,"reason":str(exc)[:80]})
            continue
        attempts.append({"method":mode,**meta})
        if rows is not None:
            return rows,{"probed_variants":attempts,"selected_extract_mode":mode}
    return None,{"probed_variants":attempts,"selected_extract_mode":None}


def build(public_body=None):
    _,metadata,cues,units,_=witness(EP)
    if metadata["timecoded"] is not False or len(cues)!=347:
        raise ValueError("Never change original source paragraph timing witness")
    base={"schema":"night-court-s09-secondary-externally-timed-original-text-probe/1",
          "episode_id":EP,"public_secondary_source_url":URL,
          "original_untimed_source_caption_sha256":SOURCE_SHA[EP],
          "held_source_original_paragraphs":347,
          "original_video_synchronization_verified":False,
          "original_episode_speaker_identity_verified":False,
          "original_witness_timestamps_edited":False,
          "original_av_cuts_verified":False}
    if public_body is None:
        try:public_body=probe_download()
        except Exception as exc:
            base.update({"status":"ABSTAIN_NETWORK_OR_SOURCE_UNAVAILABLE",
                         "fetch_error_type":type(exc).__name__,"verified_secondary_timed_cues":0,
                         "original_source_video_clock_sync_accepted":False})
            return base
    rows,detail=analyze(public_body,cues)
    base.update({"secondary_download_sha256":hashlib.sha256(public_body).hexdigest(),
                 "probe_details":detail})
    if rows is None:
        base.update({"status":"ABSTAIN_UNVERIFIED_SECONDARY_TIMING",
                     "verified_secondary_timed_cues":0,
                     "original_source_video_clock_sync_accepted":False})
    else:
        base.update({"status":"SECONDARY_CUE_TIMES_ALL_SOURCE_TEXT_EXACT",
                     "verified_secondary_timed_cues":347,
                     "source_video_clock_sync_claimed":False,
                     "secondary_candidate_cue_times":rows})
    return base


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--offline-test",action="store_true")
    args=p.parse_args()
    if args.offline_test:
        print("Offline unit tests must call build(fake bytes), not download real sources")
        return
    report=build()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n","utf-8")
    print("Secondary original-episode source:",report["status"],
          "; candidate timed text cues:",report["verified_secondary_timed_cues"],
          "; 347-source-original transcript remains untimed.")


if __name__=="__main__":main()
