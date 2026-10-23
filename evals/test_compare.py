"""Constructed comparison records; no target invocation or installed Field Lab needed."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import compare as subject


def canonical(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.execution=dict(selection_mode='explicit',requested_model='constructed',requested_reasoning_effort='low',approval_policy='never',network_access=False,timeout_override_seconds=None,keep_workspace=False)
        self.case=dict(sandbox='read-only',timeout_seconds=30,human_review_requirements=['assess'])
        self.inputs={'case_sha256':canonical(self.case)}
        self.plan=dict(run_id='run',lab_id='lab',plan_sha256='pin',mode='canary',repeat=2,execution=self.execution,planned_inputs=dict(subjects={'subject':{}},cases={'case':self.inputs},fieldlab_source_sha256='source',manifest={}),matrix=[dict(subject_id='subject',case_id='case',repeat=n) for n in (1,2)])
        identity=dict(plan_sha256='pin',subjects={'subject':{}},cases={'case':self.inputs},fieldlab_source_sha256='source',manifest={'lab_id':'lab'},execution=self.execution,mode='canary',repeat=2)
        identity['identity_sha256']=canonical(identity)
        self.identity=identity
        self.planpath=self.write('plan.json',self.plan)
        self.summary=self.write('summary.json',dict(run_id='run',identity=identity))
        self.patcher=patch.object(subject,'native',return_value=(lambda p:None,self.artifacts,canonical));self.patcher.start();self.addCleanup(self.patcher.stop)
    def write(self,name,obj):
        path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(obj));return path
    def artifacts(self,path,r):
        return dict(intact=[],missing=[],unverifiable=[],drifted=[n for n,e in r['artifacts'].items() if subject.sha(path.parent/n)!=e['sha256']])
    def receipt(self,repeat=1,attempt='attempt-001'):
        name=f'{repeat}/{attempt}'
        execution={k:self.execution[k] for k in ('selection_mode','requested_model','requested_reasoning_effort','approval_policy','network_access')};execution.update(sandbox=self.case['sandbox'],timeout_seconds=self.case['timeout_seconds'])
        r=dict(subject_delivery={'status':'verified'},host_selection={'status':'unknown'},content_application={'status':'requires-semantic-review'},schema_version=2,receipt_type='attempt',run_id='run',lab_id='lab',subject_id='subject',case_id='case',attempt_id=attempt,identity_sha256=self.identity['identity_sha256'],inputs=self.inputs,outcome='pass',target_agent_invocations=1,selection=dict(mode='explicit',requested_model='constructed',requested_reasoning_effort='low',actual_model_claimed=False),execution_boundary=dict(sandbox='read-only',approval_policy='never',network_access=False,target_started=True,quiescent=True),verification_summary=dict(passed=True,human_review=dict(required=True,requirements=['assess'])))
        m={**r,'repeat':repeat,'execution':execution,'state':'completed','process':{'quiescent':True}}
        metadata=self.write(name+'/metadata.json',m);case=self.write(name+'/case.json',self.case)
        r['artifacts']={p.name:dict(sha256=subject.sha(p),bytes=p.stat().st_size) for p in (metadata,case)}
        return self.write(name+'/receipt.json',r)
    def compare(self,receipts,reviews=()):
        return subject.compare(receipts,reviews,[self.planpath],self.root,[self.summary])
    def test_missing_and_pending(self):
        result=self.compare([self.receipt()]);self.assertFalse(result['errors']);self.assertEqual(len(result['missing_planned_rows']),1);self.assertEqual(result['attempts'][0]['semantic_review'],'pending')
    def test_valid_repeated_attempt_names(self):
        result=self.compare([self.receipt(1),self.receipt(2)]);self.assertFalse(result['errors']);self.assertFalse(result['missing_planned_rows'])
    def test_timestamp_duplicate(self):
        p=self.receipt();r=subject.read(p);r['created_at']='later';other=self.write('1/attempt-001/other.json',r)
        result=self.compare([p,other]);self.assertIn('duplicate logical',str(result['errors']));self.assertEqual(len(result['attempts']),1)
    def test_retry_needs_adjudication(self):
        result=self.compare([self.receipt(),self.receipt(attempt='attempt-002')]);self.assertEqual(result['planned_rows'][0]['status'],'retry-adjudication-required')
    def test_drift(self):
        p=self.receipt();(p.parent/'metadata.json').write_text('{}');self.assertTrue(self.compare([p])['errors'])
    def test_omitted_review_requirements(self):
        p=self.receipt();r=subject.read(p);r['verification_summary']['human_review']={'required':False,'requirements':[]};p.write_text(json.dumps(r))
        result=self.compare([p]);self.assertIn('differ from sealed case',str(result['errors']));self.assertFalse(result['attempts'])
    def test_missing_summary(self):
        result=subject.compare([],[],[self.planpath],self.root,[self.write('bad-summary.json',{})])
        self.assertIn('no validated summary',str(result['errors']))
    def test_pass_without_process(self):
        p=self.receipt();m=subject.read(p.parent/'metadata.json');m['process']=None;(p.parent/'metadata.json').write_text(json.dumps(m));r=subject.read(p);r['artifacts']['metadata.json']={'sha256':subject.sha(p.parent/'metadata.json'),'bytes':(p.parent/'metadata.json').stat().st_size};p.write_text(json.dumps(r))
        self.assertIn('process metadata',str(self.compare([p])['errors']))
    def test_summary_drift(self):
        p=self.receipt();s=subject.read(self.summary);s['identity']['plan_sha256']='bad';self.write('summary.json',s);self.assertTrue(self.compare([p])['errors'])
    def test_unbound_plan(self):
        p=self.receipt();s=subject.read(self.summary);s['identity']['plan_sha256']='bad';body=dict(s['identity']);body.pop('identity_sha256');s['identity']['identity_sha256']=canonical(body);self.write('summary.json',s);self.assertIn('unbound plan',str(self.compare([p])['errors']))
    def test_review_binding(self):
        p=self.receipt();r=dict(schema_version=2,method='human',review_id='review',created_at='today',rationale='assessed',independence='implementer-run',judgment='supported',requirement_outcomes={'assess':'supported'},receipt=dict(path=str(p),sha256=subject.sha(p)))
        review=self.write('review.json',r);result=self.compare([p],[review]);self.assertFalse(result['errors']);self.assertEqual(result['attempts'][0]['reviews'][0]['independence'],'implementer-run')
        r['requirement_outcomes']={'wrong':'supported'};self.write('review.json',r);self.assertTrue(self.compare([p],[review])['errors'])
        r['receipt']['sha256']='stale';self.write('review.json',r);self.assertIn('stale',str(self.compare([p],[review])['errors']))

if __name__=='__main__':unittest.main()

class NativeOfflineIntegration(unittest.TestCase):
    @unittest.skipUnless(__import__('os').environ.get('FIELDLAB_SOURCE'), 'optional explicit Field Lab checkout')
    def test_native_plan_and_receipt(self):
        import os
        root=Path(os.environ['FIELDLAB_SOURCE']).resolve()
        validate,report,digest=subject.native(root)
        from fieldlab.plan import build_plan
        from fieldlab.receipts import synthetic_receipt
        from fieldlab.runner import _run_identity, _effective_execution
        from fieldlab.contracts import load_lab, load_cases
        import importlib.util
        spec=importlib.util.spec_from_file_location('constructed_lab',root/'tests/test_v2_runner.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);manifest=module.create_lab(base)
            p=build_plan(manifest_path=manifest,subject_ids=['isolated-control'],case_ids=['authority-boundary'],mode='canary',repeat=2,model='offline-unused',reasoning_effort='low',codex_bin='missing-offline-binary',run_id='offline',output_root=None,timeout_override=None,keep_workspace=False)
            validate(p)
            lab,lr,cr=load_lab(manifest);cases=load_cases(cr)
            identity=_run_identity(plan=p,lab=lab,lab_root=lr,cases=cases,adapter_identity={})
            case=cases['authority-boundary'][1];execution=_effective_execution(p,case)
            attempt=base/'attempt-001';attempt.mkdir()
            inputs=p['planned_inputs']['cases']['authority-boundary']
            m=dict(schema_version=2,state='preflight-failed',outcome='preflight-failed',run_id='offline',lab_id=lab['lab_id'],case_id='authority-boundary',subject_id='isolated-control',attempt_id='attempt-001',identity_sha256=identity['identity_sha256'],repeat=1,inputs=inputs,execution=execution,target_agent_invocations=0)
            (attempt/'metadata.json').write_text(json.dumps(m));(attempt/'case.json').write_text(json.dumps(case))
            r=synthetic_receipt(run_id='offline',attempt_id='attempt-001',lab_id=lab['lab_id'],case_id='authority-boundary',claim_ids=[],subject_id='isolated-control',subject=lab['subjects']['isolated-control'],mode='canary',comparison_capable=True,identity_sha256=identity['identity_sha256'],input_identity=inputs,execution=execution,process=None,outcome='preflight-failed',verification={},attempt_dir=attempt)
            rp=attempt/'receipt.json';rp.write_text(json.dumps(r))
            pp=base/'plan.json';pp.write_text(json.dumps(p));sp=base/'summary.json';sp.write_text(json.dumps(dict(run_id='offline',identity=identity)))
            result=subject.compare([rp],[],[pp],root,[sp])
            self.assertFalse(result['errors'],result)
            self.assertEqual(result['planned_rows'][0]['status'],'known-no-invocation')
            # Native constructed completed invocation: no executable is launched.
            process=dict(quiescent=True,termination_reason='exited',orphan_descendants=False)
            m.update(state='completed',outcome='pass',target_agent_invocations=1,process=process)
            (attempt/'metadata.json').write_text(json.dumps(m))
            r=synthetic_receipt(run_id='offline',attempt_id='attempt-001',lab_id=lab['lab_id'],case_id='authority-boundary',claim_ids=[],subject_id='isolated-control',subject=lab['subjects']['isolated-control'],mode='canary',comparison_capable=True,identity_sha256=identity['identity_sha256'],input_identity=inputs,execution=execution,process=process,outcome='pass',verification={'passed':True,'human_review_requirements':case.get('human_review_requirements',[])},attempt_dir=attempt)
            rp.write_text(json.dumps(r))
            result=subject.compare([rp],[],[pp],root,[sp])
            self.assertFalse(result['errors'],result)
            self.assertEqual(result['planned_rows'][0]['status'],'observed')
