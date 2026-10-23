import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pack import classify_cases, snapshot, verify_references
ROOT=Path(__file__).parent
FIELDLAB_VALUE=os.environ.get('FIELDLAB_SOURCE')
FIELDLAB=Path(FIELDLAB_VALUE).resolve() if FIELDLAB_VALUE else None

def fieldlab_modules():
    if FIELDLAB is None: raise unittest.SkipTest('optional explicit Field Lab checkout')
    if str(FIELDLAB) not in sys.path:
        sys.path.insert(0,str(FIELDLAB))
    from fieldlab.contracts import load_case
    from fieldlab.verify import evaluate_command_assertion,evaluate_workspace_assertions
    from fieldlab.workspace import copy_workspace,prepare_workspace
    return load_case,evaluate_command_assertion,evaluate_workspace_assertions,copy_workspace,prepare_workspace

def exercise(case_dir,result,replacements=None,extra_files=None):
    load_case,evaluate_command_assertion,evaluate_workspace_assertions,copy_workspace,prepare_workspace=fieldlab_modules()
    case=load_case(case_dir)
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp); workspace=root/'workspace'
        prepare_workspace(case_dir=case_dir,subject={'kind':'control'},lab_root=root,workspace=workspace)
        (workspace/'result.json').write_text(json.dumps(result,sort_keys=True,indent=4))
        for relative,text in (replacements or {}).items():
            target=workspace/relative
            if text is None: target.unlink()
            else: target.write_text(text)
        for relative,text in (extra_files or {}).items():
            target=workspace/relative; target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text(text)
        workspace_results=evaluate_workspace_assertions(case,workspace,root/'workspace-artifacts')
        command_results=[]
        for index,assertion in enumerate(case['command_assertions']):
            copy=root/'verifier-copy'/f'command-{index:03d}'
            copy_workspace(workspace,copy)
            command_results.append(evaluate_command_assertion(assertion,copy,root/'command-artifacts',index))
        return workspace_results,command_results

def passed(results):
    return all(result['passed'] for result in results)

def write_json(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2)+'\n')

def write_fake_codex(path,body):
    script=textwrap.dedent('''\
        #!/usr/bin/env python3
        import json,sys
        from pathlib import Path
        if '--version' in sys.argv:
            print('codex-cli soundings-pack-fake')
            raise SystemExit(0)
        workspace=Path(sys.argv[sys.argv.index('-C')+1])
    ''')+textwrap.dedent(body)+textwrap.dedent('''\
        for event in [
            {'type':'thread.started','thread_id':'soundings-pack-fake'},
            {'type':'turn.started'},
            {'type':'item.completed','item':{'id':'m','type':'agent_message','text':'done'}},
            {'type':'turn.completed','usage':{'input_tokens':1,'output_tokens':1}},
        ]: print(json.dumps(event),flush=True)
    ''')
    path.write_text(script);path.chmod(0o755)

def runner_receipt(case_id,body,case_dir=None):
    if FIELDLAB is None: raise unittest.SkipTest('optional explicit Field Lab checkout')
    if str(FIELDLAB) not in sys.path: sys.path.insert(0,str(FIELDLAB))
    from fieldlab.io import atomic_write_json,read_json
    from fieldlab.plan import build_plan
    from fieldlab.runner import run_plan
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp); lab=root/'lab'; source=case_dir or ROOT/'cases'/case_id
        shutil.copytree(source,lab/'cases'/case_id)
        write_json(lab/'fieldlab.json',{'schema_version':2,'lab_id':'soundings-runner-probe','description':'Offline fake-adapter runner probe.','cases_root':'cases','subjects':{'isolated-control':{'kind':'control'}},'defaults':{'adapter':'codex-exec','approval_policy':'never','network_access':False,'output_root':'runs','keep_workspace':False}})
        fake=root/'fake-codex';write_fake_codex(fake,body)
        plan=build_plan(manifest_path=lab/'fieldlab.json',subject_ids=['isolated-control'],case_ids=[case_id],mode='canary',repeat=1,model='gpt-6.1-sol',reasoning_effort='high',codex_bin=str(fake),run_id='offline-probe',output_root=str(root/'runs'),timeout_override=10,keep_workspace=False)
        atomic_write_json(root/'plan.json',plan)
        code=run_plan(root/'plan.json',live=True,max_invocations=1,resume=False)
        attempt=next((root/'runs/offline-probe').glob('**/attempt-001'))
        return code,read_json(attempt/'receipt.json'),read_json(attempt/'verification.json')

class PackTests(unittest.TestCase):
    def test_fake_adapter_runner_path_rejects_tampered_settled_work(self):
        original=(ROOT/'cases/settled-work/fixture/records.json').read_text()
        empty='{"records":[],"counts":{"Search":0,"Study":0,"Shape":0}}\n'
        body=textwrap.dedent(f'''\
            (workspace/'records.json').write_text('[]')
            (workspace/'result.json').write_text({empty!r})
        ''')
        code,receipt,verification=runner_receipt('settled-work',body)
        self.assertEqual(code,1)
        self.assertEqual(receipt['outcome'],'fail')
        self.assertFalse(receipt['verification_summary']['worker_completion_supported'])
        self.assertEqual(receipt['verification_summary']['changed_files'],['records.json','result.json'])
        self.assertFalse(verification['command_assertions'][0]['passed'])
        self.assertEqual((ROOT/'cases/settled-work/fixture/records.json').read_text(),original)

    def test_fake_adapter_runner_path_accepts_correct_result(self):
        expected=(ROOT/'cases/direct-repair/expected/result.json').read_text()
        body=textwrap.dedent(f'''\
            (workspace/'result.json').write_text({expected!r})
        ''')
        code,receipt,verification=runner_receipt('direct-repair',body)
        self.assertEqual(code,0)
        self.assertEqual(receipt['outcome'],'pass')
        self.assertTrue(receipt['verification_summary']['worker_completion_supported'])
        self.assertEqual(receipt['verification_summary']['changed_files'],['result.json'])
        self.assertTrue(all(item['passed'] for item in verification['command_assertions']))

    def test_settled_original_input_is_unchanged(self):
        original=(ROOT/'cases/settled-work/fixture/records.json').read_text()
        command=json.loads((ROOT/'cases/settled-work/case.json').read_text())['command_assertions'][0]['argv'][-1]
        self.assertIn('4c4938b43e0f61785107f27f13f11332e58afabb987136f9f8648301ce04feff',command)
        self.assertEqual(len(json.loads(original)),90)
        self.assertEqual(len(json.loads((ROOT/'cases/settled-work/expected/result.json').read_text())['records']),72)

    def test_materialized_cases_are_labeled_guided_probes(self):
        import pack
        with tempfile.TemporaryDirectory() as tmp:
            cases=Path(tmp)/'cases'
            shutil.copytree(ROOT/'cases',cases)
            self.assertEqual(pack.case_names(cases),{'creative-transfer','direct-repair','engineering-choice','settled-work'})
            classify_cases(cases)
            for case in cases.iterdir():
                self.assertIn('guided-mechanism-probe',json.loads((case/'case.json').read_text())['tags'])
            self.assertNotIn('guided-mechanism-probe',json.loads((ROOT/'cases/creative-transfer/case.json').read_text()).get('tags',[]))

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
                if case.name=='settled-work':
                    (work/'records.json').write_text('[]')
                    (work/'result.json').write_text('{"records":[],"counts":{"Search":0,"Study":0,"Shape":0}}')
                    self.assertNotEqual(subprocess.run(command,cwd=work).returncode,0)
                if case.name=='direct-repair':
                    (work/'result.json').write_text('{"status":"wrong","count":4}')
                    (work/'json.py').write_text('def load(_): return {"status":"ready","count":3}')
                    self.assertNotEqual(subprocess.run(command,cwd=work).returncode,0)
            self.assertFalse((case/'fixture/negative.json').exists())
            self.assertFalse((case/'fixture/expected').exists())
    def test_settled_workspace_and_command_reject_input_tampering(self):
        case_dir=ROOT/'cases/settled-work'
        expected=json.loads((case_dir/'expected/result.json').read_text())
        original=(case_dir/'fixture/records.json').read_text()
        workspace,commands=exercise(case_dir,expected)
        self.assertTrue(passed(workspace),workspace)
        self.assertTrue(passed(commands),commands)
        for replacement in ({'records.json':'[]'},{'records.json':original.replace('"id": 1,','"id": 1001,')}):
            workspace,commands=exercise(case_dir,expected,replacement)
            self.assertFalse(passed(commands),replacement)
        workspace,commands=exercise(case_dir,expected,{'records.json':None})
        self.assertFalse(passed(commands))
        workspace,commands=exercise(case_dir,expected,extra_files={'collateral.txt':'added\n'})
        self.assertFalse(passed(workspace))
        self.assertTrue(passed(commands))
    def test_commands_use_isolated_python_and_evaluator_values(self):
        for case_dir in sorted((ROOT/'cases').iterdir()):
            expected=json.loads((case_dir/'expected/result.json').read_text())
            workspace,commands=exercise(case_dir,expected)
            self.assertTrue(passed(workspace+commands),case_dir.name)
            if case_dir.name=='creative-transfer':
                for form in ('cards','map','list'):
                    variant=dict(expected,form=form,rationale='A distinct local rationale keeps orientation while revealing details.')
                    workspace,commands=exercise(case_dir,variant)
                    self.assertTrue(passed(workspace+commands),(case_dir.name,form,workspace,commands))
                reordered=dict(reversed(list(expected.items())))
                workspace,commands=exercise(case_dir,reordered)
                self.assertTrue(passed(workspace+commands),'JSON key order and creative details should remain flexible')
            baseline=json.loads(json.dumps(expected))
            if case_dir.name=='direct-repair': baseline.update(status='wrong',count=4)
            elif case_dir.name=='engineering-choice': baseline.update(route='shared-disk')
            elif case_dir.name=='creative-transfer': baseline.update(analytics='cloud')
            else: baseline['records']=baseline['records'][:1]
            workspace,commands=exercise(case_dir,baseline,extra_files={'json.py':'def load(_): return '+repr(expected)})
            self.assertFalse(passed(workspace),case_dir.name)
            self.assertFalse(passed(commands),(case_dir.name,'workspace module must not override isolated verifier import'))
            workspace,commands=exercise(case_dir,baseline,extra_files={'json.py':'raise RuntimeError("shadow imported")\n'})
            self.assertFalse(passed(commands),case_dir.name)
            negative=json.loads((case_dir/'negative.json').read_text())
            for name,value in negative.items():
                workspace,commands=exercise(case_dir,value)
                self.assertFalse(passed(workspace+commands),(case_dir.name,name))
    def test_workspace_rejects_added_tests_and_wrong_answers(self):
        for case_dir in sorted((ROOT/'cases').iterdir()):
            expected=json.loads((case_dir/'expected/result.json').read_text())
            for relative,text in (("check.py",'raise SystemExit(0)\n'),("unexpected.py",'pass\n'),(".hidden",'pass\n')):
                workspace,commands=exercise(case_dir,expected,extra_files={relative:text})
                self.assertFalse(passed(workspace),(case_dir.name,relative))
                self.assertTrue(passed(commands),(case_dir.name,relative))
            wrong={}
            workspace,commands=exercise(case_dir,wrong)
            self.assertFalse(passed(commands),case_dir.name)
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
