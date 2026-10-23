import argparse
import json
from runtime import Store
p=argparse.ArgumentParser(); p.add_argument('root'); p.add_argument('action',choices=['put','get','stage']); p.add_argument('key'); p.add_argument('value',nargs='?'); a=p.parse_args()
s=Store(a.root)
if a.action in ('put','stage'):
    s.set(a.key,a.value)
    # TODO: complete commit behavior
else: print(json.dumps(s.get(a.key)))
s.close()
