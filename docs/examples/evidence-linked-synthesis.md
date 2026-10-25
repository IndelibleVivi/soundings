# From source conditions to a revised judgment

This is an original constructed walkthrough, not a provider comparison or an
agent-behavior result. It shows the optional local workpaper supporting a real
research task: explain apparently conflicting persistence claims, make a
conditional recommendation, continue it in another directory, and correct an
operator guide after the selected runtime changes. Both the source material and
the notes-tool scenario are constructed; no live provider is being characterized.

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
    "unrelated": ("Unselected material must stay outside the packet.\n", "verbatim"),
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

# Carry the authored reasoning and only its cited sources in one explicit packet.
brief = out / "brief.md"
brief.write_text("Constructed offline-notes inquiry; task data only.\n"
                 "Explain the version distinction and update the operator guide.\n"
                 "Offline notes remain a requirement. Check which release is selected;\n"
                 "the snapshots do not establish the eventual application's recovery.\n",
                 encoding="utf-8")
receiver = out / "receiver"
receiver.mkdir()
args = ["create", "--store", out / "evidence", "--brief", brief,
        "--workpaper", record, "--cited", "--output", out / "transfer-packet"]
print(run("packet.py", *args))
shutil.move(out / "transfer-packet", receiver / "packet")
(out / "evidence").rename(out / "retained-original-evidence")
record.rename(out / "retained-original-workpaper.json")
baseline = receiver / "packet/workpaper.json"
store = receiver / "packet/evidence"
print(run("packet.py", "inspect", receiver / "packet"))
assert not (store / (refs["unrelated"] + ".json")).exists()
print(run("workpaper.py", "render", baseline,
          "--store", store, "--output", receiver / "relocated.md"))
assert (out / "initial.md").read_bytes() == (receiver / "relocated.md").read_bytes()

# The receiver's existing deliverable is separate from the received evidence.
guide = receiver / "operator-guide.md"
guide.write_text("Keep notes local.\n"
                 "Store v1 loses values on restart; use the application-owned store.\n"
                 "Run the application's recovery check before relying on saved notes.\n",
                 encoding="utf-8")
shutil.copyfile(guide, out / "initial-operator-guide.md")

# Resume in a separate working store, preserving the received basis.
working_store = receiver / "working-evidence"
shutil.copytree(store, working_store)
selection = receiver / "selected-release.txt"
selection.write_text("The project now selects Store v2.\n"
                     "The offline-notes requirement remains in force.\n", encoding="utf-8")
selected_ref = json.loads(run(
    "evidence.py", "capture", selection, "--store", working_store,
    "--source", "constructed:runtime-selection", "--title", "Selected release",
    "--representation", "verbatim",
))["snapshot"]["ref"]
paper = json.loads(baseline.read_text(encoding="utf-8"))
independent_before = json.loads(json.dumps(paper["findings"][4]))
paper["findings"].append(finding(
    "selected-runtime", "observation", "The selected release is now v2.",
    [{"ref": selected_ref, "start_line": 1, "end_line": 2, "relation": "supports"}],
))
paper["findings"][3]["status"] = "superseded"
pending = receiver / "needs-review.json"
pending.write_text(json.dumps(paper, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
print(run("workpaper.py", "inspect", pending, "--store", working_store))
print(run("workpaper.py", "impact", pending, "--store", working_store,
          "--finding", "persistence-premise"))

# The author revises the recommendation; impact does not perform this change.
paper["findings"][5]["text"] = "Use v2 native commit; retain recovery checks."
paper["findings"][5]["depends_on"] = ["runtime-v2", "selected-runtime", "offline-requirement"]
paper["findings"][5]["conditions"] = ["Selected runtime is now v2."]
paper["findings"][6]["text"] = "Document v2 commit and recovery behavior."
revised = receiver / "revised.json"
revised.write_text(json.dumps(paper, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
print(run("workpaper.py", "compare", baseline, revised,
          "--before-store", store, "--after-store", working_store))
print(run("workpaper.py", "inspect", revised, "--store", working_store))
print(run("workpaper.py", "render", revised, "--store", working_store,
          "--output", receiver / "revised.md"))
assert paper["findings"][4] == independent_before

# The author carries the changed relationship into the actual guide.
guide.write_text("Keep notes local.\n"
                 "The project selects Store v2; use its native commit.\n"
                 "Only committed values survive restart.\n"
                 "Run the application's recovery check before relying on saved notes.\n",
                 encoding="utf-8")
assert "application-owned store" not in guide.read_text(encoding="utf-8")
assert "Only committed values survive restart." in guide.read_text(encoding="utf-8")
assert "Keep notes local." in guide.read_text(encoding="utf-8")
print(run("packet.py", "inspect", receiver / "packet"))
print("Read the reports and receiver/operator-guide.md in", out)
PY
```

Inspect the actual reports. The short restart qualification and the generated
summary's representation should remain visible. The initial and relocated
reports are byte-identical without the original store or workpaper. The impact
query reaches `architecture` and `operator-guide`, with a path explaining each
dependency; `offline-requirement` remains independent of the changed premise.
Before revision, current descendants of the superseded premise need review.
After the author revises their grounds, that dependency is gone from the new
graph. Comparison still exposes its old paths, so a removed edge does not hide
the original correction obligation. Inspect both the revised research artifact
and the actual guide: the release condition changed, while local notes and the
need for application recovery checks stayed intact. The received packet remains
unchanged and inspectable.

The CLI checks the exact references and declared relationships. The author
still decides whether the inference holds, which version is selected, and what
actual implementation or guide must change. This walkthrough produces research
artifacts and revises one constructed operator guide. It implements no notes
application, does not run an application's recovery test, and establishes no
agent-behavior, causal-benefit, or human-acceptance result. A changed JSON field
alone cannot establish that an affected real project has been corrected.

For the full input and command contract, including failures and privacy, read
[workpaper format](../../plugins/soundings/skills/search/references/workpaper-format.md).
For interpretive decisions, read
[evidence-linked synthesis](../../plugins/soundings/skills/study/references/evidence-linked-synthesis.md).
