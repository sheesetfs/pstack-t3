"""Light rows from light.md and the light command."""


import sys


from _roles.base import RolesError
from _roles import seam


LIGHT_TITLE = "# Light mode reference"

# Other names a lead may use for a row, keyed by its label in lower case. A name here still prints one row.
ALIASES = {
    "architect runners": ("architect runner",),
    "arena cross-judge": ("arena judge",),
}


def light_path():
    """The rendered tree's light.md, or the source checkout's."""
    root = seam.TREE_ROOT
    candidates = (root / "pstack-runtime" / "light.md", root / "t3" / "added" / "pstack-runtime" / "light.md")
    found = next((candidate for candidate in candidates if candidate.is_file()), None)
    if found is None:
        raise RolesError("no light.md: " + ", ".join(str(candidate) for candidate in candidates))
    return found


def canonical_label(cell):
    """The label a lead types for a row, with the table's code ticks and padding gone."""
    return " ".join(cell.replace("`", "").split())


def light_rows(text):
    """(label, behavior) for each row of the first table after the title, in table order."""
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
        rows.append((canonical_label(cells[0]), cells[1]))
    if not rows:
        raise RolesError("light.md has no light rows")
    return rows


def labels(rows):
    return [label for label, _behavior in rows]


def row_for(rows, spawn):
    """The one row whose label or alias matches the query exactly, or None."""
    query = canonical_label(spawn).casefold()
    if not query:
        return None
    for label, behavior in rows:
        names = (label, *ALIASES.get(label.casefold(), ()))
        if query in {name.casefold() for name in names}:
            return (label, behavior)
    return None


def command_light(args):
    path = light_path()
    rows = light_rows(path.read_text(encoding="utf-8"))
    if args.spawn is None:
        print(f"Light rows in {path}: " + "; ".join(labels(rows)))
        print("Run roles.py light --spawn \"<label>\" before each light spawn and run the row it prints.")
        return 0
    row = row_for(rows, args.spawn)
    if row is None:
        print(f"No light row matches '{args.spawn}'.", file=sys.stderr)
        print("Rerun with one of these labels: " + "; ".join(labels(rows)), file=sys.stderr)
        return 2
    label, behavior = row
    print(f"{label}: {behavior}")
    print(f"Links are relative to {path}.")
    return 0


__all__ = [
    "ALIASES",
    "LIGHT_TITLE",
    "light_path",
    "canonical_label",
    "light_rows",
    "labels",
    "row_for",
    "command_light",
]
