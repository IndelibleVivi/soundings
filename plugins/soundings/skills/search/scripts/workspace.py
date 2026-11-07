#!/usr/bin/env python3
"""Explicit, portable local inquiry state; task material, never authority.

Python 3.10+, standard library only. The newest numbered revision is the commit
point. Sources and actual result files are immutable members. No network,
model, automatic memory, source-instruction execution or semantic acceptance.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import uuid

import evidence
from evidence import EvidenceError, encode


SCHEMA = "soundings.workspace.v1"
STATE_KEYS = {"schema", "revision", "updated_at", "outcome", "question", "next_action",
              "project_record", "settled", "leads", "sources", "artifacts", "feedback"}
STATUSES = {"unread", "partial", "read", "blocked", "dismissed"}
KINDS = {"explanation", "creative", "implementation", "other"}
ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")
REVISION = re.compile(r"([0-9]{8})\.json\Z")
MAX_FILE_BYTES = 16 * 1024 * 1024


def _text(value, label, *, empty=False):
    if not isinstance(value, str) or (not empty and not value.strip()):
        raise EvidenceError(f"{label} must be {'a string' if empty else 'a nonempty string'}")
    return value


def _object(value, keys, label):
    if not isinstance(value, dict) or set(value) != set(keys):
        raise EvidenceError(f"invalid {label} fields")


def _identifier(value):
    if not isinstance(value, str) or not ID.fullmatch(value):
        raise EvidenceError("invalid local identifier")
    return value


def _regular(path):
    if path.is_symlink() or not path.is_file():
        raise EvidenceError(f"member must be a regular file: {path.name}")


def _directory(path):
    if path.is_symlink() or not path.is_dir():
        raise EvidenceError(f"member must be a real directory: {path.name}")


def _file_bytes(path):
    if not path.is_file() or path.stat().st_size > MAX_FILE_BYTES:
        raise EvidenceError("selected input must be a file of at most 16 MiB")
    data = path.read_bytes()
    if len(data) > MAX_FILE_BYTES:
        raise EvidenceError("selected input grew beyond 16 MiB")
    return data


def _json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")


def _revision_name(number):
    if type(number) is not int or not 1 <= number <= 99999999:
        raise EvidenceError("invalid or exhausted revision number")
    return f"{number:08d}.json"


def _descends(artifacts, successor, ancestor):
    visited = set()
    while successor is not None:
        if successor in visited or successor not in artifacts:
            return False
        if successor == ancestor:
            return True
        visited.add(successor)
        successor = artifacts[successor]["supersedes"]
    return False


def _validate_state(state):
    _object(state, STATE_KEYS, "workspace state")
    if state["schema"] != SCHEMA:
        raise EvidenceError("unsupported workspace schema")
    _revision_name(state["revision"])
    for key in ("updated_at", "outcome", "question", "next_action"):
        _text(state[key], key)
    _text(state["project_record"], "project_record", empty=True)
    if not isinstance(state["settled"], list):
        raise EvidenceError("settled must be a list")
    for value in state["settled"]:
        _text(value, "settled choice")
    for key in ("leads", "sources", "artifacts", "feedback"):
        if not isinstance(state[key], dict):
            raise EvidenceError(f"{key} must be an object")
    for key, lead in state["leads"].items():
        _identifier(key)
        _object(lead, {"locator", "title", "why", "status", "note"}, "lead")
        for field in ("locator", "title", "why"):
            _text(lead[field], "lead " + field)
        _text(lead["note"], "lead note", empty=True)
        if lead["status"] not in STATUSES or (lead["status"] == "blocked" and not lead["note"].strip()):
            raise EvidenceError("invalid lead status or missing blocked reason")
    for ref, source in state["sources"].items():
        if not re.fullmatch(r"s-[0-9a-f]{32}", ref):
            raise EvidenceError("invalid source ref")
        _object(source, {"via", "lead", "derived_from", "delivered"}, "source")
        _text(source["via"], "acquisition method")
        if source["lead"] is not None and source["lead"] not in state["leads"]:
            raise EvidenceError("source names an unknown lead")
        if not isinstance(source["delivered"], list):
            raise EvidenceError("invalid delivered ranges")
        for pair in source["delivered"]:
            if not isinstance(pair, list) or len(pair) != 2 or any(type(n) is not int for n in pair) or not 1 <= pair[0] <= pair[1]:
                raise EvidenceError("invalid delivered range bounds")
        seen, current = {ref}, source["derived_from"]
        while current is not None:
            if current in seen or current not in state["sources"]:
                raise EvidenceError("invalid source derivation")
            seen.add(current)
            current = state["sources"][current]["derived_from"]
    for key, artifact in state["artifacts"].items():
        _identifier(key)
        _object(artifact, {"name", "kind", "path", "bytes", "note", "refs", "supersedes"}, "artifact")
        _safe_name(artifact["name"])
        if artifact["path"] != f"{key}-{artifact['name']}" or artifact["kind"] not in KINDS:
            raise EvidenceError("invalid artifact path or kind")
        if type(artifact["bytes"]) is not int or not 0 <= artifact["bytes"] <= MAX_FILE_BYTES:
            raise EvidenceError("invalid artifact size")
        _text(artifact["note"], "artifact note", empty=True)
        if not isinstance(artifact["refs"], list) or any(ref not in state["sources"] for ref in artifact["refs"]):
            raise EvidenceError("artifact cites an unknown source")
        parent = artifact["supersedes"]
        if parent is not None:
            if parent == key or parent not in state["artifacts"] or state["artifacts"][parent]["name"] != artifact["name"]:
                raise EvidenceError("invalid artifact predecessor")
            seen, cursor = {key}, parent
            while cursor is not None:
                if cursor in seen:
                    raise EvidenceError("artifact predecessor cycle")
                seen.add(cursor)
                cursor = state["artifacts"][cursor]["supersedes"]
    for key, item in state["feedback"].items():
        _identifier(key)
        _object(item, {"artifact", "text", "status", "successor", "resolution"}, "feedback")
        if item["artifact"] not in state["artifacts"] or item["status"] not in {"open", "resolved"}:
            raise EvidenceError("invalid feedback target or status")
        _text(item["text"], "feedback text")
        _text(item["resolution"], "feedback resolution", empty=True)
        if item["status"] == "open":
            if item["successor"] is not None or item["resolution"]:
                raise EvidenceError("open feedback cannot carry a resolution")
        elif (not item["resolution"].strip() or item["successor"] == item["artifact"]
              or not _descends(state["artifacts"], item["successor"], item["artifact"])):
            raise EvidenceError("resolved feedback needs an actual descendant and reason")


def _safe_name(name):
    _text(name, "artifact name")
    if name in {".", ".."} or name.startswith(".") or any(c in name for c in "/\\") or any(ord(c) < 32 for c in name):
        raise EvidenceError("artifact name must be one safe visible filename")


def _load(root, *, recover_unreferenced=False):
    _directory(root)
    allowed = {"revisions", "evidence", "artifacts", ".lock"}
    if set(p.name for p in root.iterdir()) - allowed:
        raise EvidenceError("workspace has unexpected top-level members")
    for name in ("revisions", "evidence", "artifacts"):
        _directory(root / name)
    if (root / ".lock").exists() or (root / ".lock").is_symlink():
        _regular(root / ".lock")
    paths = sorted((root / "revisions").iterdir())
    states, extras = [], []
    for path in paths:
        _regular(path)
        match = REVISION.fullmatch(path.name)
        if not match:
            if recover_unreferenced and path.name.startswith(".tmp-"):
                extras.append("revisions/" + path.name)
                continue
            raise EvidenceError("unexpected revision member; inspect partial write")
        try:
            state = json.loads(path.read_text(encoding="utf-8"))
            _validate_state(state)
        except (ValueError, KeyError, TypeError) as exc:
            raise EvidenceError(f"invalid revision {path.name}: {exc}") from exc
        if state["revision"] != len(states) + 1 or path.name != _revision_name(state["revision"]):
            raise EvidenceError("missing, misnumbered or noncontiguous workspace revision")
        if states:
            for kind in ("sources", "artifacts", "feedback", "leads"):
                if set(states[-1][kind]) - set(state[kind]):
                    raise EvidenceError("a revision removed retained history")
            for key, artifact in states[-1]["artifacts"].items():
                if artifact != state["artifacts"][key]:
                    raise EvidenceError("a revision rewrote an immutable result declaration")
        states.append(state)
    if not states:
        raise EvidenceError("workspace has no committed revision")
    current = states[-1]
    expected = {"evidence": {ref + ".json" for ref in current["sources"]},
                "artifacts": {a["path"] for a in current["artifacts"].values()}}
    for folder, names in expected.items():
        actual = {p.name for p in (root / folder).iterdir()}
        if names - actual:
            raise EvidenceError(f"missing retained {folder} members")
        for path in (root / folder).iterdir():
            _regular(path)
        if actual - names:
            extras += [folder + "/" + name for name in sorted(actual - names)]
    if extras and not recover_unreferenced:
        raise EvidenceError("unreferenced staged material; inspect then fork --recover-unreferenced: " + ", ".join(extras))
    for ref, source in current["sources"].items():
        snapshot = evidence.load(root / "evidence", ref)
        count = len(snapshot["content"].splitlines())
        if any(pair[1] > count for pair in source["delivered"]):
            raise EvidenceError("delivered range exceeds retained source")
    for artifact in current["artifacts"].values():
        if (root / "artifacts" / artifact["path"]).stat().st_size != artifact["bytes"]:
            raise EvidenceError("retained artifact size changed")
    return current, extras


def load_state(root: Path) -> dict:
    return _load(Path(root))[0]


def _publish(path, content):
    descriptor, name = tempfile.mkstemp(dir=path.parent, prefix=".tmp-")
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)  # Same-directory no-clobber publication.
    finally:
        temporary.unlink(missing_ok=True)


@contextmanager
def _locked(root):
    _directory(root)
    lock = root / ".lock"
    try:
        descriptor = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise EvidenceError("workspace writer lock exists; inspect owner before recovery") from exc
    try:
        with os.fdopen(descriptor, "w") as stream:
            stream.write(str(os.getpid()) + "\n")
        yield
    finally:
        lock.unlink()


def _change(root, action, *, expect_revision=None, max_bytes=8192):
    with _locked(root):
        previous = load_state(root)
        if expect_revision is not None and previous["revision"] != expect_revision:
            raise EvidenceError("stale workspace revision; resume before changing it")
        state = deepcopy(previous)
        state["revision"] += 1
        state["updated_at"] = datetime.now(timezone.utc).isoformat()
        payload, files = action(state)
        _validate_state(state)
        encode(payload, max_bytes)  # No new member or revision if stdout cannot fit.
        published = []
        try:
            for path, content in files.items():
                _publish(root / path, content)
                published.append(root / path)
            _publish(root / "revisions" / _revision_name(state["revision"]), _json_bytes(state))
        except BaseException:
            # Roll back only this command's uniquely named, uncommitted members.
            # Abrupt process death can still leave extras, diagnosed by _load.
            for path in published:
                path.unlink()
            raise
        return payload


def init(root, outcome, question, next_action, project_record="", *, max_bytes=8192):
    state = {"schema": SCHEMA, "revision": 1, "updated_at": datetime.now(timezone.utc).isoformat(),
             "outcome": outcome, "question": question, "next_action": next_action,
             "project_record": project_record, "settled": [], "leads": {}, "sources": {},
             "artifacts": {}, "feedback": {}}
    _validate_state(state)
    result = {"operation": "init", "revision": 1, "workspace": str(root)}
    encode(result, max_bytes)
    root.mkdir(mode=0o700)
    for name in ("revisions", "evidence", "artifacts"):
        (root / name).mkdir(mode=0o700)
    _publish(root / "revisions" / _revision_name(1), _json_bytes(state))
    return result


def update(root, patch, **options):
    if not patch or set(patch) - {"outcome", "question", "next_action", "project_record", "settled"}:
        raise EvidenceError("update needs explicit supported fields")
    def action(state):
        state.update(patch)
        return {"operation": "update", "revision": state["revision"]}, {}
    return _change(root, action, **options)


def lead(root, *, lead_id=None, **fields):
    options = {key: fields.pop(key) for key in ("expect_revision", "max_bytes") if key in fields}
    lead_id = _identifier(lead_id) if lead_id else "l-" + uuid.uuid4().hex
    def action(state):
        item = deepcopy(state["leads"].get(lead_id, {"locator": "", "title": "", "why": "", "status": "unread", "note": ""}))
        item.update({key: value for key, value in fields.items() if value is not None})
        state["leads"][lead_id] = item
        return {"operation": "lead", "id": lead_id, "revision": state["revision"]}, {}
    return _change(root, action, **options)


def capture_source(root: Path, file: Path, source: str, title: str, representation: str,
                   via="local", lead_id=None, derived_from=None, *, expect_revision=None, max_bytes=8192):
    selected_bytes = _file_bytes(file)
    load_state(root)
    with tempfile.TemporaryDirectory(prefix="soundings-source-") as temporary:
        store = Path(temporary) / "evidence"
        selected_input = Path(temporary) / "selected.txt"
        selected_input.write_bytes(selected_bytes)
        captured = evidence.capture(selected_input, store, source, title, representation, 8192)
        ref = captured["snapshot"]["ref"]
        content = (store / (ref + ".json")).read_bytes()
    def action(state):
        if lead_id is not None and lead_id not in state["leads"]:
            raise EvidenceError("unknown lead; capture was not committed")
        if derived_from is not None and derived_from not in state["sources"]:
            raise EvidenceError("unknown source derivation")
        state["sources"][ref] = {"via": via, "lead": lead_id, "derived_from": derived_from, "delivered": []}
        return {"operation": "capture", "ref": ref, "revision": state["revision"]}, {"evidence/" + ref + ".json": content}
    return _change(root, action, expect_revision=expect_revision, max_bytes=max_bytes)


def _merge_ranges(pairs):
    merged = []
    for start, end in sorted(pairs):
        if merged and start <= merged[-1][1] + 1:
            merged[-1][1] = max(end, merged[-1][1])
        else:
            merged.append([start, end])
    return merged


def read_source(root, ref, *, query=None, start_line=1, end_line=None, context=2,
                case_sensitive=False, max_bytes=8192, expect_revision=None):
    def action(state):
        if ref not in state["sources"]:
            raise EvidenceError("source is outside this workspace selection")
        if query is None:
            payload = evidence.read(root / "evidence", ref, start_line, end_line, max_bytes)
        else:
            payload = evidence.find(root / "evidence", ref, query, context, max_bytes,
                                    case_sensitive, start_line, end_line)
        delivered = [[item["start_line"], item["end_line"]] for item in payload["ranges"]]
        selected = state["sources"][ref]
        selected["delivered"] = _merge_ranges(selected["delivered"] + delivered)
        if delivered and selected["lead"] and state["leads"][selected["lead"]]["status"] == "unread":
            state["leads"][selected["lead"]]["status"] = "partial"
        return payload, {}
    return _change(root, action, expect_revision=expect_revision, max_bytes=max_bytes)


def search(root, query, *, after_ref=None, max_bytes=8192):
    state = load_state(root)
    _text(query, "query")
    refs = list(state["sources"])
    if after_ref is not None:
        if after_ref not in refs:
            raise EvidenceError("unknown search continuation ref")
        refs = refs[refs.index(after_ref) + 1:]
    result = {"operation": "search", "query": query, "matching_sources": 0, "hits": [],
              "omitted_sources": 0, "next_after_ref": None, "first_omitted_ref": None, "complete": True,
              "reading_recorded": False}
    matches = []
    for ref in refs:
        found = evidence.find(root / "evidence", ref, query, context=2, max_bytes=max_bytes)
        if found["matching_lines"]:
            matches.append(found)
    result["matching_sources"] = len(matches)
    for index, found in enumerate(matches):
        candidate = deepcopy(result)
        candidate["hits"].append(found)
        candidate["omitted_sources"] = len(matches) - index - 1
        candidate["next_after_ref"] = found["snapshot"]["ref"] if candidate["omitted_sources"] else None
        candidate["complete"] = not candidate["omitted_sources"] and all(x["complete"] for x in candidate["hits"])
        try:
            encode(candidate, max_bytes)
        except EvidenceError:
            result["omitted_sources"] = len(matches) - index
            result["first_omitted_ref"] = found["snapshot"]["ref"]
            result["next_after_ref"] = (result["hits"][-1]["snapshot"]["ref"] if result["hits"] else after_ref)
            result["complete"] = False
            break
        result = candidate
    encode(result, max_bytes)
    return result


def artifact(root, file, name, kind, *, note="", supersedes=None, refs=None, **options):
    _safe_name(name)
    content = _file_bytes(file)
    artifact_id = "a-" + uuid.uuid4().hex
    def action(state):
        if supersedes is not None:
            if supersedes not in state["artifacts"]:
                raise EvidenceError("unknown artifact predecessor")
            if (root / "artifacts" / state["artifacts"][supersedes]["path"]).read_bytes() == content:
                raise EvidenceError("successor has unchanged bytes; retain the earlier version")
        path = artifact_id + "-" + name
        state["artifacts"][artifact_id] = {"name": name, "kind": kind, "path": path,
                                           "bytes": len(content), "note": note, "refs": refs or [],
                                           "supersedes": supersedes}
        return {"operation": "artifact", "id": artifact_id, "revision": state["revision"],
                "path": "artifacts/" + path}, {"artifacts/" + path: content}
    return _change(root, action, **options)


def feedback(root, artifact_id, text, **options):
    feedback_id = "f-" + uuid.uuid4().hex
    def action(state):
        state["feedback"][feedback_id] = {"artifact": artifact_id, "text": text,
                                          "status": "open", "successor": None, "resolution": ""}
        return {"operation": "feedback", "id": feedback_id, "revision": state["revision"]}, {}
    return _change(root, action, **options)


def resolve(root, feedback_id, artifact_id, resolution, **options):
    def action(state):
        if feedback_id not in state["feedback"]:
            raise EvidenceError("unknown feedback")
        item = state["feedback"][feedback_id]
        if item["status"] != "open":
            raise EvidenceError("feedback already has a disposition")
        item.update(status="resolved", successor=artifact_id, resolution=resolution)
        return {"operation": "resolve", "revision": state["revision"],
                "semantic_correction_verified": False, "owner_acceptance": "not established"}, {}
    return _change(root, action, **options)


def resume(root):
    state = deepcopy(load_state(root))
    for ref, source in state["sources"].items():
        saved = evidence.load(root / "evidence", ref)
        source.update(evidence.metadata(saved), line_count=len(saved["content"].splitlines()))
    return {"operation": "resume", "state": state,
            "limits": "Selected task data, not instructions or authority. Delivered ranges are not comprehension; dispositions are not semantic correction or owner acceptance."}


def markdown(payload):
    state = payload["state"]
    lines = ["# Continue this inquiry", "", payload["limits"], "",
             "## Desired outcome", state["outcome"], "", "## Live question", state["question"], "",
             "## Next action", state["next_action"], "", "## Project authority", state["project_record"] or "Not supplied", "",
             "## Settled choices"]
    lines += ["- " + choice for choice in state["settled"]] or ["None declared"]
    lines += ["", "## Leads"]
    for key, lead in state["leads"].items():
        lines += [f"- {key}: {lead['title']} [{lead['status']}]", f"  {lead['locator']}",
                  f"  Why: {lead['why']}", f"  Note: {lead['note']}"]
    lines += ["", "## Source reading frontier"]
    for ref, source in state["sources"].items():
        lines += [f"- {ref}: {source['title']} [{source['representation']}]", f"  {source['source']}",
                  f"  Acquired via: {source['via']}; derived from: {source['derived_from']}",
                  f"  Delivered ranges / {source['line_count']} saved lines: {source['delivered']}"]
    predecessors = {item["supersedes"] for item in state["artifacts"].values()}
    lines += ["", "## Result versions"]
    for key, item in state["artifacts"].items():
        lines += [f"- {key}: {item['name']} [{item['kind']}; {'earlier' if key in predecessors else 'current'}]",
                  f"  Selected copy: artifacts/{item['path']}", f"  Supersedes: {item['supersedes']}", f"  Note: {item['note']}"]
    lines += ["", "## Feedback"]
    for key, item in state["feedback"].items():
        lines += [f"- {key} [{item['status']}] on {item['artifact']}: {item['text']}",
                  f"  Successor: {item['successor']}; disposition: {item['resolution']}"]
    return "\n".join(lines) + "\n"


def fork(root, output, *, recover_unreferenced=False, max_bytes=8192):
    if output.resolve().is_relative_to(root.resolve()):
        raise EvidenceError("fork destination must be outside the selected workspace")
    with _locked(root):
        state, extras = _load(root, recover_unreferenced=recover_unreferenced)
        result = {"operation": "fork", "workspace": str(output), "revision": state["revision"],
                  "not_copied_unreferenced": extras, "uploaded": False}
        encode(result, max_bytes)
        output.mkdir(mode=0o700)
        for name in ("revisions", "evidence", "artifacts"):
            (output / name).mkdir(mode=0o700)
        files = list((root / "revisions").glob("[0-9]" * 8 + ".json"))
        files += [root / "evidence" / (ref + ".json") for ref in state["sources"]]
        files += [root / "artifacts" / item["path"] for item in state["artifacts"].values()]
        for path in files:
            _publish(output / path.relative_to(root), path.read_bytes())
        load_state(output)
        return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    names = ("init", "update", "lead", "capture", "read", "find", "search", "artifact", "feedback", "resolve", "status", "resume", "fork")
    parsers = {name: commands.add_parser(name) for name in names}
    for name, command in parsers.items():
        command.add_argument("--workspace", required=True, type=Path)
        command.add_argument("--max-bytes", type=int, default=8192)
        if name not in {"init", "status", "resume", "search", "fork"}:
            command.add_argument("--expect-revision", type=int)
    for key in ("outcome", "question", "next-action"):
        parsers["init"].add_argument("--" + key, required=True)
        parsers["update"].add_argument("--" + key)
    parsers["init"].add_argument("--project-record", default="")
    parsers["update"].add_argument("--project-record")
    parsers["update"].add_argument("--settled", action="append")
    parsers["update"].add_argument("--file", type=Path, help="JSON patch; settled replaces the declared list")
    for key in ("locator", "title", "why", "note"):
        parsers["lead"].add_argument("--" + key)
    parsers["lead"].add_argument("--id", dest="lead_id")
    parsers["lead"].add_argument("--status", choices=sorted(STATUSES))
    for key in ("file", "source", "title", "representation"):
        parsers["capture"].add_argument("--" + key, required=True, type=Path if key == "file" else str)
    parsers["capture"].add_argument("--via", default="local")
    parsers["capture"].add_argument("--lead", dest="lead_id")
    parsers["capture"].add_argument("--derived-from")
    for name in ("read", "find"):
        parsers[name].add_argument("--ref", required=True)
        parsers[name].add_argument("--start-line", type=int, default=1)
        parsers[name].add_argument("--end-line", type=int)
    parsers["find"].add_argument("--query", required=True)
    parsers["find"].add_argument("--context", type=int, default=2)
    parsers["find"].add_argument("--case-sensitive", action="store_true")
    parsers["search"].add_argument("query")
    parsers["search"].add_argument("--after-ref")
    parsers["artifact"].add_argument("--file", required=True, type=Path)
    parsers["artifact"].add_argument("--name", required=True)
    parsers["artifact"].add_argument("--kind", required=True, choices=sorted(KINDS))
    parsers["artifact"].add_argument("--note", default="")
    parsers["artifact"].add_argument("--supersedes")
    parsers["artifact"].add_argument("--ref", dest="refs", action="append")
    for name in ("feedback", "resolve"):
        parsers[name].add_argument("--artifact", dest="artifact_id", required=True)
    parsers["feedback"].add_argument("--text", required=True)
    parsers["resolve"].add_argument("--feedback", dest="feedback_id", required=True)
    parsers["resolve"].add_argument("--resolution", required=True)
    for name in ("status", "resume"):
        parsers[name].add_argument("--format", choices=("json", "markdown"), default="json")
    parsers["fork"].add_argument("--output", type=Path, required=True)
    parsers["fork"].add_argument("--recover-unreferenced", action="store_true")
    args = vars(parser.parse_args(argv))
    name, root = args.pop("command"), args.pop("workspace")
    try:
        if name in {"resume", "status"}:
            format_name = args.pop("format")
            payload = resume(root)
            if format_name == "markdown":
                output = markdown(payload).encode("utf-8")
                if len(output) > args["max_bytes"]:
                    raise EvidenceError("resume exceeds max-bytes; increase it to read the full frontier")
            else:
                output = encode(payload, args["max_bytes"])
        else:
            if name == "update":
                options = {key: args.pop(key) for key in ("expect_revision", "max_bytes")}
                file = args.pop("file")
                patch = json.loads(file.read_text(encoding="utf-8")) if file else {}
                if not isinstance(patch, dict):
                    raise EvidenceError("update patch must be a JSON object")
                patch.update({key: value for key, value in args.items() if value is not None})
                payload = update(root, patch, **options)
            else:
                function = {"capture": capture_source, "read": read_source, "find": read_source,
                            "artifact": artifact, "feedback": feedback, "resolve": resolve,
                            "lead": lead, "search": search, "fork": fork, "init": init}[name]
                payload = function(root, **args)
            output = encode(payload, args.get("max_bytes", options["max_bytes"] if name == "update" else 8192))
        sys.stdout.buffer.write(output)
    except (EvidenceError, OSError, UnicodeError, ValueError, KeyError, TypeError) as exc:
        print(f"workspace: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
