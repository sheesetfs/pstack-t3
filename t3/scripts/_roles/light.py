"""Light rows from light.md and the light command."""


import re


from _roles.base import RolesError
from _roles import seam


LIGHT_TITLE = "# Light mode reference"


def light_path():
    """The rendered tree's light.md, or the source checkout's."""
    root = seam.TREE_ROOT
    candidates = (root / "pstack-runtime" / "light.md", root / "t3" / "added" / "pstack-runtime" / "light.md")
    found = next((candidate for candidate in candidates if candidate.is_file()), None)
    if found is None:
        raise RolesError("no light.md: " + ", ".join(str(candidate) for candidate in candidates))
    return found


def light_rows(text):
    """(spawn, behavior) for each row of the first table after the title, in table order."""
    if LIGHT_TITLE not in text:
        raise RolesError(f"light.md has no '{LIGHT_TITLE}' title")
    rows = []
    for line in text.split(LIGHT_TITLE, 1)[1].splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            if rows:
                break
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|", 1)]
        if len(cells) != 2 or cells[0] == "Spawn" or not cells[0].strip("-: "):
            continue
        rows.append((cells[0], cells[1]))
    if not rows:
        raise RolesError("light.md has no light rows")
    return rows


def _words(text):
    return re.findall(r"[a-z0-9][a-z0-9-]*", text.lower())


def matching_rows(rows, spawn):
    """Rows whose spawn words all appear in the query, or whose spawn holds every query word."""
    query = set(_words(spawn))
    if not query:
        return []
    return [row for row in rows if set(_words(row[0])) <= query or query <= set(_words(row[0]))]


def command_light(args):
    path = light_path()
    rows = light_rows(path.read_text(encoding="utf-8"))
    names = "; ".join(spawn for spawn, _behavior in rows)
    if args.spawn is None:
        print(f"Light rows in {path}: {names}")
        print("Run roles.py light --spawn <name> before each light spawn and run the row it prints.")
        return 0
    found = matching_rows(rows, args.spawn)
    if not found:
        print(f"No light row names '{args.spawn}'. That spawn runs as its skill or playbook says, under the runtime's Light behavior rules.")
        print(f"Rows: {names}")
        return 0
    for spawn, behavior in found:
        print(f"{spawn}: {behavior}")
    print(f"Links are relative to {path}.")
    return 0


__all__ = [
    "LIGHT_TITLE",
    "light_path",
    "light_rows",
    "matching_rows",
    "command_light",
]
