"""Tests for roles.py light, which prints the light row for one spawn."""

if __package__ in (None, ""):
    import sys
    from pathlib import Path

    _repo_root = Path(__file__).resolve().parent
    while _repo_root != _repo_root.parent and not (_repo_root / "tests" / "isolation.py").is_file():
        _repo_root = _repo_root.parent
    sys.path.insert(0, str(_repo_root))
from tests import isolation

isolation.install()

import unittest
from tests import in_process
from .support import ROOT, roles, setUpModule  # noqa: F401

LIGHT = ROOT / "t3/added/pstack-runtime/light.md"


def run_light(*args):
    return in_process.invoke(in_process.Invocation(program=ROOT / "t3/scripts/roles.py", argv=("light", *args)))


class LightRowsTest(unittest.TestCase):
    def test_every_row_of_light_md_parses(self):
        rows = roles.light_rows(LIGHT.read_text())
        spawns = [spawn for spawn, _behavior in rows]
        self.assertEqual(spawns[0], "how")
        self.assertIn("Code delegate", spawns)
        self.assertEqual(spawns[-1], "Setup smoke test")
        self.assertEqual(len(spawns), len(set(spawns)))
        self.assertTrue(all(behavior and not behavior.startswith("|") for _spawn, behavior in rows))

    def test_a_label_or_an_alias_matches_its_row_exactly(self):
        rows = roles.light_rows(LIGHT.read_text())

        def row(query):
            found = roles.row_for(rows, query)
            return None if found is None else found[0]

        self.assertEqual(row("code delegate"), "Code delegate")
        self.assertEqual(row("Code Delegate"), "Code delegate")
        self.assertEqual(row("how"), "how")
        self.assertEqual(row("`how`"), "how")
        self.assertEqual(row("  architect runners "), "architect runners")
        self.assertEqual(row("arena cross-judge"), "Arena cross-judge")
        self.assertIsNone(row("architect"))
        self.assertIsNone(row("code delegate for feature"))
        self.assertIsNone(row("  "))

    def test_the_alias_names_belong_to_real_rows(self):
        rows = roles.light_rows(LIGHT.read_text())
        known = {label.casefold() for label in roles.labels(rows)}
        self.assertEqual(sorted(set(roles.ALIASES) - known), [])

    def test_an_alias_prints_the_row_it_names(self):
        completed = run_light("--spawn", "arena judge")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout.splitlines()[0], f"Arena cross-judge: {dict(roles.light_rows(LIGHT.read_text()))['Arena cross-judge']}")
        completed = run_light("--spawn", "architect runner")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Spawn one runner on the first", completed.stdout)

    def test_command_prints_the_row_verbatim(self):
        completed = run_light("--spawn", "code delegate")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        row = dict(roles.light_rows(LIGHT.read_text()))["Code delegate"]
        self.assertEqual(completed.stdout.splitlines()[0], f"Code delegate: {row}")
        self.assertIn(f"Links are relative to {LIGHT}.", completed.stdout)

    def test_an_unmatched_spawn_is_refused_with_every_label(self):
        completed = run_light("--spawn", "banana split")
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(completed.stdout, "")
        self.assertIn("No light row matches 'banana split'.", completed.stderr)
        self.assertIn("Rerun with one of these labels: ", completed.stderr)
        for label in roles.labels(roles.light_rows(LIGHT.read_text())):
            self.assertIn(label, completed.stderr)

    def test_no_spawn_lists_the_rows(self):
        completed = run_light()
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Setup smoke test", completed.stdout)
        self.assertIn('roles.py light --spawn "<label>"', completed.stdout)

    def test_a_file_without_rows_is_an_error(self):
        with self.assertRaises(roles.RolesError):
            roles.light_rows("# Light mode reference\n\nNo table.\n")
        with self.assertRaises(roles.RolesError):
            roles.light_rows("| Spawn | Light behavior |\n| --- | --- |\n| a | b |\n")


if __name__ == "__main__":
    unittest.main()
