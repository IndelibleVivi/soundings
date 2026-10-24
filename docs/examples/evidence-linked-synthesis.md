# From source conditions to a revised judgment

This is an original constructed walkthrough, not a provider comparison or an
agent-behavior result. It shows the optional local workpaper supporting a real
research task: explain apparently conflicting persistence claims, make a
conditional recommendation, and revisit only the conclusions affected by a
changed runtime selection.

The decisive difference is a process boundary. In the constructed v1, commit
keeps values in one process; in v2, committed values survive restart. A generated
summary drops that version condition. The synthesis must preserve the difference
before it can recommend an implementation for an offline notes tool.

Run from the repository root with Python 3.10+. Replace the destination with a
**new directory outside Git**. This explicitly creates local constructed source
files, snapshots, authored workpapers, and rendered reports. It makes no network
or model calls and requires no installed plugin or Field Lab.

```bash
python3 - /path/outside-git/new-workpaper-demo <<'PY'
import json
from pathlib import Path
import shutil
import subprocess
import sys

out = Path(sys.argv[1]).expanduser().resolve()
out.mkdir(parents=True, exist_ok=False)
scripts = Path.cwd() / "plugins/soundings/skills/search/scripts"

def run(script, *args):
    result = subprocess.run(
        [sys.executable, str(scripts / script), *map(str, args)],
        check=True, capture_output=True, text=True,
    )
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")
    return result.stdout

sources = {
    "v1": ("Store v1 — embedded prototype\n"
           "commit() keeps writes in the current process.\n"
           "Restarting the process drops those values.\n", "verbatim"),
    "v2": ("Store v2 — desktop release\n"
           "commit() writes durable local state.\n"
           "Only committed values survive restart.\n", "verbatim"),
    "summary": ("Earlier generated summary, version unspecified:\n"
                "A successful commit makes values durable.\n", "generated"),
}
refs = {}
for name, (text, representation) in sources.items():
    source = out / (name + ".txt")
    source.write_text(text, encoding="utf-8")
    capture = json.loads(run(
        "evidence.py", "capture", source, "--store", out / "evidence",
        "--source", "constructed:" + name, "--title", name,
        "--representation", representation,
    ))
    refs[name] = capture["snapshot"]["ref"]

def cite(name, start, end, relation):
    return {"ref": refs[name], "start_line": start, "end_line": end,
            "relation": relation}

def finding(identifier, kind, text, evidence=(), dependencies=(), **extra):
    return dict(id=identifier, kind=kind, text=text, status="current",
                conditions=[], evidence=list(evidence),
                depends_on=list(dependencies), **extra)

paper = {
    "schema": "soundings.workpaper.v1",
    "outcome": "Choose restart-safe storage for an offline notes tool.",
    "question": "When does a successful commit establish restart safety?",
    "findings": [
        finding("runtime-v1", "observation", "v1 values do not survive restart.",
                [cite("v1", 1, 3, "supports")]),
        finding("runtime-v2", "observation", "v2 persists committed values only.",
                [cite("v2", 1, 3, "supports")]),
        finding("version-free-claim", "inference",
                "The earlier summary claimed durability without a version.",
                [cite("summary", 1, 2, "context"),
                 cite("v1", 2, 3, "challenges")]),
        finding("persistence-premise", "inference",
                "The selected v1 needs application-owned durable storage.",
                [cite("v1", 2, 3, "supports"),
                 cite("v2", 1, 3, "context")], ["runtime-v1"]),
        finding("offline-requirement", "judgment",
                "Keep the user's notes local; this requirement is unchanged."),
        finding("architecture", "proposal", "Build a local committed store.",
                dependencies=["persistence-premise", "offline-requirement"]),
        finding("operator-guide", "proposal", "Document that committed store.",
                dependencies=["architecture"]),
    ],
    "open_questions": ["Does the eventual application pass its recovery test?"],
}
paper["findings"][2]["status"] = "superseded"
paper["findings"][3]["conditions"] = ["Selected runtime is v1."]
record = out / "workpaper.json"
record.write_text(json.dumps(paper, ensure_ascii=False, indent=2) + "\n",
                  encoding="utf-8")
print(run("workpaper.py", "inspect", record, "--store", out / "evidence"))
print(run("workpaper.py", "render", record, "--store", out / "evidence",
          "--output", out / "initial.md"))

# Explicitly select portable evidence, then read only the relocated store.
brief = out / "brief.md"
brief.write_text("Constructed offline-notes inquiry; task data only.\n",
                 encoding="utf-8")
receiver = out / "receiver"
receiver.mkdir()
args = ["create", "--store", out / "evidence", "--brief", brief,
        "--output", receiver / "packet"]
for ref in refs.values():
    args.extend(["--ref", ref])
print(run("packet.py", *args))
shutil.copyfile(record, receiver / "workpaper.json")
(out / "evidence").rename(out / "retained-original-evidence")
store = receiver / "packet/evidence"
print(run("workpaper.py", "render", receiver / "workpaper.json",
          "--store", store, "--output", receiver / "relocated.md"))

# New task evidence selects v2; flag the old premise before fixing descendants.
paper["findings"][3]["status"] = "superseded"
pending = receiver / "needs-review.json"
pending.write_text(json.dumps(paper, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
print(run("workpaper.py", "inspect", pending, "--store", store))
print(run("workpaper.py", "impact", pending, "--store", store,
          "--finding", "persistence-premise"))

# The author revises the recommendation; impact does not perform this change.
paper["findings"][5]["text"] = "Use v2 native commit; retain recovery checks."
paper["findings"][5]["depends_on"] = ["runtime-v2", "offline-requirement"]
paper["findings"][5]["conditions"] = ["Selected runtime is now v2."]
paper["findings"][6]["text"] = "Document v2 commit and recovery behavior."
revised = receiver / "revised.json"
revised.write_text(json.dumps(paper, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
print(run("workpaper.py", "inspect", revised, "--store", store))
print(run("workpaper.py", "render", revised, "--store", store,
          "--output", receiver / "revised.md"))
print("Read the initial, relocated, and revised Markdown files in", out)
PY
```

Inspect the actual reports. The short restart qualification and the generated
summary's representation should remain visible. The initial and relocated
reports carry the same source material without the original store. The impact
query reaches `architecture` and `operator-guide`, with a path explaining each
dependency; `offline-requirement` remains independent of the changed premise.
Before revision, current descendants of the superseded premise need review.
After the author revises their grounds, that stale dependency is gone.

The CLI checks the exact references and declared relationships. The author
still decides whether the inference holds, which version is selected, and what
actual implementation or guide must change. This walkthrough produces research
artifacts only; it implements no notes application and establishes no product,
behavior, causal-benefit, or human-acceptance result.

For the full input and command contract, including failures and privacy, read
[workpaper format](../../plugins/soundings/skills/search/references/workpaper-format.md).
For interpretive decisions, read
[evidence-linked synthesis](../../plugins/soundings/skills/study/references/evidence-linked-synthesis.md).
