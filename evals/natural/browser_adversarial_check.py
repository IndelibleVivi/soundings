"""Executable browser regression variants against a materialized sealed oracle."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('pack',type=Path);a=p.parse_args()
    case=a.pack/'cases'/'reading-ordinary-a';assets=Path(__file__).resolve().parent/'assets'
    command=json.loads((case/'case.json').read_text())['command_assertions'][0]['argv']
    checks=[]
    with tempfile.TemporaryDirectory(prefix='natural-browser-regression-') as raw:
        for variant,files,reason in [
            ('split-with-save',[('desk_split.html','desk.html'),('desk_split.js','desk.js'),('desk_split_storage.js','storage.js'),('desk_split.css','styles.css')],None),
            ('lost-restored-evidence',[('desk_bad_restore.js','desk.js')],'export missing'),
            ('restored-external-request',[('desk_bad_restore_network.js','desk.js')],'offline boundary violated'),
        ]:
            work=Path(raw)/variant;shutil.copytree(case/'fixture',work)
            for source,target in files:shutil.copyfile(assets/source,work/target)
            before={str(p.relative_to(work)):p.read_bytes() for p in work.rglob('*') if p.is_file()}
            result=subprocess.run(command,cwd=work,capture_output=True,text=True,timeout=60)
            if reason:assert result.returncode!=0 and reason in result.stderr,(variant,result.stdout,result.stderr)
            else:assert result.returncode==0,(variant,result.stdout,result.stderr)
            assert before=={str(p.relative_to(work)):p.read_bytes() for p in work.rglob('*') if p.is_file()}
            checks.append(dict(variant=variant,expected='reject' if reason else 'accept',observed_exit=result.returncode,reason=reason,workspace_unchanged=True))
    print(json.dumps(dict(target_calls=0,checks=checks),indent=2))

if __name__=='__main__':main()
