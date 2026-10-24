#!/usr/bin/env python3
"""Monotonic CTC character/word forced alignment with an explicit abstention gate.

Pure NumPy core, independent of removed torchaudio.functional.forced_align.
Real model inference is isolated in s01e01_ctc_source_pilot.py.
"""
import math
import re
import numpy as np

WORD = re.compile(r"[A-Za-z]+(?:['\u2019][A-Za-z]+)*")

def normalize_words(text):
    """CTC label sequence for wav2vec2 uppercase English vocabulary."""
    return [re.sub("[^A-Z]", "", x.upper()) for x in WORD.findall(text) if re.sub("[^A-Z]", "", x.upper())]

def encode(words, vocabulary):
    if not words: raise ValueError("No words to align")
    if "|" not in vocabulary: raise ValueError("Missing CTC space symbol")
    letters, mapping = [], []
    for n, word in enumerate(words):
        if n:
            letters.append(vocabulary["|"]);mapping.append(None)
        for character in word:
            if character not in vocabulary:raise ValueError("Unsupported character "+character)
            letters.append(vocabulary[character]);mapping.append(n)
    return letters,mapping

def viterbi(log_probability,labels,blank):
    """Maximum CTC path for a fixed transcript with blanks/repeats.

    States alternate blank, letter, blank. A skip over a blank may
    not merge identical adjacent letters. Always allow ending on the
    final letter or terminal blank. Returns state path and scores.
    """
    lp=np.asarray(log_probability,dtype=np.float64)
    if lp.ndim!=2 or not np.isfinite(lp).all():raise ValueError("Invalid CTC emissions")
    timesteps, classes=lp.shape
    if not 0<=blank<classes or not labels or any(not 0<=x<classes for x in labels):
        raise ValueError("Missing or invalid CTC tokens")
    # A CTC transcript needs a frame for every label and another for each
    # repeated adjacent label, otherwise any supposed alignment is fabricated.
    minimum=len(labels)+sum(a==b for a,b in zip(labels,labels[1:]))
    if timesteps<minimum:raise ValueError("Not enough acoustic frames for source transcript")
    states=[blank]
    for label in labels:states.extend([label,blank])
    ns=len(states)
    neg=-float("inf")
    prev=np.full(ns,neg)
    trace=np.full((timesteps,ns),-1,dtype=np.int32)
    prev[0]=lp[0,blank]
    prev[1]=lp[0,labels[0]]
    for t in range(1,timesteps):
        curr=np.full(ns,neg)
        for s,label in enumerate(states):
            opts=[(prev[s],s)]
            if s>=1:opts.append((prev[s-1],s-1))
            if s>=2 and s%2==1 and label!=states[s-2]:
                opts.append((prev[s-2],s-2))
            best_score,best_state=max(opts,key=lambda x:x[0])
            if np.isfinite(best_score):
                curr[s]=best_score+lp[t,label]
                trace[t,s]=best_state
        prev=curr
    final=max((ns-1,ns-2),key=lambda s:prev[s])
    if not np.isfinite(prev[final]):raise ValueError("Transcript cannot be CTC-aligned")
    path=[final]
    for t in range(timesteps-1,0,-1):
        last=trace[t,path[-1]]
        if last<0:raise ValueError("Invalid CTC traceback")
        path.append(int(last))
    path.reverse()
    return path,float(prev[final]),states

def align_words(log_probability, transcript, dictionary, blank, absolute_start_ms,
                frame_step_ms, min_confidence=0.15):
    words=normalize_words(transcript)
    labels,mapping=encode(words,dictionary)
    path,logscore,states=viterbi(log_probability,labels,blank)
    scores=np.asarray(log_probability,dtype=np.float64)
    indices=[[] for _ in words]
    for t,s in enumerate(path):
        if s%2==1:
            wi=mapping[(s-1)//2]
            if wi is not None:indices[wi].append(t)
    result=[]
    for word,frames in zip(words,indices):
        if not frames:
            result.append({"word":word,"status":"abstain_unassigned","time_candidate_ms":None})
            continue
        confidences=[math.exp(float(scores[t,states[path[t]]])) for t in frames]
        prob=round(float(np.mean(confidences)),4)
        result.append({
           "word":word,
           "time_candidate_ms":[round(absolute_start_ms+min(frames)*frame_step_ms),
                                round(absolute_start_ms+(max(frames)+1)*frame_step_ms)],
           "mean_matched_ctc_frame_probability":prob,
           "status":"candidate_unreviewed" if prob>=min_confidence else "abstain_low_acoustic_support"
        })
    return {
       "words":result,"ctc_path_average_log_probability":round(logscore/len(path),4),
       "frames":len(path),"aligned_word_candidates":sum(x["status"]=="candidate_unreviewed" for x in result),
       "abstentions":sum(x["status"]!="candidate_unreviewed" for x in result),
       "alignment_source":"known_original_caption_constrained_ctc_not_a_transcription",
       "audio_word_timing_verified":False
    }
