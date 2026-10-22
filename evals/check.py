#!/usr/bin/env python3
"""Provider-neutral deterministic gate. Never launches a target agent."""
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
for directory in ("plugins/soundings/skills/search/scripts", "evals"):
    result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", directory,
                             "-p", "test_*.py", "-v"], cwd=ROOT, env=env)
    if result.returncode:
        raise SystemExit(result.returncode)
