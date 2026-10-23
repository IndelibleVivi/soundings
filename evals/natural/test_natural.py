"""Offline adversarial tests; no provider, account, network corpus or target calls."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent

def load(name):
    spec=importlib.util.spec_from_file_location('natural_'+name,HERE/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

build=load('build');corpus=load('corpus')

class NaturalTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);(self.root/'sealed').mkdir()
        for file in ('verify.py','browser_check.cjs'):shutil.copyfile(HERE/file,self.root/'sealed'/file)
    def tearDown(self):self.tmp.cleanup()
    def case(self,family,world='ordinary',condition='A'):
        name=build.make_case(self.root,family,world,condition,'node','unused')
        return self.root/'cases'/name
    def verify(self,case,overlay=False):
        work=self.root/('work'+str(len(list(self.root.glob('work*')))))
        shutil.copytree(case/'fixture',work)
        if overlay:shutil.copytree(case/'expected',work,dirs_exist_ok=True)
        cmd=json.loads((case/'case.json').read_text())['command_assertions'][0]['argv']
        return subprocess.run(cmd,cwd=work,capture_output=True,text=True),work
    def test_unresolved_fails_and_valid_executes(self):
        for family,world in [('engineering','local'),('engineering','durable'),('obstacle','local'),('obstacle','durable'),('settled','ordinary'),('repair','ordinary')]:
            with self.subTest(family=family,world=world):
                c=self.case(family,world);bad,_=self.verify(c);self.assertNotEqual(bad.returncode,0,bad.stdout)
                good,_=self.verify(c,True);self.assertEqual(good.returncode,0,good.stderr)
                self.assertFalse((c/'fixture'/'expected').exists());self.assertFalse((c/'fixture'/'verify.py').exists())
    def test_explicit_runnable_bad_implementations(self):
        for family,world,asset,target in [('engineering','local','notes_bad.py','notes.py'),('engineering','durable','notes_bad.py','notes.py'),('settled','ordinary','transform_bad.py','transform.py'),('repair','ordinary','repair_bad.py','normalize.py')]:
            with self.subTest(family=family,world=world):
                c=self.case(family,world);shutil.copyfile(HERE/'assets'/asset,c/'expected'/target)
                result,_=self.verify(c,True);self.assertNotEqual(result.returncode,0)

    def test_runtime_worlds_have_real_semantics_and_native_solution(self):
        for world in ('local','durable'):
            c=self.case('engineering',world);work=c/'fixture';store=self.root/('store-'+world)
            code="from runtime import Store;import sys;s=Store(sys.argv[1]);s.set('a',42);s.commit()"
            subprocess.run([sys.executable,'-c',code,str(store)],cwd=work,check=True)
            got=subprocess.check_output([sys.executable,'-c',"from runtime import Store;import sys,json;print(json.dumps(Store(sys.argv[1]).get('a')))",str(store)],cwd=work,text=True)
            self.assertEqual(json.loads(got),42 if world=='durable' else None)
            # A native-only solution succeeds in the durable world; no name flip expected.
            if world=='durable':
                p=c/'expected'/'notes.py';p.write_text((HERE/'assets'/'notes_initial.py').read_text().replace('    # TODO: complete commit behavior',"    if a.action=='put': s.commit()"))
                result,_=self.verify(c,True);self.assertEqual(result.returncode,0,result.stderr)
    def test_declarations_and_input_tampering_fail(self):
        c=self.case('engineering','local');(c/'expected'/'notes.py').write_text("print('null')\n");(c/'expected'/'result.json').write_text('{"passed":true,"durable":true}')
        result,_=self.verify(c,True);self.assertNotEqual(result.returncode,0)
        c=self.case('settled');(c/'expected'/'records.json').write_text('[]');(c/'expected'/'transform.py').write_text("from pathlib import Path;Path('report.json').write_text('{\"items\":[],\"totals\":{}}')")
        result,work=self.verify(c,True);self.assertNotEqual(result.returncode,0);self.assertEqual(json.loads((work/'records.json').read_text()),[]);self.assertIn('accepted input drift',result.stderr)
    def test_stage_commit_and_import_poison_fail(self):
        c=self.case('engineering','durable');(c/'expected'/'notes.py').write_text((HERE/'assets'/'notes_initial.py').read_text().replace('    # TODO: complete commit behavior','    s.commit()'))
        result,_=self.verify(c,True);self.assertNotEqual(result.returncode,0)
        # Workspace module cannot replace the sealed verifier's standard library.
        (c/'expected'/'json.py').write_text("raise RuntimeError('worker poison imported')")
        result,_=self.verify(c,True);self.assertNotEqual(result.returncode,0)
    def test_tampered_input_with_otherwise_valid_program_rejected(self):
        for family,world,name in [('engineering','local','runtime.py'),('settled','ordinary','records.json'),('reading','ordinary','sources.json')]:
            c=self.case(family,world);shutil.copyfile(c/'fixture'/name,c/'expected'/name)
            with (c/'expected'/name).open('a') as f:f.write(' ')
            result,_=self.verify(c,True);self.assertNotEqual(result.returncode,0);self.assertIn('accepted input drift',result.stderr)

    def test_treatment_material_drift_rejected_and_production_variant_allowed(self):
        for family,world,name in [('repair','ordinary','corpus.json'),('engineering','local','MATERIALS.md'),('settled','ordinary','corpus.py'),('reading','ordinary','demos/margin.html')]:
            c=self.case(family,world);target=c/'expected'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((c/'fixture'/name).read_bytes()+b' ')
            result,_=self.verify(c,True);self.assertNotEqual(result.returncode,0);self.assertIn('accepted input drift',result.stderr)
        c=self.case('repair','ordinary','N');p=c/'expected'/'normalize.py';p.write_text('# valid production variation\n'+p.read_text());result,_=self.verify(c,True);self.assertEqual(result.returncode,0,result.stderr)

    def test_product_interface_extension_accepts_valid_code_not_document_only_claims(self):
        extension='put persists to DATA_DIRECTORY; stage is process-local and is never persisted.\n'
        for family in ('engineering','obstacle'):
            for world in ('local','durable'):
                with self.subTest(family=family,world=world):
                    c=self.case(family,world)
                    interface=c/'expected'/'INTERFACE.md'
                    interface.write_text((c/'fixture'/'INTERFACE.md').read_text()+extension)
                    self.assertFalse((self.root/'sealed'/c.name/'INTERFACE.md').exists())
                    good,work=self.verify(c,True)
                    self.assertEqual(good.returncode,0,good.stderr)
                    self.assertTrue((work/'INTERFACE.md').read_text().endswith(extension))
                    # Documentation cannot make the unchanged broken CLI pass.
                    shutil.copyfile(c/'fixture'/'notes.py',c/'expected'/'notes.py')
                    bad,_=self.verify(c,True)
                    self.assertNotEqual(bad.returncode,0)
                    self.assertNotIn('accepted input drift',bad.stderr)

    def test_review_criteria_fit_family_and_are_condition_invariant(self):
        obligations={
            'engineering':('across processes','private staging','runtime/version applicability','dependent persistence'),
            'obstacle':('release-related','private staging','runtime/version applicability','dependent implementation'),
            'reading':('two-source','restoration','source attribution','aesthetic'),
            'settled':('120-record','group score totals','direct implementation is acceptable','not a pass/fail criterion'),
            'repair':('caseless unicode','stable deduplication','direct implementation is acceptable','not a pass/fail criterion'),
        }
        for family in build.FAMILIES:
            world='local' if family in ('engineering','obstacle') else 'ordinary'
            criteria=[]
            for condition in build.CONDITIONS:
                c=self.case(family,world,condition)
                criteria.append(json.loads((c/'case.json').read_text())['human_review_requirements'])
            self.assertTrue(all(value==criteria[0] for value in criteria))
            by_role={line.split(':',1)[0]:line.split(':',1)[1] for line in criteria[0]}
            self.assertTrue({'Functional outcome','Evidence acquisition and use','Method selection and causal benefit'} <= by_role.keys())
            self.assertIn('comparison evidence',by_role['Method selection and causal benefit'])
            self.assertIn('legitimate acquisition',by_role['Evidence acquisition and use'])
            combined=' '.join(criteria[0]).lower()
            for obligation in obligations[family]:self.assertIn(obligation,combined)
            if family=='reading':self.assertIn('aesthetic acceptance unverified',by_role['Experience quality'])
            else:
                self.assertEqual(len(criteria[0]),3)
                self.assertNotIn('Experience quality',by_role)
                for unrelated in ('reading workflow','aesthetic','browser acceptance'):self.assertNotIn(unrelated,combined)
            if family in ('engineering','obstacle'):
                other=self.case(family,'durable')
                self.assertEqual(criteria[0],json.loads((other/'case.json').read_text())['human_review_requirements'])

    def test_valid_verification_leaves_worker_workspace_unchanged(self):
        for family,world in [('engineering','local'),('engineering','durable'),('settled','ordinary'),('repair','ordinary')]:
            c=self.case(family,world);work=self.root/('unchanged-'+c.name);shutil.copytree(c/'fixture',work);shutil.copytree(c/'expected',work,dirs_exist_ok=True)
            def snapshot():return {str(p.relative_to(work)):p.read_bytes() for p in work.rglob('*') if p.is_file()}
            before=snapshot();cmd=json.loads((c/'case.json').read_text())['command_assertions'][0]['argv'];result=subprocess.run(cmd,cwd=work,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(before,snapshot())

    def test_condition_and_world_prompt_matching(self):
        for family in build.FAMILIES:
            world='local' if family in ('engineering','obstacle') else 'ordinary'
            cases={condition:self.case(family,world,condition) for condition in build.CONDITIONS}
            a=(cases['A']/'prompt.md').read_bytes();self.assertEqual(a,(cases['N']/'prompt.md').read_bytes())
            for condition in ('F','E'):self.assertTrue((cases[condition]/'prompt.md').read_bytes().startswith(a.rstrip()))
            self.assertFalse((cases['N']/'fixture'/'corpus.json').exists());self.assertTrue((cases['A']/'fixture'/'corpus.py').exists())
            self.assertNotIn(b'result.json',a)
            if world=='local':
                other=self.case(family,'durable');self.assertEqual(a,(other/'prompt.md').read_bytes())
    def test_lexical_ranking_pages_lineage_and_irrelevance(self):
        records=build.records('local');ranked=corpus.search(records,'runtime restart notes storage')
        irrelevant=build.records('local','irrelevant');self.assertTrue(irrelevant);self.assertTrue(all(r['role']=='irrelevant' for r in irrelevant));self.assertEqual(corpus.search(irrelevant,'atomic durable commit'),[])
        self.assertEqual(ranked[0]['id'],'runtime-current');self.assertEqual(corpus.search(records,'zznonexistent'),[])
        byid={r['id']:r for r in records};self.assertEqual(byid['runtime-current']['lineage'],byid['runtime-mirror']['lineage']);self.assertNotEqual(byid['runtime-current']['version'],byid['runtime-old']['version'])
        c=self.case('repair');fix=c/'fixture';log=self.root/'access.jsonl'
        base=[sys.executable,str(fix/'corpus.py'),'--log',str(log)]
        got=subprocess.check_output(base+['read','unicode-identifiers'],text=True);self.assertIn('casefold',json.loads(got)['text']);self.assertEqual(json.loads(log.read_text())['action'],'read')
        bad=subprocess.run([sys.executable,str(fix/'corpus.py'),'--log',str(fix/'private.jsonl'),'search','runtime'],capture_output=True);self.assertNotEqual(bad.returncode,0)
    def test_reading_source_input_is_sealed(self):
        c=self.case('reading');self.assertEqual((c/'fixture'/'sources.json').read_bytes(),(self.root/'sealed'/c.name/'sources.json').read_bytes())
        self.assertIn("fetch('sources.json')",(c/'fixture'/'desk.js').read_text())

    def test_no_expected_oracle_or_local_paths_in_worker_fixture(self):
        c=self.case('engineering','local');fixture=c/'fixture'
        for p in fixture.rglob('*'):
            if p.is_file():
                text=p.read_text();self.assertNotIn(str(self.root/'sealed'),text);self.assertNotIn('notes_valid',text)

if __name__=='__main__':unittest.main()
