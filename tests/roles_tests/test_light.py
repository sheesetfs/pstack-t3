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
        self.assertEqual(spawns[0], "`how`")
        self.assertIn("Code delegate", spawns)
        self.assertEqual(spawns[-1], "Setup smoke test")
        self.assertEqual(len(spawns), len(set(spawns)))
        self.assertTrue(all(behavior and not behavior.startswith("|") for _spawn, behavior in rows))

    def test_a_spawn_matches_its_row_by_words(self):
        rows = roles.light_rows(LIGHT.read_text())

        def names(query):
            return [spawn for spawn, _behavior in roles.matching_rows(rows, query)]

        self.assertEqual(names("code delegate"), ["Code delegate"])
        self.assertEqual(names("Code Delegate for feature"), ["Code delegate"])
        self.assertEqual(names("how explainer"), ["`how`"])
        self.assertEqual(names("architect"), ["`architect` grounding", "`architect` runners"])
        self.assertEqual(names("comment sicko"), ["Comment Sicko", "Comment Sicko follow-ups"])
        self.assertEqual(names("swarm worker"), ["`swarm`"])
        self.assertEqual(names("gate review"), [])
        self.assertEqual(names("  "), [])

    def test_command_prints_the_row_verbatim(self):
        completed = run_light("--spawn", "code delegate")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        row = dict(roles.light_rows(LIGHT.read_text()))["Code delegate"]
        self.assertEqual(completed.stdout.splitlines()[0], f"Code delegate: {row}")
        self.assertIn(f"Links are relative to {LIGHT}.", completed.stdout)

    def test_unmatched_spawn_names_the_rows(self):
        completed = run_light("--spawn", "gate review")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertTrue(completed.stdout.startswith("No light row names 'gate review'."))
        self.assertIn("Run roles.py light with no --spawn to list the rows.", completed.stdout)
        self.assertNotIn("`why`", completed.stdout)

    def test_no_spawn_lists_the_rows(self):
        completed = run_light()
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Setup smoke test", completed.stdout)
        self.assertIn("roles.py light --spawn <name>", completed.stdout)

    def test_a_file_without_rows_is_an_error(self):
        with self.assertRaises(roles.RolesError):
            roles.light_rows("# Light mode reference\n\nNo table.\n")
        with self.assertRaises(roles.RolesError):
            roles.light_rows("| Spawn | Light behavior |\n| --- | --- |\n| a | b |\n")


if __name__ == "__main__":
    unittest.main()
