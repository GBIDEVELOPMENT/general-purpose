import unittest, importlib.util, os
from unittest import mock
from pathlib import Path
spec=importlib.util.spec_from_file_location("organize",Path(__file__).resolve().parents[1]/"organize.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def inventory(*names):
    return {"files":[{"path":name,"size":15} for name in names],"failures":[],"truncated":[]}
class OrganizerTests(unittest.TestCase):
    def test_path_guard(self):
        for p in ("/etc/passwd","/downloads/../other","/downloads/a\\b","/downloads/file\x00.mkv"):
            with self.assertRaises(ValueError):m.safe(p)
    def test_episode_candidate(self):
        result=m.propose(inventory("/downloads/Comedy.Show.S1E2.720p.mkv"))
        self.assertEqual(result["moves"][0]["to"],"/downloads/Comedy Show - S01E02.mkv")
    def test_parent_title_inference(self):
        result=m.propose(inventory("/downloads/Night Court/Season 1/S01E01.mkv"))
        self.assertEqual(result["moves"][0]["to"],"/downloads/Night Court/Season 1/Night Court - S01E01.mkv")
    def test_sidecar_language_not_episode_title(self):
        result=m.propose(inventory("/downloads/Comedy.Show.S1E2.en.forced.srt"))
        self.assertEqual(result["moves"][0]["to"],"/downloads/Comedy Show - S01E02.en.forced.srt")
    def test_no_ambiguous_movie_rename(self):
        self.assertEqual(m.propose(inventory("/downloads/Some.Movie.1999.mkv"))["moves"],[])
    def test_multi_episode_quarantined(self):
        result=m.propose(inventory("/downloads/Comedy.Show.S01E01E02.mkv"))
        self.assertEqual(result["moves"],[])
        self.assertEqual(result["review"][0]["reason"],"Multi-episode file requires review")
    def test_collision_quarantined(self):
        result=m.propose(inventory("/downloads/Comedy.Show.S1E2.mkv","/downloads/Comedy Show - S01E02.mkv"))
        self.assertEqual(result["moves"],[])
        self.assertEqual(result["review"][0]["reason"],"Destination collision")
    def test_connect_retries_temporary_timeout_only(self):
        class FakeFTP:
            def __init__(self,fail=False):self.fail=fail;self.closed=False
            def connect(self,*args):
                if self.fail:raise TimeoutError("temporary outage")
            def login(self,*args):return None
            def close(self):self.closed=True
        bad=FakeFTP(fail=True);good=FakeFTP()
        with mock.patch.dict(os.environ,{"FTP_HOST":"example.invalid","FTP_USER":"u","FTP_PASSWORD":"p","FTP_PROTOCOL":"ftp"}):
            with mock.patch.object(m.ftplib,"FTP",side_effect=[bad,good]) as maker:
                with mock.patch.object(m.time,"sleep") as sleeper:
                    result=m.connect()
        self.assertIs(result,good)
        self.assertTrue(bad.closed)
        self.assertEqual(maker.call_count,2)
        sleeper.assert_called_once_with(2)
    def test_permanent_login_error_is_not_retried(self):
        class FakeFTP:
            def connect(self,*args):return None
            def login(self,*args):raise m.ftplib.error_perm("530 login denied")
            def close(self):return None
        with mock.patch.dict(os.environ,{"FTP_HOST":"example.invalid","FTP_USER":"u","FTP_PASSWORD":"p","FTP_PROTOCOL":"ftp"}):
            with mock.patch.object(m.ftplib,"FTP",return_value=FakeFTP()) as maker:
                with self.assertRaises(m.ftplib.error_perm):m.connect()
        self.assertEqual(maker.call_count,1)
    def test_folder_occupancy_counts_hidden_files_without_indexing_them(self):
        class FakeFTP:
            def cwd(self,p):self.path=p
            def mlsd(self):
                return iter([(".private",{"type":"file","size":"3"}),
                             ("episode.mkv",{"type":"file","size":"99"})])
        result=m.scan(FakeFTP(),max_depth=0)
        self.assertEqual(result["folders"][0]["entries"],2)
        self.assertEqual(result["folders"][0]["hidden_entries"],1)
        self.assertEqual(result["folders"][0]["hidden_name_samples"],[".private"])
        self.assertEqual(result["folders"][0]["file_entries"],2)
        self.assertEqual(len(result["files"]),1)
    def test_empty_directory_is_explicitly_recorded(self):
        class FakeFTP:
            def cwd(self,p):self.path=p
            def mlsd(self):return iter([])
        result=m.scan(FakeFTP(),max_depth=0)
        self.assertEqual(result["folders"][0]["entries"],0)
    def test_deleted_folder_during_listing_is_recorded_not_crash(self):
        import ftplib
        class FakeFTP:
            def cwd(self,p):self.path=p
            def mlsd(self):
                if self.path=="/downloads":
                    return iter([("just-removed",{"type":"dir"})])
                raise ftplib.error_perm("550 no such file or directory")
        report=m.scan(FakeFTP(),max_seconds=2,max_depth=2)
        self.assertEqual(len(report["failures"]),1)
        self.assertEqual(report["failures"][0]["directory"],"/downloads/just-removed")
        self.assertEqual(report["failures"][0]["error_type"],"error_perm")
    def test_depth_limit_is_reported(self):
        class FakeFTP:
            def cwd(self,p):self.path=p
            def mlsd(self):return iter([("nested",{"type":"dir"})]) if self.path=="/downloads" else iter([])
        result=m.scan(FakeFTP(),max_depth=0)
        self.assertEqual(result["truncated"],["/downloads/nested"])
if __name__=="__main__":unittest.main()
