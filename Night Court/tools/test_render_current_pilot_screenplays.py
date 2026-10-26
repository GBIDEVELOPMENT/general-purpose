#!/usr/bin/env python3
"""Synthetic-only regression tests for private pilot screenplay rendering."""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from render_current_pilot_screenplays import (
    INPUT, INPUT_MANIFEST, SOURCE, build, check_source, display_join,
    group_rows, render, sha, time_envelope,
)

def fixture():
    rows=[]
    # 336 timed S01 original cues, including 68 synthetic second parts = 404.
    seq=[]
    for cue in range(1,337):
        seq.append(f"C{cue:03d}.1")
        if cue<=68:
            seq.append(f"C{cue:03d}.2")
    assert len(seq)==404
    for n,ref in enumerate(seq):
        cue=int(ref[1:4])
        rows.append({
            "episode_id":"S01E01", "reading_block_id":f"test-s01-{n}",
            "source_reading_ref":ref, "original_source_part_refs":[ref],
            "original_source_sha256":SOURCE["S01E01"][0],
            "caption_text":f"Test synthetic line {n}\nStill same cue.",
            "candidate_role":"HARRY STONE",
            "speaker_turn_boundary_verified":False,
            "actor_face_or_voice_independently_verified":False,
            "source_original_times_ms":{"start_ms":cue*3000,"end_ms":cue*3000+1200},
        })
    # 347 untimed paragraphs in 322 reading blocks (25 paragraph pairs).
    cue=1
    for n in range(322):
        refs=[f"C{cue:03d}.1"]
        cue+=1
        if n<25:
            refs.append(f"C{cue:03d}.1")
            cue+=1
        role="ROZ RUSSELL" if int(refs[-1][1:4])<=217 else None
        rows.append({
            "episode_id":"S09E19", "reading_block_id":f"test-s09-{n}",
            "source_reading_ref":refs[0], "original_source_part_refs":refs,
            "original_source_sha256":SOURCE["S09E19"][0],
            "caption_text":f"Untimed synthetic original part {n}.",
            "candidate_role":role,
            "speaker_turn_boundary_verified":False,
            "actor_face_or_voice_independently_verified":False,
            "source_original_times_ms":None,
            "original_source_untimed":True,
        })
    assert len(rows)==726 and cue==348
    raw="".join(json.dumps(row,sort_keys=True)+"\n" for row in rows).encode()
    manifest={
        "source_role_record_sha256":sha(raw),
        "original_caption_source_units":751,
        "provisional_named_original_source_units":621,
        "original_source_units_still_UNKNOWN":130,
        "current_provisional_speaking_blocks":726,
        "new_performer_turns_independently_audio_verified":0,
        "new_original_actor_identities_certified":0,
    }
    witnesses={ep:({"sha256":sha_val,"timecoded":timed},
                   [{"text":"synthetic"}]* (336 if timed else 347))
               for ep,(sha_val,_,timed) in SOURCE.items()}
    return rows,raw,manifest,witnesses

class CurrentPilotScreenplayTests(unittest.TestCase):
    def test_full_synthetic_original_unit_and_role_invariants(self):
        rows,raw,manifest,witnesses=fixture()
        self.assertEqual(check_source(rows,manifest,raw,witnesses),
                         {"original_source_units":751,"named_provisional":621,"unknown":130})
        scripts,sidecars,summary=render(rows)
        self.assertEqual({x:len(v) for x,v in sidecars.items()},
                         {"S01E01":404,"S09E19":322})
        self.assertEqual(sum(x["display_joins_unverified"] for x in summary.values()),
                         726-sum(x["display_groups"] for x in summary.values()))
        self.assertIn("scene",scripts["S01E01"].lower())
        self.assertIn("entirely untimed",scripts["S09E19"])
        self.assertNotIn("879532",scripts["S01E01"])  # No injected performance clock.
        self.assertTrue(all(x["actual_original_av_reviewer_accepted"] is False
                            for v in sidecars.values() for x in v))
        self.assertEqual(sidecars["S01E01"][0]["exact_rendered_caption_sha256"],
                         hashlib.sha256(rows[0]["caption_text"].encode()).hexdigest())

    def test_layout_joins_only_provisionally_named_distinct_source_parts(self):
        rows,_,_,_=fixture()
        left,right=rows[0],rows[1]
        self.assertFalse(display_join(left,right)) # Same original cue (different part).
        pair=[row for row in rows if row["episode_id"]=="S01E01"
              and row["source_reading_ref"] in ("C069.1","C070.1")]
        self.assertEqual(len(pair),2)
        self.assertTrue(display_join(*pair))
        unknown=copy.deepcopy(pair[1]);unknown["candidate_role"]=None
        self.assertFalse(display_join(pair[0],unknown))
        changed=copy.deepcopy(pair[1]);changed["candidate_role"]="DAN FIELDING"
        self.assertFalse(display_join(pair[0],changed))
        changed=copy.deepcopy(pair[1]);changed["source_original_times_ms"]={
            "start_ms":2_000_000,"end_ms":2_001_000}
        self.assertFalse(display_join(pair[0],changed))
        changed=copy.deepcopy(pair[1]);changed["original_source_part_refs"]=pair[0]["original_source_part_refs"]
        self.assertFalse(display_join(pair[0],changed))
        grouped=group_rows(rows,compact=False)
        self.assertEqual(sum(map(len,grouped["S01E01"])),404)
        self.assertTrue(all(len(group)==1 for group in grouped["S01E01"]))

    def test_source_chronology_restored_when_role_reader_input_interleaves_episodes(self):
        rows,_,manifest,witnesses=fixture()
        # A source-patch pipeline may append an older S01 role change after S09.
        unsorted=rows[404:]+rows[1:404]+rows[:1]
        scrambled="".join(json.dumps(row,sort_keys=True)+"\\n" for row in unsorted).encode()
        updated=dict(manifest,source_role_record_sha256=sha(scrambled))
        self.assertEqual(check_source(unsorted,updated,scrambled,witnesses)["original_source_units"],751)
        scripts,sidecars,summary=render(unsorted,compact=False)
        self.assertEqual(sidecars["S01E01"][0]["reading_block_id"],"test-s01-0")
        self.assertEqual(sidecars["S01E01"][-1]["reading_block_id"],"test-s01-403")
        self.assertEqual(sidecars["S09E19"][0]["reading_block_id"],"test-s09-0")
        self.assertEqual(summary["S01E01"]["source_blocks"],404)
        self.assertIn("Test synthetic line 0",scripts["S01E01"])

    def test_invalid_source_changes_and_fake_s09_times_fail_closed(self):
        rows,raw,manifest,witnesses=fixture()
        fake=copy.deepcopy(rows)
        fake[-1]["source_original_times_ms"]={"start_ms":1,"end_ms":2}
        with self.assertRaisesRegex(ValueError,"Invented original S09 timing"):
            check_source(fake,manifest,raw,witnesses)
        fake=copy.deepcopy(rows)
        fake[0]["actor_face_or_voice_independently_verified"]=True
        with self.assertRaisesRegex(ValueError,"review status"):
            check_source(fake,manifest,raw,witnesses)
        fake=copy.deepcopy(rows);fake.pop()
        with self.assertRaisesRegex(ValueError,"manifest/count"):
            check_source(fake,manifest,raw,witnesses)
        changed=copy.deepcopy(manifest);changed["source_role_record_sha256"]="bad"
        with self.assertRaisesRegex(ValueError,"manifest/count"):
            check_source(rows,changed,raw,witnesses)
        changed=copy.deepcopy(witnesses)
        changed["S01E01"]=({"sha256":"wrong","timecoded":True},changed["S01E01"][1])
        with self.assertRaisesRegex(ValueError,"SHA/identity"):
            check_source(rows,manifest,raw,changed)
        with self.assertRaisesRegex(ValueError,"Invalid original cue time"):
            time_envelope({"source_original_times_ms":{"start_ms":9,"end_ms":8}})

    def test_private_output_is_generated_but_not_written_into_git_tree(self):
        rows,raw,manifest,witnesses=fixture()
        with TemporaryDirectory() as temp:
            parent=Path(temp);root=parent/"repo";root.mkdir()
            reader=parent/"private-reader";reader.mkdir()
            (reader/INPUT).write_bytes(raw)
            (reader/INPUT_MANIFEST).write_text(json.dumps(manifest),"utf-8")
            with patch("render_current_pilot_screenplays.load_witness",
                       side_effect=lambda _root,ep:witnesses[ep]):
                report=build(root,reader,parent/"private-output")
            self.assertEqual(report["source_unit_counts"]["original_source_units"],751)
            for ep in SOURCE:
                self.assertTrue((parent/"private-output"/f"{ep}-working-screenplay.md").is_file())
                lines=(parent/"private-output"/f"{ep}-working-screenplay-provenance.jsonl").read_text().splitlines()
                self.assertEqual(len(lines),summary_count(ep))
            with self.assertRaisesRegex(ValueError,"never be written inside repo"):
                build(root,reader,root/"prohibited")

def summary_count(ep):
    return 404 if ep=="S01E01" else 322

if __name__=="__main__":
    unittest.main()
