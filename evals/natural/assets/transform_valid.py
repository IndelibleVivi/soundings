import json
from pathlib import Path
rows=json.loads(Path('records.json').read_text())
selected=sorted((r for r in rows if r['active'] and r['score']>=40),key=lambda r:(r['group'],-r['score'],r['id']))
items=[dict(id=r['id'],label=r['title'].strip().upper(),group=r['group'],score=r['score']) for r in selected]
groups={g:sum(r['score'] for r in selected if r['group']==g) for g in sorted({r['group'] for r in selected})}
Path('report.json').write_text(json.dumps(dict(items=items,totals=groups),ensure_ascii=False))
