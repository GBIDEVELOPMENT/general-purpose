"""Ensure large catalog is accessed selectively; does not grade agent choices."""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT=Path(__file__).resolve().parents[1]/'scripts/procedure_lookup.py'
spec=importlib.util.spec_from_file_location('procedure_lookup', SCRIPT)
mod=importlib.util.module_from_spec(spec)
sys.modules['procedure_lookup']=mod
spec.loader.exec_module(mod)

class ProcedureLookupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.item={'id':'PROC-001','title':'Investigate requirement','trigger':'User states are undefined',
                  'exclude':'The spec already defines the states','source_pattern_id':'PRX-001',
                  'steps':[{'op':'inspect'}], 'oracle':'Visible result test','stop':'Stop once choice resolved'}
        cls.other=dict(cls.item,id='PROC-002',title='Inspect architecture')
        cls.data={'schema':'mechanised-expertise/source-mechanisms-v1',
                  'procedures':[cls.item,cls.other]}

    def test_list_excludes_full_operations(self):
        s=mod.select({'PROC-001':self.item,'PROC-002':self.other})
        self.assertIn('PROC-001',s)
        self.assertIn('User states are undefined',s)
        self.assertNotIn('"steps"',s)
        self.assertIn('NOT automatic diagnoses',s)

    def test_one_id_does_not_load_other_technical_text(self):
        s=mod.select({'PROC-001':self.item,'PROC-002':self.other},'PROC-001')
        self.assertIn('"steps"',s)
        self.assertNotIn('Inspect architecture',s)

    def test_unknown_id_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'Unknown procedure'):
            mod.select({'PROC-001':self.item},'PROC-999')

    def test_declared_schema_and_duplicate_gate(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'catalog.json'
            path.write_text(json.dumps(self.data))
            self.assertEqual(len(mod.read_catalog(path)),2)
            broken=dict(self.data,procedures=[self.item,self.item])
            path.write_text(json.dumps(broken))
            with self.assertRaisesRegex(ValueError,'duplicate'):
                mod.read_catalog(path)

    def test_malformed_input_fails(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'catalog.json'
            path.write_text('{"schema":"wrong","procedures":[]}')
            with self.assertRaisesRegex(ValueError,'schema'):
                mod.read_catalog(path)

    def test_full_checkout_catalog_and_compactness(self):
        catalog=SCRIPT.parents[1]/'assets/source-mechanisms-v1.json'
        if not catalog.is_file():
            self.skipTest('Only runs from complete repository checkout')
        recipes=mod.read_catalog(catalog)
        self.assertEqual(len(recipes),30)
        text=mod.select(recipes)
        self.assertLess(len(text.encode('utf-8')), 17000)
        self.assertLess(len(mod.select(recipes,'PROC-005')),len(catalog.read_text()))

if __name__=='__main__':
    unittest.main()