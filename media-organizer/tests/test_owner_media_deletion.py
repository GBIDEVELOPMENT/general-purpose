"""Owner-approved media deletion remains exact-match pinned and non-generalizable."""
import json
import pathlib
import unittest
from tempfile import TemporaryDirectory
from unittest.mock import patch
import sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from delete_debris import validate, OWNER_MEDIA_BATCH

ORIGINAL=pathlib.Path("media-organizer/approved-delete.json")
class OwnerMediaValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=json.loads(ORIGINAL.read_text(encoding="utf-8"))
        assert cls.doc["batch_id"]==OWNER_MEDIA_BATCH
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
