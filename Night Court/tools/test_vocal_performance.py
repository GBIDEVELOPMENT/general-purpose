#!/usr/bin/env python3
"""Synthetic acoustic regression; no real episode audio or model weights."""
import json, math, struct, subprocess, sys, tempfile, wave
from pathlib import Path
SCRIPT=Path(__file__).with_name("measure_vocal_performance.py")
def main():
    with tempfile.TemporaryDirectory() as tmp:
        wav=Path(tmp)/"synthetic.wav"
        rate=16000
        signal=[int(3000*math.sin(2*math.pi*220*i/rate)) for i in range(rate)]
        with wave.open(str(wav),"wb") as w:
            w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate)
            w.writeframes(struct.pack("<"+str(len(signal))+"h",*signal))
        out=subprocess.check_output([sys.executable,str(SCRIPT),"--wav",str(wav),
             "--episode","S01E01","--source-id","fixture","--start-ms","0",
             "--end-ms","1000"],text=True)
        j=json.loads(out)
        assert -25 < j["features"]["rms_dbfs"] < -20,j
        assert -23 < j["features"]["peak_dbfs"] < -20,j
        assert j["features"]["f0_median_hz"] is None
        assert j["features"]["speaker_id"] is None
        assert j["features"]["emotion_label"] is None
        assert j["features"]["mix_activity_fraction_above_minus_40_dbfs"]==1.0
        assert j["wav_sha256"] and j["segment_pcm_sha256"]
        for bad in [(-1,100),(0,31000),(2000,3000)]:
            p=subprocess.run([sys.executable,str(SCRIPT),"--wav",str(wav),
                "--episode","S01E01","--source-id","fixture",
                "--start-ms",str(bad[0]),"--end-ms",str(bad[1])],
                capture_output=True,text=True)
            assert p.returncode!=0,(bad,p.stdout,p.stderr)
    print("Synthetic vocal baseline regression passed: input gates, audio metrics, abstentions and hashes")
if __name__=="__main__":main()
