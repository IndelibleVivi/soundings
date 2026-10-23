"""One adaptive valid solution; native persistence and atomic app persistence both accepted."""
import argparse
import json
import os
from pathlib import Path
from runtime import Store
p=argparse.ArgumentParser(); p.add_argument('root'); p.add_argument('action',choices=['put','get','stage']); p.add_argument('key'); p.add_argument('value',nargs='?'); a=p.parse_args()
s=Store(a.root); backup=Path(a.root)/'notes.json'
values=json.loads(backup.read_text()) if backup.exists() else {}
if a.action in ('put','stage'):
    s.set(a.key,a.value)
    if a.action in ('put','stage'):
        s.commit(); values[a.key]=a.value; tmp=backup.with_suffix('.tmp')
        with tmp.open('w') as f: json.dump(values,f); f.flush(); os.fsync(f.fileno())
        os.replace(tmp,backup)
else: print(json.dumps(values.get(a.key,s.get(a.key))))
s.close()
