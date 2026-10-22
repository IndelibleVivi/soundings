import json,sys
PAGES={'reference-2': 'A museum reader keeps orientation visible and reveals details on demand. Transfer progressive disclosure, not its exact appearance. Cards, map and list can all express it.', 'deployment': 'The museum pays for cloud analytics. This is incidental deployment detail and requires a network; the target must remain offline.'}
INDEX={'version': [], 'mechanism': [{'rank': 1, 'id': 'reference-2', 'snippet': 'A museum reader keeps orientation visible and reveals details on '}], 'deployment': [{'rank': 2, 'id': 'deployment', 'snippet': 'The museum pays for cloud analytics. This is incidental deploymen'}], 'history': [], 'repair': []}
if len(sys.argv)!=3 or sys.argv[1] not in ("search","page"): raise SystemExit("lookup.py search QUERY | page ID")
print(json.dumps(INDEX.get(sys.argv[2],[]) if sys.argv[1]=="search" else PAGES[sys.argv[2]]))
