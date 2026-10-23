#!/usr/bin/env python3
"""Offline path and episode-matching smoke checks."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from ftp_video_metadata import PATTERN
from ftp_research_intake import clean_path

class Tests(unittest.TestCase):
    def test_filename(self):
        self.assertEqual(PATTERN.search('Night.Court.S02E20.mkv').groups()[:2], ('2','20'))
        self.assertEqual(PATTERN.search('S07E24.avi').groups()[:2], ('7','24'))
        self.assertEqual(PATTERN.search('Night Court - 1x01 - All You Need Is Love.avi').groups()[2:], ('1','1'))
        self.assertEqual(PATTERN.search('Night Court - 9x22 - The 1992 Boat Show.avi').groups()[2:], ('9','22'))
    def test_path(self):
        self.assertEqual(clean_path('/downloads/Night Court TVRip S1-S9'),'/downloads/Night Court TVRip S1-S9')
        with self.assertRaises(ValueError):clean_path('/downloads/../private')

if __name__=='__main__': unittest.main()
