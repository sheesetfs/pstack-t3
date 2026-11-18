"""The harness hooks pstack-t3 owns in a harness settings file.

One `Hook` is one registry entry: the harness, its settings file, the event, the matcher, and the exact command
string pstack-t3 installs. The install manifest records a row per hook with the checkout that recorded it, the way a
link row records its checkout, so install and uninstall know what they own.

Install adds the command to the event list only when no identical command is in the file, and writes the file
atomically. Uninstall removes that exact command and the containers it empties, and leaves every other entry and
key as the file holds it. A file that will not parse refuses the run before anything is written. A checkout whose
generated tree carries no hook script manages no hook.
"""

from __future__ import annotations

import json
import os
import shlex
from dataclasses import dataclass
from pathlib import Path

from . import records

SETTINGS_NAME = "settings.json"

ENTRY_TYPE = "command"

SCRIPT = ("pstack-runtime", "session-start.sh")

# One row per harness hook the installer manages: harness, event, matcher.
REGISTRY = (
    ("claude", "SessionStart", "startup|resume|clear|compact"),
)


@dataclass(frozen=True)
class Hook:
    """One harness hook pstack-t3 manages: its settings file, the event, the matcher, and the exact command."""

    harness: str
    file: str
    event: str
    matcher: str
    command: str


def script(root):
    """The hook script this checkout's generated tree carries."""
    return os.path.join(root, "skills", *SCRIPT)


def built(root):
    """Whether this checkout's generated tree carries the hook script."""
    return os.path.isfile(script(root))


def managed(dirs, root):
    """The hooks this run manages, in registry order. `dirs` maps a harness to its config directory."""
    command = shlex.join(("sh", script(root)))
    return tuple(
        Hook(harness, os.path.join(dirs[harness], SETTINGS_NAME), event, matcher, command)
        for harness, event, matcher in REGISTRY
        if harness in dirs
    )


def row(hook, root):
    """The manifest row that records a hook this checkout installs."""
    return {
        "harness": hook.harness,
        "file": hook.file,
        "event": hook.event,
        "matcher": hook.matcher,
        "command": hook.command,
        "checkout": root,
    }


def owner(raw):
    """The checkout a manifest row records, or None when the row records none."""
    found = raw.get("checkout") if isinstance(raw, dict) else None
    return found if isinstance(found, str) else None


def parse(raw):
    """The Hook a manifest row holds, or None when the row is not one."""
    if not isinstance(raw, dict):
        return None
    values = [raw.get(key) for key in ("harness", "file", "event", "matcher", "command")]
    if not all(isinstance(value, str) and value for value in values):
        return None
    return Hook(*values)


def describe(hook):
    """The words a report uses for one hook."""
    return f"{hook.event} hook in {hook.file}"


def settings(file):
    """The settings object at `file`, or {} when no file is there. A file that will not parse raises Unreadable."""
    return records.read_object(Path(file)) or {}


def groups(data, hook):
    """The matcher groups under `hook.event`. Raise Unreadable when the file holds another shape there."""
    hooks = data.get("hooks", {})
    if not isinstance(hooks, dict):
        raise records.Unreadable(f"{hook.file}: hooks is not an object; fix or move it and rerun")
    found = hooks.get(hook.event, [])
    if not isinstance(found, list):
        raise records.Unreadable(f"{hook.file}: hooks.{hook.event} is not a list; fix or move it and rerun")
    for group in found:
        if not isinstance(group, dict) or not isinstance(group.get("hooks", []), list):
            raise records.Unreadable(
                f"{hook.file}: hooks.{hook.event} holds an entry that is not an object with a hooks list; "
                "fix or move it and rerun")
    return found


def matching(data, hook):
    """The entries under `hook.event` that hold `hook.command`, in file order."""
    return [
        entry
        for group in groups(data, hook)
        for entry in group["hooks"]
        if isinstance(entry, dict) and entry.get("command") == hook.command
    ]


def add(data, hook):
    """Add `hook`'s command under its event. Return False when an identical command is already there."""
    if matching(data, hook):
        return False
    data.setdefault("hooks", {}).setdefault(hook.event, []).append(
        {"matcher": hook.matcher, "hooks": [{"type": ENTRY_TYPE, "command": hook.command}]}
    )
    return True


def remove(data, hook):
    """Remove every entry that holds `hook.command`, with the list and the hooks object that empties. Return whether `data` changed."""
    kept = []
    changed = False
    for group in groups(data, hook):
        entries = group["hooks"]
        rest = [entry for entry in entries if not (isinstance(entry, dict) and entry.get("command") == hook.command)]
        if len(rest) == len(entries):
            kept.append(group)
            continue
        changed = True
        if rest:
            kept.append({**group, "hooks": rest})
    if not changed:
        return False
    if kept:
        data["hooks"][hook.event] = kept
    else:
        del data["hooks"][hook.event]
        if not data["hooks"]:
            del data["hooks"]
    return True


def install(hook):
    """Add `hook` to its settings file. Write nothing when the file already holds the command."""
    data = settings(hook.file)
    if add(data, hook):
        write(hook.file, data)


def uninstall(hook):
    """Remove `hook`'s command from its settings file. Make no file when there is none."""
    data = settings(hook.file)
    if remove(data, hook):
        write(hook.file, data)


def write(file, data):
    """Write `data` to `file` as JSON, through a temporary file in that directory and a rename."""
    records.atomic_write(Path(os.path.dirname(file)), os.path.basename(file), json.dumps(data, indent=2) + "\n")
