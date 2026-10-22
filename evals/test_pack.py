import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from pack import snapshot, verify_references
ROOT=Path(__file__).parent
class PackTests(unittest.TestCase):
    def test_semantic_counterexamples(self):
        for case in (ROOT/'cases').iterdir():
            spec=json.loads((case/'case.json').read_text())
            command=spec['command_assertions'][0]['argv']
            good=json.loads((case/'expected/result.json').read_text())
            bad=json.loads((case/'negative.json').read_text())
            with tempfile.TemporaryDirectory() as tmp:
                work=Path(tmp)/'work'; shutil.copytree(case/'fixture',work)
                for value,accepted in [(good,True),*[(v,False) for v in bad.values()]]:
                    (work/'result.json').write_text(json.dumps(value,sort_keys=True,indent=4))
                    result=subprocess.run(command,cwd=work,capture_output=True)
                    self.assertEqual(result.returncode==0,accepted,(case.name,value,result.stderr))
                if case.name=='creative-transfer':
                    for form in ['map','list','cards']:
                        (work/'result.json').write_text(json.dumps(dict(good,form=form)))
                        self.assertEqual(subprocess.run(command,cwd=work).returncode,0)
            self.assertFalse((case/'fixture/negative.json').exists())
            self.assertFalse((case/'fixture/expected').exists())
    def test_sealed_review_paths(self):
        for case in (ROOT/'cases').iterdir():
            spec=json.loads((case/'case.json').read_text())
            with tempfile.TemporaryDirectory() as tmp:
                work=Path(tmp)/'work'
                shutil.copytree(case/'fixture',work)
                shutil.copytree(case/'expected',work,dirs_exist_ok=True)
                for relative in spec['human_review_material']:
                    path=work/relative
                    self.assertTrue(path.resolve().is_relative_to(work.resolve()))
                    self.assertTrue(path.is_file(), (case.name,relative))
            prompt=(case/'prompt.md').read_text()
            self.assertNotIn('page reference',prompt)
            if case.name in ('direct-repair','settled-work'):
                self.assertNotIn('lookup.py',prompt)
            self.assertNotIn('Inspect local evidence before deciding',prompt)
        rubrics=[tuple(json.loads((case/'case.json').read_text())['human_review_requirements']) for case in (ROOT/'cases').iterdir()]
        self.assertEqual(len(set(rubrics)),4)

    def test_invalid_ref(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(subprocess.CalledProcessError): snapshot(ROOT.parent,'not-a-real-ref','plugins/soundings/skills',Path(tmp))
    def test_broken_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); s=root/'skills/example';s.mkdir(parents=True)
            (s/'SKILL.md').write_text('[missing](../../references/missing.md)')
            with self.assertRaises(ValueError):verify_references(root)
    def test_second_hop_reference_is_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); s=root/'skills/example';s.mkdir(parents=True)
            refs=root/'references'; refs.mkdir()
            (s/'SKILL.md').write_text('[first](../../references/a.md)')
            (refs/'a.md').write_text('[second](missing.md)')
            with self.assertRaises(ValueError):verify_references(root)
if __name__=='__main__': unittest.main()
