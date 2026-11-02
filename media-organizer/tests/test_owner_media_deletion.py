"""Owner-approved media deletion remains exact-match pinned and non-generalizable."""
import json
import pathlib
import unittest
from tempfile import TemporaryDirectory
from unittest.mock import patch
import sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from delete_debris import validate, OWNER_MEDIA_BATCH

ORIGINAL=pathlib.Path("media-organizer/review/ftp-selected-title-delete-2026-11-01.json")
CURRENT=pathlib.Path("media-organizer/approved-delete.json")
class OwnerMediaValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        prior=json.loads(ORIGINAL.read_text(encoding="utf-8"))
        cls.doc={"root":"/downloads","batch_id":OWNER_MEDIA_BATCH,"description":"Previous exact 289-media owner approval retained for regression tests.",
                 "entries":[{"from":f["path"],"size":f["size_bytes"],"modify":f["modify_ftp"],"category":"owner_media"}
                            for g in prior["groups"] for f in g["files"]]}
    def test_full_approved_manifest(self):
        self.assertEqual(len(validate(self.doc)),289)
    def test_unselected_media_denied(self):
        candidate=json.loads(json.dumps(self.doc))
        candidate["entries"][0]["from"]="/downloads/other-file.mkv"
        with self.assertRaises(ValueError):validate(candidate)
    def test_changed_size_denied(self):
        candidate=json.loads(json.dumps(self.doc))
        candidate["entries"][10]["size"]+=1
        with self.assertRaises(ValueError):validate(candidate)
    def test_broader_media_category_denied(self):
        candidate=json.loads(json.dumps(self.doc))
        candidate["batch_id"]="generic_media_005"
        with self.assertRaises(ValueError):validate(candidate)
    def test_missing_entry_denied(self):
        candidate=json.loads(json.dumps(self.doc))
        candidate["entries"].pop()
        with self.assertRaises(ValueError):validate(candidate)
    def test_original_debris_still_works(self):
        doc={"root":"/downloads","batch_id":"debri_005","description":"remove one approved nfo detritus only","entries":[{"from":"/downloads/show/movie.nfo","size":15,"modify":"20260101120000","category":"nfo"}]}
        self.assertEqual(len(validate(doc)),1)
if __name__=="__main__":unittest.main()

class TVDuplicationValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=json.loads(CURRENT.read_text(encoding="utf-8"))
        assert cls.doc["batch_id"]=="owner_tv_dedupe_20261102_080"
    def test_approved_80_exact_files(self):
        from delete_debris import tv_keepers
        self.assertEqual(len(validate(self.doc)),80)
        keepers=tv_keepers(self.doc)
        self.assertEqual(len(keepers),80)
        self.assertFalse(set(keepers) & {v["from"] for v in keepers.values()})
    def test_changed_loser_rejected(self):
        candidate=json.loads(json.dumps(self.doc))
        candidate["entries"][0]["size"]+=1
        with self.assertRaises(ValueError):validate(candidate)
    def test_wrong_series_rejected(self):
        candidate=json.loads(json.dumps(self.doc))
        candidate["entries"][0]["from"]="/downloads/Studio 60 on the Sunset Strip/Season 01/Studio 60 S01E01.mp4"
        with self.assertRaises(ValueError):validate(candidate)
    def test_wrong_batch_id_rejected(self):
        candidate=json.loads(json.dumps(self.doc))
        candidate["batch_id"]="generic_tv_delete_001"
        with self.assertRaises(ValueError):validate(candidate)
    def test_missing_file_rejected(self):
        candidate=json.loads(json.dumps(self.doc))
        candidate["entries"].pop()
        with self.assertRaises(ValueError):validate(candidate)
