#!/usr/bin/env python3
"""Independent-source-listened ASR model evaluation, never an answer key for ASR.

Inputs are small *reviewer-confirmed original listening* truth packets and
unprompted model hypotheses. All share exact original AV SHA, source windows.
Emits WER and two-model joint-error evidence, not speaker or script acceptance.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

WORD=re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)?")
MAX_CASES=120
MAX_WORDS=300


def words(text):
    if not isinstance(text,str) or len(text)>1600:
        raise ValueError("Expected bounded original dialogue text")
    result=WORD.findall(text.casefold())
    if len(result)>MAX_WORDS:
        raise ValueError("Oversized listened dialogue or model hypothesis")
    return result


def edits(left,right):
    prev=list(range(len(right)+1))
    for i,a in enumerate(left,1):
        row=[i]
        for j,b in enumerate(right,1):
            row.append(min(prev[j]+1,row[-1]+1,prev[j-1]+(a!=b)))
        prev=row
    return prev[-1]


def calibrate(truth,hypotheses):
    sha=truth.get("original_video_sha256")
    cases=truth.get("cases")
    models=hypotheses.get("models")
    if (truth.get("schema")!="night-court-original-source-listened-dialogue-gold/1" or
        hypotheses.get("schema")!="night-court-original-model-calibration-proposals/1" or
        not isinstance(sha,str) or len(sha)!=64 or
        any(c not in "0123456789abcdef" for c in sha) or
        hypotheses.get("original_video_sha256")!=sha or
        not isinstance(cases,list) or not 1<=len(cases)<=MAX_CASES or
        not isinstance(models,list) or not 2<=len(models)<=4):
        raise ValueError("Missing independent original source and bounded study")
    reference={}
    for row in cases:
        ident=row.get("case_id")
        interval=row.get("source_interval_ms")
        if (not isinstance(ident,str) or not ident or ident in reference or
            not isinstance(interval,list) or len(interval)!=2 or
            any(type(x) is not int for x in interval) or
            not 0<=interval[0]<interval[1]<=1800000 or
            interval[1]-interval[0]>30000 or
            row.get("original_audio_independently_listened") is not True or
            row.get("reviewer_attested_original_words") is not True):
            raise ValueError("Unreviewed or ill-formed original audio reference")
        reference[ident]=(interval,words(row.get("verified_original_text")))
    results=[]
    by_model={}
    families=set()
    for model in models:
        ident=model.get("model_id")
        family=model.get("architecture_family")
        entries=model.get("cases")
        if (not isinstance(ident,str) or not ident or ident in by_model or
            not isinstance(family,str) or not family or
            model.get("original_subtitle_or_other_decoder_prompt_used") is not False or
            not isinstance(entries,list) or len(entries)!=len(reference)):
            raise ValueError("Non-independent or incomplete model proposal")
        by_id={}
        for row in entries:
            case_id=row.get("case_id")
            if case_id not in reference or case_id in by_id:
                raise ValueError("Different, missing or duplicate source window")
            if row.get("source_interval_ms")!=reference[case_id][0]:
                raise ValueError("Model / original source window mismatch")
            by_id[case_id]=words(row.get("model_hypothesis_text"))
        if set(by_id)!=set(reference):
            raise ValueError("Missing model source-time reference")
        by_model[ident]=by_id
        families.add(family)
        incorrect=sum(edits(reference[case][1],proposal) for case,proposal in by_id.items())
        denominator=sum(len(r[1]) for r in reference.values())
        results.append({"model_id":ident,"architecture_family":family,
                        "reference_words":denominator,
                        "word_edit_errors":incorrect,
                        "word_error_rate":round(incorrect/max(1,denominator),6)})
    if len(families)<2:
        raise ValueError("Distinct independent model architectures required")
    two=list(by_model)[:2]
    agreed=0
    joint_wrong=0
    all_right=0
    for case_id,(_,actual) in reference.items():
        a,b=by_model[two[0]][case_id],by_model[two[1]][case_id]
        if a==b:
            agreed+=1
            if a!=actual:joint_wrong+=1
            else:all_right+=1
    return {
      "schema":"night-court-listened-original-ASR-candidate-calibration/1",
      "source_video_sha256":sha,
      "independently_listened_windows":len(reference),
      "models":results,
      "first_two_models":two,
      "first_two_models_agree_windows":agreed,
      "two_models_jointly_wrong_when_agree_windows":joint_wrong,
      "agreement_joint_error_fraction":round(joint_wrong/agreed,6) if agreed else None,
      "first_two_models_agree_with_original_windows":all_right,
      "computed_from_attested_original_audio_only":True,
      "whole_episode_or_speaker_identity_accepted":False
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--independently-listened-gold",type=Path,required=True)
    p.add_argument("--models",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():p.error("Refuse overwrite")
    data=calibrate(json.loads(a.independently_listened_gold.read_bytes()),
                   json.loads(a.models.read_bytes()))
    data["source_gold_sha256"]=hashlib.sha256(a.independently_listened_gold.read_bytes()).hexdigest()
    data["source_models_sha256"]=hashlib.sha256(a.models.read_bytes()).hexdigest()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")


if __name__=="__main__":
    main()
