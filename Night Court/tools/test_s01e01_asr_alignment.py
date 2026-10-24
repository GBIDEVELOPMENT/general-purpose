#!/usr/bin/env python3
"""Offline text-alignment heuristic checks without model weights."""
from run_s01e01_asr_prosody import propose_alignment,normalized
def main():
    assert normalized('Hello, World!')=='hello world'
    src=[{"cue":10,"start_ms":60000,"text":"The judge will be here any minute."},
         {"cue":20,"start_ms":66000,"text":"I pick a word every month."}]
    asr=[{"index":0,"text":"I pick a word every month.","start_ms":66500,"end_ms":68000}]
    out=propose_alignment(asr,src)
    assert out[0]["candidate_caption_cue"]==20
    assert out[0]["suggested_offset_ms"]==500
    assert out[0]["status"]=="automated_heuristic_not_verified"
    print("Source time-map proposal remains non-authoritative by construction")
if __name__=="__main__":main()
