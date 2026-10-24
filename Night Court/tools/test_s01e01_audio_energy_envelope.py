#!/usr/bin/env python3
"""No raw audio or inferred source dialogue in synthetic acoustic evidence."""
import array,copy,math,sys,unittest
from probe_s01e01_audio_energy_envelope import envelope_pcm,tasks_from_envelope,contract,RATE

class OriginalAudioEnergy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m,cls.packet=contract()

    def synthetic(self):
        samples=array.array("h")
        for i in range(37*RATE):
            seconds=i/RATE
            amp=0 if seconds<2 else 0.2*math.sin(2*math.pi*440*seconds)
            samples.append(int(amp*32767))
        if sys.byteorder!="little":samples.byteswap()
        return samples.tobytes()

    def test_small_synthetic_energy_envelope_and_abstentions(self):
        rows=envelope_pcm(self.synthetic())
        self.assertEqual(len(rows),370)
        self.assertEqual(rows[0]["nominal_start_ms"],56912)
        self.assertEqual(rows[-1]["nominal_end_ms"],93912)
        self.assertTrue(all(x["rms_dbfs"]==-120 for x in rows[:20]))
        self.assertTrue(-18<rows[100]["rms_dbfs"]<-16)
        self.assertTrue(-15<rows[100]["peak_dbfs"]<-13)
        byturn=tasks_from_envelope(self.packet,rows)
        self.assertEqual(len(byturn),11)
        self.assertTrue(all(not t["original_speech_present_verified"] for t in byturn))
        self.assertTrue(all(not t["speaker_or_delivery_verified"] for t in byturn))

    def test_reject_unsafe_pcm_and_missing_caption_windows(self):
        with self.assertRaisesRegex(ValueError,"bounded"):
            envelope_pcm(b"a"*(1_600_002))
        with self.assertRaisesRegex(ValueError,"small bounded"):
            envelope_pcm(b"x")
        short=envelope_pcm(b"\x00\x00"*RATE)
        with self.assertRaisesRegex(ValueError,"outside acoustic window"):
            tasks_from_envelope(self.packet,short)

    def test_exact_historical_source_hash_metadata(self):
        self.assertEqual(self.m["source_video_sha256"],
                         "5b607acc60fae6893aa76e5b02fc34900cbe68050eac486b31382dc91e504962")
        self.assertEqual(self.packet["counts"]["source_speaking_turns"],11)

if __name__=="__main__":
    unittest.main()
