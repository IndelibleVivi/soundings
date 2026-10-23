"""Descriptive comparison of explicitly pinned Field Lab runs; never a runner."""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import sys


def read(path):
    value = json.loads(Path(path).read_text())
    if not isinstance(value, dict):
        raise ValueError('JSON object required')
    return value


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check(condition, message):
    if not condition:
        raise ValueError(message)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def native(root):
    root = Path(root).resolve()
    sys.path.insert(0, str(root))
    module = importlib.import_module('fieldlab.plan')
    check(Path(module.__file__).resolve().parent.parent == root, 'Field Lab import source mismatch')
    from fieldlab.explain import _artifact_report
    from fieldlab.io import canonical_json, sha256_text
    return module.validate_plan, _artifact_report, lambda obj: sha256_text(canonical_json(obj))


def compare(receipt_paths, review_paths=(), plan_paths=(), fieldlab_root=None, summary_paths=()):
    check(fieldlab_root is not None and plan_paths and summary_paths,
          'explicit Field Lab root, pinned plans and run summaries required')
    validate, artifact_report, canonical_digest = native(fieldlab_root)
    errors, plans, identities, expected, rows = [], {}, {}, {}, []
    def error(path, exc):
        errors.append({'path': str(path), 'error': str(exc)})
    for path in plan_paths:
        try:
            p = read(path); validate(p)
            check(p['run_id'] not in plans, 'duplicate plan run_id')
            plans[p['run_id']] = p
            for item in p['matrix']:
                expected[(p['run_id'], item['subject_id'], item['case_id'], item['repeat'])] = []
        except Exception as exc:
            error(path, exc)
    for path in summary_paths:
        try:
            s = read(path); identity = s['identity']; body = dict(identity)
            digest = body.pop('identity_sha256')
            check(canonical_digest(body) == digest, 'summary identity digest mismatch')
            runtime = identity.get('runtime')
            check(runtime is None or (isinstance(runtime,dict) and all(text(v) for v in runtime.values())), 'invalid summary runtime')
            p = plans[s['run_id']]
            check(identity['plan_sha256'] == p['plan_sha256'], 'summary unbound plan')
            for key in ('subjects', 'cases', 'fieldlab_source_sha256'):
                check(identity[key] == p['planned_inputs'][key], 'summary planned input mismatch: '+key)
            check(identity['manifest'] == {'lab_id': p['lab_id'], **p['planned_inputs']['manifest']}, 'summary manifest mismatch')
            check(identity['mode'] == p['mode'] and identity['repeat'] == p['repeat'], 'summary matrix mismatch')
            check(identity['execution'] == {k:p['execution'][k] for k in ('selection_mode','requested_model','requested_reasoning_effort','approval_policy','network_access','timeout_override_seconds','keep_workspace')}, 'summary execution mismatch')
            check(s['run_id'] not in identities, 'duplicate summary run_id')
            identities[s['run_id']] = identity
        except Exception as exc:
            error(path, exc)
    for run_id in plans:
        if run_id not in identities:
            error(run_id, 'supplied plan has no validated summary')
    reviews = []
    for path in review_paths:
        try: reviews.append((Path(path), read(path)))
        except Exception as exc: error(path, exc)
    seen, used_reviews = set(), set()
    for raw in receipt_paths:
        path = Path(raw).resolve()
        try:
            r = read(path)
            check(r.get('schema_version') == 2 and r.get('receipt_type') == 'attempt', 'v2 attempt required')
            for key in ('run_id','lab_id','subject_id','case_id','attempt_id','identity_sha256'):
                check(text(r.get(key)), 'invalid '+key)
            p = plans[r['run_id']]; identity = identities[r['run_id']]
            check(r['identity_sha256'] == identity['identity_sha256'] and r['lab_id'] == p['lab_id'], 'receipt identity mismatch')
            check(isinstance(r.get('artifacts'),dict) and {'metadata.json','case.json'}.issubset(r['artifacts']), 'sealed metadata required')
            for name, entry in r['artifacts'].items():
                target = path.parent / name
                check(target.resolve().is_relative_to(path.parent) and not any(x.is_symlink() for x in [target, *target.parents] if x != path.parent), 'artifact path escapes or symlinks')
                check(isinstance(entry,dict) and text(entry.get('sha256')) and type(entry.get('bytes')) is int and target.stat().st_size == entry['bytes'], 'artifact byte metadata mismatch')
            report = artifact_report(path,r)
            check(not any(report[k] for k in ('missing','drifted','unverifiable')), 'artifact integrity failure: '+str(report))
            m = read(path.parent/'metadata.json')
            for key in ('run_id','lab_id','subject_id','case_id','attempt_id','identity_sha256','inputs','outcome','target_agent_invocations'):
                check(m.get(key) == r.get(key), 'sealed metadata mismatch: '+key)
            repeat = m.get('repeat'); check(type(repeat) is int, 'invalid repeat')
            key = (r['run_id'],r['subject_id'],r['case_id'],repeat)
            check(key in expected, 'unexpected planned row')
            attempt = (*key,r['attempt_id']); check(attempt not in seen, 'duplicate logical attempt')
            check(r['inputs'] == p['planned_inputs']['cases'][r['case_id']], 'case input mismatch')
            check(type(r.get('target_agent_invocations')) is int and r['target_agent_invocations'] in (0,1), 'invalid invocation count')
            check(r['outcome'] in {'pass','fail','error','timeout','termination-failure','inconclusive','input-drift','preflight-failed'}, 'invalid outcome')
            case = read(path.parent/'case.json'); execution = m['execution']
            check(canonical_digest(case) == r['inputs']['case_sha256'], 'sealed case input digest mismatch')
            check(type(r['execution_boundary'].get('target_started')) is bool and r['execution_boundary']['target_started'] == bool(r['target_agent_invocations']), 'target invocation boundary mismatch')
            check(case.get('sandbox') in {'read-only','workspace-write'} and type(case.get('timeout_seconds')) is int, 'invalid sealed case execution')
            check(m.get('state') in {'completed','preflight-failed','input-drift'}, 'unsealed attempt state')
            check(type(r['execution_boundary'].get('network_access')) is bool, 'invalid boundary network flag')
            wanted = {k:p['execution'][k] for k in ('selection_mode','requested_model','requested_reasoning_effort','approval_policy','network_access')}
            wanted.update(sandbox=case['sandbox'],timeout_seconds=p['execution']['timeout_override_seconds'] or case['timeout_seconds'])
            check(execution == wanted, 'attempt execution mismatch')
            check(r['selection'] == {'mode':wanted['selection_mode'],'requested_model':wanted['requested_model'],'requested_reasoning_effort':wanted['requested_reasoning_effort'],'actual_model_claimed':False}, 'receipt selection mismatch')
            for k in ('sandbox','approval_policy','network_access'):
                check(r['execution_boundary'][k] == wanted[k], 'receipt boundary mismatch')
            human = r['verification_summary']['human_review']; requirements = human['requirements']
            check(isinstance(requirements,list) and all(text(x) for x in requirements) and len(set(requirements)) == len(requirements), 'invalid requirements')
            check(type(human['required']) is bool and human['required'] == bool(requirements), 'invalid review required flag')
            invoked = r['target_agent_invocations'] == 1
            if invoked:
                check(requirements == case.get('human_review_requirements', []), 'receipt review requirements differ from sealed case')
                check(m['state'] == 'completed' and isinstance(m.get('process'),dict), 'invoked attempt lacks completed process metadata')
                check(m['process'].get('quiescent') is True, 'invoked attempt not quiescent')
                check(r['execution_boundary'].get('quiescent') is True, 'receipt not quiescent')
                check(r['outcome'] not in {'preflight-failed','input-drift'}, 'invoked preflight outcome')
                check(type(r['verification_summary'].get('passed')) is bool, 'invalid verification passed flag')
                if r['outcome'] == 'pass':
                    check(r['verification_summary']['passed'] is True, 'pass without verification support')
            else:
                check(m['state'] in {'preflight-failed','input-drift'} and r['outcome'] == m['state'], 'zero invocation must be a preflight failure')
            for field, allowed in [('subject_delivery',{'verified','failed','unknown'}),('host_selection',{'unknown','observed'}),('content_application',{'requires-semantic-review'})]:
                check(isinstance(r.get(field),dict) and r[field].get('status') in allowed, 'invalid '+field)
            usage = r['verification_summary'].get('usage')
            check(usage is None or isinstance(usage,dict), 'invalid usage object')
            if usage is not None:
                check(all(type(v) in (int,float) and v >= 0 for v in usage.values()), 'invalid usage values')
            bound = []
            for rp, review in reviews:
                binding = review.get('receipt',{})
                if binding.get('sha256') != sha(path): continue
                check(Path(binding['path']).resolve() == path, 'review path mismatch')
                check(review.get('schema_version') == 2 and review.get('method') == 'human', 'invalid review contract')
                check(all(text(review.get(k)) for k in ('review_id','created_at','rationale')), 'review identity required')
                check(review.get('independence') in {'implementer-run','separate-agent','external-reviewer'}, 'invalid review independence')
                outcomes = review.get('requirement_outcomes'); allowed = {'supported','not-supported','inconclusive'}
                check(isinstance(outcomes,dict) and set(outcomes) == set(requirements) and all(x in allowed for x in outcomes.values()), 'review requirements mismatch')
                check(review.get('judgment') in allowed and (review['judgment'] != 'supported' or all(x == 'supported' for x in outcomes.values())), 'invalid review judgment')
                bound.append({**review,'review_path':str(rp),'review_sha256':sha(rp)})
                used_reviews.add(str(rp))
            seen.add(attempt)
            row = dict(run_id=key[0],subject_id=key[1],case_id=key[2],repeat=repeat,attempt_id=r['attempt_id'],outcome=r['outcome'],target_agent_invocations=r['target_agent_invocations'],receipt_sha256=sha(path),reviews=bound,semantic_review='adjudication-required' if len(bound)>1 else bound[0]['judgment'] if bound else 'pending' if requirements else 'not-required')
            row.update(runtime=identity.get('runtime'), delivery=r['subject_delivery'], host_selection=r['host_selection'], content_application=r['content_application'], usage=usage, execution_boundary=r['execution_boundary'], process=m.get('process'), verification_passed=r['verification_summary'].get('passed'))
            rows.append(row); expected[key].append(row)
        except Exception as exc: error(path,exc)
    for path, review in reviews:
        if str(path) not in used_reviews: error(path,'unbound, stale or invalid review')
    groups = [dict(run_id=k[0],subject_id=k[1],case_id=k[2],repeat=k[3],attempts=v,status='missing-no-valid-receipt' if not v else 'retry-adjudication-required' if len(v)>1 else 'known-no-invocation' if v[0]['target_agent_invocations']==0 else 'observed') for k,v in expected.items()]
    return dict(contract_validation='comparison-fields-and-native-integrity',receipt_schema_validation='not-performed',attempts=rows,planned_rows=groups,missing_planned_rows=[g for g in groups if not g['attempts']],errors=errors,analysis='Descriptive only; retries are not repetitions; no automatic retry selection or independent-supported claim.')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('receipt','review','plan','summary'): p.add_argument('--'+key,type=Path,action='append',default=[])
    p.add_argument('--fieldlab-root',type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(compare(a.receipt,a.review,a.plan,a.fieldlab_root,a.summary),indent=2))

if __name__=='__main__': main()
