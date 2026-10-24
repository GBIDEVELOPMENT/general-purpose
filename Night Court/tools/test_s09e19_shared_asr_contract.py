#!/usr/bin/env python3
"""Static API-shape drift guard for expensive private original-source recognizers."""
import ast
from pathlib import Path
import unittest

TOOLS=Path(__file__).resolve().parent


def function_ast(filename,name):
    tree=ast.parse((TOOLS/filename).read_text('utf-8'))
    return next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name==name)


def shared_returns(filename,fn):
    node=function_ast(filename,fn)
    return next(x.value for x in reversed(node.body) if isinstance(x,ast.Return))


def unpack_count_from_profile(fn_name):
    tree=function_ast('profile_s09e19_source_once_factory.py','profile')
    for node in ast.walk(tree):
        if isinstance(node,ast.Assign) and isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Name) and node.value.func.id==fn_name:
            return len(node.targets[0].elts)
    raise AssertionError('Missing shared original-source ASR decoder call')


class SourceDecoderDrift(unittest.TestCase):
    def test_s09_original_episode_uses_exact_current_shared_decoder_return_contract(self):
        for name,length in (('vosk_free_decode',3),('whisper_free_decode',4)):
            with self.subTest(fn=name):
                shared=shared_returns('probe_s01e01_full_dual_asr.py',name)
                self.assertIsInstance(shared,ast.Tuple)
                self.assertEqual(len(shared.elts),length)
                self.assertEqual(unpack_count_from_profile(name),length)

    def test_rejection_reasons_are_preserved_and_unverified(self):
        content=(TOOLS/'profile_s09e19_source_once_factory.py').read_text('utf-8')
        self.assertIn("'model_rejection_reasons':{'whisper':whisper_reasons,'vosk':vosk_reasons}",content)
        self.assertIn("'source_untimed_paragraph_timestamps_created':False",content)
        self.assertIn("'episode_production_script_accepted':False",content)


if __name__=='__main__':
    unittest.main()
