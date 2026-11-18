"""Tests for roles.py gate-brief, which prints the gate review brief."""

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
from tests.pstack_t3.support import GATE_CONTRACT
from .support import ROOT, roles, setUpModule  # noqa: F401

HEAD = "a" * 40
PREVIOUS = "b" * 40


def run_gate(*args):
    return in_process.invoke(in_process.Invocation(program=ROOT / "t3/scripts/roles.py", argv=("gate-brief", *args)))


def persona(name):
    text = (ROOT / "t3/agents" / f"{name}.md").read_text()
    lines = text.splitlines(keepends=True)
    fences = [index for index, line in enumerate(lines) if line.strip() == "---"]
    return "".join(lines[fences[1] + 1:]).strip()


class GateBriefTest(unittest.TestCase):
    def brief(self, *args):
        completed = run_gate("--head", HEAD, *args)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stderr, "")
        return completed.stdout

    def test_contract_matches_the_literal(self):
        self.assertEqual(roles.GATE_CONTRACT, GATE_CONTRACT)

    def test_round_one_reads_the_whole_diff_then_persona_then_contract(self):
        text = self.brief("--base", "origin/main")
        self.assertIn(f"`git diff origin/main...{HEAD}`", text)
        body = persona("comment-sicko")
        self.assertIn(body + "\n\n" + GATE_CONTRACT, text)
        self.assertLess(text.index("Apply the comment rules below"), text.index(body))
        self.assertTrue(text.rstrip("\n").endswith(roles.WEAK_EVIDENCE))
        self.assertNotIn("FOCUS", text)
        self.assertNotIn("same-family", text)

    def test_later_round_reads_the_fix_diff_with_the_round_rules(self):
        text = self.brief("--previous-sha", PREVIOUS, "--previous-review", "reports/r-1.md")
        self.assertIn(f"`git diff {PREVIOUS}...{HEAD}`", text)
        self.assertIn("The previous round's review is reports/r-1.md.", text)
        rules = (ROOT / "t3/added/brigade/verdict-protocol.md").read_text()
        rules = rules.split("\n## Rounds after the first\n", 1)[1].split("\n## ", 1)[0].strip()
        self.assertIn("FOCUS\n" + rules + "\n", text)
        self.assertLess(text.index("FOCUS"), text.index(GATE_CONTRACT))

    def test_optional_lines_follow_the_contract(self):
        text = self.brief("--base", "main", "--design", "/tmp/sketch-b.md", "--trail", "/tmp/log.md",
                          "--thread", "thread-1", "--same-family")
        after = text.split(GATE_CONTRACT, 1)[1]
        self.assertIn("The chosen design is /tmp/sketch-b.md.", after)
        self.assertIn("decision trail at /tmp/log.md in thread thread-1", after)
        self.assertIn("audit checks on it yourself with t3_thread_read", after)
        self.assertTrue(after.rstrip("\n").endswith("Write same-family beside the verifier in your final line."))

    def test_bad_arguments_are_refused(self):
        for args, message in (
            (("--head", "abc1234", "--base", "main"), "--head needs a full commit SHA"),
            (("--head", HEAD), "round one needs --base"),
            (("--head", HEAD, "--previous-sha", PREVIOUS), "round one needs --base"),
            (("--head", HEAD, "--base", "main", "--previous-sha", PREVIOUS), "not both"),
            (("--head", HEAD, "--previous-sha", "short", "--previous-review", "r.md"), "--previous-sha needs a full commit SHA"),
            (("--head", HEAD, "--base", "main", "--trail", "/tmp/log.md"), "--trail and --thread go together"),
        ):
            with self.subTest(args=args):
                completed = run_gate(*args)
                self.assertEqual(completed.returncode, 2)
                self.assertEqual(completed.stdout, "")
                self.assertIn(message, completed.stderr)


if __name__ == "__main__":
    unittest.main()
