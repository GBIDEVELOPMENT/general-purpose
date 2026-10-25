#!/usr/bin/env python3
"""Second-pass bounded original-video action review for the two Night Court pilots.

Extends the previously verified, single-download per episode original-AVI
5-fps still/movie-contact-sheet engine. Only the action windows change.
Outputs are temporary private image sheets, NOT copyrighted media in Git
nor inferred words, characters, shot continuity or native frame PTS.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import capture_original_physical_beats as baseline

PASSES={
  "S01E01":[
     (0,20,"opening-painter-window-business"),
     (838,20,"judge-ear-coin-conjuring"),
     (1094,20,"double-headed-coin-kerr-reconciliation")],
  "S09E19":[
     (551,20,"hidden-safe-combination-and-warning"),
     (812,20,"restaurant-two-impostors-entry"),
     (1280,20,"hidden-safe-final-reveal")]
}
PREVIOUS={episode:list(baseline.SOURCES[episode][1]) for episode in PASSES}
MAX_WINDOWS=3
MAX_TOTAL_SOURCE_SECONDS_PER_EPISODE=60

def configure(episode):
    if episode not in PASSES:
        raise ValueError("Only original two source-SHA-verified pilots")
    original_sha=baseline.SOURCES[episode][0]
    new=PASSES[episode]
    prior=PREVIOUS[episode]
    if len(new)!=MAX_WINDOWS or sum(n for _,n,_ in new)>MAX_TOTAL_SOURCE_SECONDS_PER_EPISODE:
        raise ValueError("Review coverage would exceed bounded source action budget")
    spans=[]
    labels=set()
    limit=1320 if episode=='S09E19' else 1448
    for start,duration,label in new:
        if (type(start) is not int or type(duration) is not int
            or duration!=20 or start<0 or start+duration>limit):
            raise ValueError("Invalid source window")
        if label in labels or not label or any(not (start+duration<=a or start>=a+b) for a,b,_ in spans+prior):
            raise ValueError("Duplicate/overlapping old and new source action windows")
        labels.add(label);spans.append((start,duration,label))
    baseline.SOURCES[episode]=(original_sha,new)
    checked=baseline.windows(episode)
    if checked!=new:raise ValueError("Source windows were not configured exactly")
    return original_sha,checked


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--episode",choices=sorted(PASSES),required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--ftp",action="store_true")
    a=p.parse_args()
    configure(a.episode)
    if not a.ftp:p.error("Review photos only from trusted SHA-bound original source")
    baseline.ftp_mode(a.episode,a.output)


if __name__=="__main__":main()
