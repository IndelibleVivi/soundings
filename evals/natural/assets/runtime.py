"""Synthetic embedded runtime. Public API is identical in both release worlds."""
import json
import os
from pathlib import Path

# The builder substitutes only the runtime implementation, not the task prompt.
DURABLE = False

class Store:
    def __init__(self, root):
        self.root = Path(root); self.root.mkdir(parents=True, exist_ok=True)
        self.file = self.root/'runtime.json'
        self.values = json.loads(self.file.read_text()) if DURABLE and self.file.exists() else {}
    def get(self, key): return self.values.get(key)
    def set(self, key, value): self.values[key] = value
    def commit(self):
        if DURABLE:
            tmp = self.file.with_suffix('.tmp')
            with tmp.open('w') as f:
                json.dump(self.values, f); f.flush(); os.fsync(f.fileno())
            os.replace(tmp, self.file)
    def close(self): pass
