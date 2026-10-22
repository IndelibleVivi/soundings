import json,sys
PAGES={'repair': 'Change only redy to ready; preserve count.'}
INDEX={'version': [], 'mechanism': [], 'deployment': [], 'history': [], 'repair': [{'rank': 1, 'id': 'repair', 'snippet': 'Change only redy to ready; preserve count.'}]}
if len(sys.argv)!=3 or sys.argv[1] not in ("search","page"): raise SystemExit("lookup.py search QUERY | page ID")
print(json.dumps(INDEX.get(sys.argv[2],[]) if sys.argv[1]=="search" else PAGES[sys.argv[2]]))
