"""Hidden executable oracles. Run with Python -I; never import worker modules."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def run(root, *args):
    return subprocess.check_output([sys.executable, '-B', *map(str,args)], cwd=root, timeout=15, text=True).strip()


def runtime(root, world):
    with tempfile.TemporaryDirectory() as raw:
        store=Path(raw)/'store'
        def cli(*args): return run(root,root/'notes.py',store,*args)
        # Independent processes; cannot be satisfied by declarations or one process globals.
        cli('put','river','one'); cli('put','estuary','two')
        assert json.loads(cli('get','river'))=='one'
        assert json.loads(cli('get','estuary'))=='two'
        cli('stage','river','discard me')
        assert json.loads(cli('get','river'))=='one', 'uncommitted stage survived recovery'
        cli('put','river','revised')
        assert json.loads(cli('get','river'))=='revised'
        assert json.loads(cli('get','missing')) is None
        cli('put','unicode','水,🌊'); assert json.loads(cli('get','unicode'))=='水,🌊'
        # A committed root can be relocated with its actual on-disk state.
        moved=Path(raw)/'moved'; shutil.copytree(store,moved)
        assert json.loads(run(root,root/'notes.py',moved,'get','estuary'))=='two'


def transform(root):
    # Independent acceptance computation, not an import of submitted code.
    rows=json.loads((root/'records.json').read_text())
    delivered=json.loads((root/'report.json').read_text())
    run(root,root/'transform.py')
    result=json.loads((root/'report.json').read_text())
    assert delivered==result, 'delivered report differs from executable output'
    keep=[r for r in rows if r['active'] is True and r['score']>=40]
    keep.sort(key=lambda r:(r['group'],-r['score'],r['id']))
    assert result['items']==[{'id':r['id'],'label':r['title'].strip().upper(),'group':r['group'],'score':r['score']} for r in keep]
    totals={}
    for r in keep: totals[r['group']]=totals.get(r['group'],0)+r['score']
    assert result['totals']==totals


def repair(root):
    for text,want in [(' River, ,RIVER,Estuary,',['river','estuary']),('',[]),('Straße,STRASSE,水, 水',['strasse','水']),('x,x,y,X',['x','y'])]:
        assert json.loads(run(root,root/'normalize.py',text))==want


def main():
    p=argparse.ArgumentParser();p.add_argument('family');p.add_argument('world');p.add_argument('trusted',type=Path);p.add_argument('--node');p.add_argument('--playwright');a=p.parse_args();root=Path.cwd();trusted=a.trusted.resolve()
    # Reject changed accepted inputs rather than letting a valid replacement
    # program conceal tampering. Execute in a scratch tree; never mutate the
    # runner's sealed final verifier workspace, including Python bytecode.
    for src in trusted.rglob('*'):
        if src.is_file():
            name=src.relative_to(trusted)
            observed=root/name
            assert observed.is_file() and not observed.is_symlink() and observed.read_bytes()==src.read_bytes(), 'accepted input drift: '+str(name)
    with tempfile.TemporaryDirectory(prefix='natural-execution-') as raw:
        execution=Path(raw)/'workspace'
        shutil.copytree(root,execution,ignore=shutil.ignore_patterns('.git','__pycache__'))
        for src in trusted.rglob('*'):
            if src.is_file():
                target=execution/src.relative_to(trusted);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,target)
        if a.family in ('engineering','obstacle'):runtime(execution,a.world)
        elif a.family=='settled':transform(execution)
        elif a.family=='repair':repair(execution)
        elif a.family=='reading': subprocess.run([a.node,str(Path(__file__).with_name('browser_check.cjs')),str(execution),a.playwright],check=True,timeout=60)
        else: raise ValueError(a.family)
    print('functional acceptance passed')

if __name__=='__main__':main()
