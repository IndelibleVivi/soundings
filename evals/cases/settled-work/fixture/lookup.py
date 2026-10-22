import json,sys
PAGES={'historical': 'Prior wording browse/learn/choose is retired. Current accepted mapping is find/understand/decide.'}
INDEX={'version': [], 'mechanism': [], 'deployment': [], 'history': [{'rank': 1, 'id': 'historical', 'snippet': 'Prior wording browse/learn/choose is retired. Current accepted ma'}], 'repair': []}
if len(sys.argv)!=3 or sys.argv[1] not in ("search","page"): raise SystemExit("lookup.py search QUERY | page ID")
print(json.dumps(INDEX.get(sys.argv[2],[]) if sys.argv[1]=="search" else PAGES[sys.argv[2]]))
