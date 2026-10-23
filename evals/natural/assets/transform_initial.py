import json
from pathlib import Path
rows=json.loads(Path('records.json').read_text())
Path('report.json').write_text(json.dumps(rows[:3]))
