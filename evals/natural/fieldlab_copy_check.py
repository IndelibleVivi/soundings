"""Offline use of current Field Lab command-copy APIs; never invokes an adapter."""
import argparse
import json
from pathlib import Path
import shutil
import tempfile


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('pack',type=Path);a=p.parse_args()
    # The caller explicitly supplies its existing checkout through PYTHONPATH.
    from fieldlab.io import tree_digest
    from fieldlab.verify import evaluate_command_assertion
    from fieldlab.workspace import copy_workspace
    reports=[]
    with tempfile.TemporaryDirectory(prefix='natural-native-command-copy-') as raw:
        root=Path(raw)
        cases=sorted(c for c in (a.pack/'cases').iterdir() if c.name.endswith('-a'))
        for case in cases:
            for variation in ('ordinary','html-only','split-with-save') if case.name.startswith('reading-') else ('ordinary',):
                final=root/(case.name+'-'+variation)/'worker-final';shutil.copytree(case/'fixture',final)
                if variation=='html-only':
                    html=(final/'desk.html').read_text();script=(case/'expected'/'desk.js').read_text()
                    (final/'desk.html').write_text(html.replace('<script src="desk.js"></script>','<script>'+script+'</script>'))
                elif variation=='split-with-save':
                    assets=Path(__file__).resolve().parent/'assets'
                    for source,target in [('desk_split.html','desk.html'),('desk_split.js','desk.js'),('desk_split_storage.js','storage.js'),('desk_split.css','styles.css')]:shutil.copyfile(assets/source,final/target)
                else:shutil.copytree(case/'expected',final,dirs_exist_ok=True)
                identity=tree_digest(final);copy=final.parent/'verifier-copy';copy_workspace(final,copy)
                command=json.loads((case/'case.json').read_text())['command_assertions'][0]
                result=evaluate_command_assertion(command,copy,final.parent/'assertion-artifacts',0)
                mutated=tree_digest(copy)!=identity
                assert result['passed'],result
                assert not mutated,case.name+' verifier mutated sealed workspace'
                assert tree_digest(final)==identity
                reports.append(dict(case=case.name,variation=variation,passed=True,verifier_mutated=False))
    print(json.dumps(dict(target_calls=0,api='fieldlab.verify.evaluate_command_assertion + workspace.copy_workspace + io.tree_digest (same command-copy boundary used by runner)',checks=reports),indent=2))

if __name__=='__main__':main()
