"""Offline composition: never invokes a target model."""
import argparse
import itertools
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent

def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])

def snapshot(repo, ref, prefix, dest):
    commit = git(repo, 'rev-parse', ref + '^{commit}').decode().strip()
    names = git(repo, 'ls-tree', '-r', '--name-only', commit, prefix).decode().splitlines()
    if not names:
        raise ValueError('empty runtime tree: ' + prefix)
    for name in names:
        rel = Path(name).relative_to(prefix)
        mode = git(repo, 'ls-tree', commit, name).decode().split()[0]
        if mode not in ('100644', '100755'):
            raise ValueError('unsupported tree entry: ' + name)
        out = dest / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(git(repo, 'show', commit + ':' + name))
        out.chmod(0o755 if mode == '100755' else 0o644)
    if not list(dest.rglob('SKILL.md')):
        raise ValueError('no skills')
    return commit

def verify_references(root):
    import re
    for skill in root.rglob('*.md'):
        for ref in re.findall(r'\[[^\]]*\]\(([^)]+)\)', skill.read_text()):
            if '://' in ref or ref.startswith('#'): continue
            resolved = (skill.parent / ref.split('#')[0]).resolve()
            if not resolved.is_relative_to(root.resolve()) or not resolved.exists():
                raise ValueError('broken runtime reference: ' + str(skill) + ' -> ' + ref)
    if not list((root / 'skills').glob('*/SKILL.md')):
        raise ValueError('no directly discoverable skills')

def build(a):
    out = a.output.resolve()
    for repo in (a.soundings, a.servotab, a.fieldlab):
        root = Path(repo).resolve()
        if out == root or root in out.parents:
            raise ValueError('output must be external to source repositories')
    if subprocess.run(['git', '-C', str(out.parent), 'rev-parse', '--show-toplevel'], capture_output=True).returncode == 0:
        raise ValueError('output parent belongs to Git')
    out.mkdir(parents=False, exist_ok=False)
    shutil.copytree(HERE / 'cases', out / 'cases')
    subjects = {}; provenance = {}; rows = []
    for s, t in itertools.product(('old', 'current'), repeat=2):
        name = 'soundings-' + s + '-servotab-' + t
        dest = out / 'subjects' / name
        sc = snapshot(a.soundings, getattr(a, 'soundings_' + s), 'plugins/soundings', dest / 'soundings')
        tc = snapshot(a.servotab, getattr(a, 'servotab_' + t), 'plugins/servotab', dest / 'servotab')
        # Compose direct discoverable skills; package-level references retain their
        # original relation to skills/<name>/SKILL.md under the .agents mount.
        for package in ('soundings','servotab'):
            package_root = dest / package
            for child in list(package_root.iterdir()):
                if child.name not in ('skills','references'): continue
                target = dest / child.name
                shutil.copytree(child, target, dirs_exist_ok=True)
            shutil.rmtree(package_root)
        verify_references(dest)
        subjects[name] = dict(kind='agent-skill', label=name, source=dict(type='snapshot', path='subjects/' + name), mount='.agents')
        provenance[name] = dict(soundings=sc, servotab=tc)
    subjects['isolated-control'] = dict(kind='control', label='True no-Skill isolated control')
    manifest = dict(schema_version=2, lab_id='soundings-offline-research', description='Constructed offline cases; no behavior evidence yet.', cases_root='cases', subjects=subjects, defaults=dict(adapter='codex-exec', approval_policy='never', network_access=False, output_root='runs', keep_workspace=False))
    (out / 'fieldlab.json').write_text(json.dumps(manifest, indent=2))
    env = dict(os.environ, PYTHONPATH=str(Path(a.fieldlab).resolve()))
    def lab(*args):
        subprocess.run([sys.executable, '-m', 'fieldlab', *map(str,args)], env=env, check=True)
    lab('validate', out / 'fieldlab.json')
    lab('selftest', out / 'fieldlab.json')
    for subject in subjects:
        if subject == 'isolated-control' and not a.control: continue
        args = ['plan', out / 'fieldlab.json', '--subject', subject, '--repeat', '2', '--model', a.model, '--reasoning-effort', a.effort, '--output', out / (subject + '.plan.json')]
        for case in sorted((out / 'cases').iterdir()):
            args += ['--case', case.name]
            for rep in (1,2):
                if subject != 'isolated-control': rows.append(dict(subject=subject, case=case.name, repetition=rep))
        lab(*args)
    (out / 'composition.json').write_text(json.dumps(dict(schema_version=1, authorization='offline only; plans grant no invocation authority', provenance=provenance, invocations=rows), indent=2))
    return out

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=['build','materialize'])
    for key in ('output','soundings','servotab','fieldlab'): p.add_argument('--'+key, type=Path, required=True)
    for key,default in [('soundings-old','3619a1b'),('soundings-current','84accd1'),('servotab-old','959823e'),('servotab-current','0e63ed0')]: p.add_argument('--'+key,default=default)
    p.add_argument('--control',action='store_true',help='Create separate optional 8-invocation control plan')
    p.add_argument('--model',required=True); p.add_argument('--effort',required=True,choices=['minimal','low','medium','high','xhigh'])
    print(build(p.parse_args()))
if __name__=='__main__': main()
