import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from trek_probe import validate, read_header, MAX_HEADER_BYTES
def item(path="/downloads/Star Trek/Star Trek Strange New Worlds S03E03 HDR 2160p.mkv"):
    return {"from":path,"size":1000000,"modify":"20261023093000"}
def plan(entries):
    return {"root":"/downloads","description":"Read-only HDR and DV metadata probe on exact vetted private media","targets":entries}
class ProbeTests(unittest.TestCase):
    def test_bounded_header_read_and_control_connection_close(self):
        import tempfile
        from unittest.mock import patch
        x=item()
        class FakeFTP:
            closed=False
            def cwd(self,d):self.current=d
            def mlsd(self):return iter([(Path(x["from"]).name,{"type":"file","size":"1000000","modify":"20261023093000"})])
            def retrbinary(self,cmd,callback,blocksize=None):
                callback(b"x"*(MAX_HEADER_BYTES+1024))
            def close(self):self.closed=True
        ftp=FakeFTP()
        with tempfile.TemporaryDirectory() as tmp:
            destination=str(Path(tmp)/"small.mkv")
            with patch("trek_probe.connect",return_value=ftp):
                n=read_header(x,destination)
            self.assertEqual(n,MAX_HEADER_BYTES)
            self.assertEqual(Path(destination).stat().st_size,MAX_HEADER_BYTES)
            self.assertTrue(ftp.closed)
    def test_valid(self):self.assertEqual(len(validate(plan([item()]))),1)
    def test_escape(self):
        with self.assertRaises(ValueError):validate(plan([item("/downloads/../secret/file.mkv")]))
    def test_no_non_trek(self):
        with self.assertRaises(ValueError):validate(plan([item("/downloads/Other Show S01E01.mkv")]))
    def test_duplicate(self):
        with self.assertRaises(ValueError):validate(plan([item(),item()]))
    def test_requires_timestamp(self):
        x=item();x["modify"]=None
        with self.assertRaises(ValueError):validate(plan([x]))
if __name__=="__main__":unittest.main()
