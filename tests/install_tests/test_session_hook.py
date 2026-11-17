"""The Claude Code session-start hook the installer manages."""

if __package__ in (None, ""):
    import sys
    from pathlib import Path

    _repo_root = Path(__file__).resolve().parent
    while _repo_root != _repo_root.parent and not (_repo_root / "tests" / "isolation.py").is_file():
        _repo_root = _repo_root.parent
    sys.path.insert(0, str(_repo_root))
from tests import isolation

isolation.install()

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from .support import ROOT
from .support import _env
from .support import _run
from .support import legacy_file
from .support import run_install
from .support import setUpModule

SCRIPT = ROOT / "skills/pstack-runtime/session-start.sh"

CONTEXT = ROOT / "skills/pstack-runtime/session-start-context.md"

MATCHER = "startup|resume|clear|compact"

COMMAND = "sh " + str(SCRIPT)

FOREIGN = {"matcher": "startup", "hooks": [{"type": "command", "command": "echo foreign"}]}


def entries(document, command=COMMAND):
    """Every hook object under SessionStart that holds `command`."""
    return [
        entry
        for group in document.get("hooks", {}).get("SessionStart", [])
        for entry in group.get("hooks", [])
        if entry.get("command") == command
    ]


class SessionHookTest(unittest.TestCase):
    def setUp(self):
        self.wrapper = tempfile.TemporaryDirectory()

        self.home = Path(os.path.realpath(self.wrapper.name))

    def tearDown(self):
        self.wrapper.cleanup()

    def settings_path(self):
        return self.home / ".claude/settings.json"

    def settings(self):
        return json.loads(self.settings_path().read_text())

    def write_settings(self, document):
        self.settings_path().parent.mkdir(parents=True, exist_ok=True)
        self.settings_path().write_text(json.dumps(document, indent=2) + "\n")

    def install(self, *args):
        completed = run_install(self.home, "install", "--harness", "claude", *args)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        return completed

    def uninstall(self, *args):
        return run_install(self.home, "uninstall", "--harness", "claude", *args)

    def test_install_adds_the_command_once_and_a_second_install_changes_nothing(self):
        first = self.install()
        self.assertIn(f"added the SessionStart hook in {self.settings_path()}", first.stdout)
        document = self.settings()
        self.assertEqual(len(entries(document)), 1)
        self.assertEqual(document["hooks"]["SessionStart"][0]["matcher"], MATCHER)
        self.assertEqual(entries(document), [{"type": "command", "command": COMMAND}])
        recorded = json.loads(legacy_file(self.home).read_text())["hooks"]
        self.assertEqual(recorded, [{"harness": "claude", "file": str(self.settings_path()), "event": "SessionStart",
                                     "matcher": MATCHER, "command": COMMAND}])
        before = self.settings_path().read_bytes()
        again = self.install()
        self.assertNotIn("added the SessionStart hook", again.stdout)
        self.assertIn("already installed", again.stdout)
        self.assertEqual(self.settings_path().read_bytes(), before)

    def test_uninstall_removes_only_its_own_entry(self):
        document = {"permissions": {"allow": ["Bash(ls:*)"]}, "hooks": {"SessionStart": [FOREIGN]}}
        self.write_settings(document)
        self.install()
        self.assertEqual(len(entries(self.settings())), 1)

        completed = self.uninstall()

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(self.settings(), document)

    def test_uninstall_leaves_a_foreign_hook_in_the_same_group(self):
        self.install()
        document = self.settings()
        document["hooks"]["SessionStart"][0]["hooks"].append(dict(FOREIGN["hooks"][0]))
        self.write_settings(document)

        completed = self.uninstall()

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(self.settings(), {"hooks": {"SessionStart": [{"matcher": MATCHER, "hooks": [dict(FOREIGN["hooks"][0])]}]}})

    def test_a_file_that_is_not_json_refuses_and_changes_nothing(self):
        self.settings_path().parent.mkdir(parents=True)
        self.settings_path().write_text("{ not json")

        completed = run_install(self.home, "install", "--harness", "claude")

        self.assertEqual(completed.returncode, 1)
        self.assertIn(f"{self.settings_path()} is not valid JSON", completed.stderr)
        self.assertEqual(self.settings_path().read_text(), "{ not json")
        self.assertFalse((self.home / ".claude/skills/poteto-mode").exists())
        self.assertFalse(legacy_file(self.home).exists())

    def test_dry_run_prints_the_change_and_writes_nothing(self):
        completed = self.install("--dry-run")

        self.assertIn(f"would add the SessionStart hook in {self.settings_path()}", completed.stdout)
        self.assertFalse(self.settings_path().exists())
        self.assertFalse(legacy_file(self.home).exists())
        second = self.install("--dry-run")
        self.assertIn(f"would add the SessionStart hook in {self.settings_path()}", second.stdout)

    def test_doctor_names_a_missing_a_duplicated_and_a_stale_entry(self):
        self.install()
        document = self.settings()
        self.write_settings({"hooks": {"SessionStart": []}})

        missing = run_install(self.home, "doctor", "--harness", "claude")

        self.assertEqual(missing.returncode, 0, missing.stdout + missing.stderr)
        self.assertIn(f"hook SessionStart in {self.settings_path()}: no entry holds the command pstack-t3 records ({COMMAND})",
                      missing.stdout)
        self.assertIn('run "python3 scripts/install.py install --harness claude" to add it again', missing.stdout)

        entry = {"matcher": MATCHER, "hooks": [{"type": "command", "command": COMMAND}]}
        self.write_settings({"hooks": {"SessionStart": [entry, entry]}})

        twice = run_install(self.home, "doctor", "--harness", "claude")

        self.assertEqual(twice.returncode, 0, twice.stdout + twice.stderr)
        self.assertIn("2 entries hold the command pstack-t3 records", twice.stdout)

        self.write_settings(document)
        recorded = json.loads(legacy_file(self.home).read_text())
        recorded["hooks"][0]["command"] = "sh /gone/session-start.sh"
        legacy_file(self.home).write_text(json.dumps(recorded, indent=2) + "\n")
        self.write_settings({"hooks": {"SessionStart": [
            {"matcher": MATCHER, "hooks": [{"type": "command", "command": "sh /gone/session-start.sh"}]}]}})

        stale = run_install(self.home, "doctor", "--harness", "claude")

        self.assertEqual(stale.returncode, 0, stale.stdout + stale.stderr)
        self.assertIn("pstack-t3 records the command sh /gone/session-start.sh", stale.stdout)
        self.assertIn(f"and now installs {COMMAND}", stale.stdout)
        self.assertIn(f'run "python3 scripts/install.py uninstall --harness claude", then ', stale.stdout)

    def test_doctor_is_quiet_after_install(self):
        self.install()

        completed = run_install(self.home, "doctor", "--harness", "claude")

        self.assertEqual(completed.returncode, 0, completed.stdout)

    def test_project_scope_leaves_the_settings_file_alone(self):
        completed = run_install(self.home, "install", "--harness", "claude", "--project", str(self.home))

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertFalse(self.settings_path().exists())

    def test_claude_config_dir_decides_the_settings_file(self):
        configured = self.home / "claude-config"
        completed = _run(self.home, ROOT, ("install", "--harness", "claude"), env={"CLAUDE_CONFIG_DIR": str(configured)})

        self.assertEqual(completed.returncode, 0, completed.stderr)
        document = json.loads((configured / "settings.json").read_text())
        self.assertEqual(len(entries(document)), 1)
        self.assertFalse(self.settings_path().exists())

    def hook(self, *args):
        return subprocess.run(["sh", str(SCRIPT), *args], capture_output=True, text=True, env=_env(self.home),
                              cwd=str(self.home))

    def test_the_hook_prints_the_note_and_a_false_session_hook_silences_it(self):
        on = self.hook()

        self.assertEqual(on.returncode, 0, on.stderr)
        self.assertEqual(on.stdout, CONTEXT.read_text())

        roles = self.home / ".config/pstack-t3/roles.json"
        roles.parent.mkdir(parents=True)
        roles.write_text(json.dumps({"sessionHook": False}) + "\n")

        off = self.hook()

        self.assertEqual(off.returncode, 0, off.stderr)
        self.assertEqual(off.stdout, "")

    def test_an_unreadable_roles_file_leaves_the_note_on(self):
        roles = self.home / ".config/pstack-t3/roles.json"
        roles.parent.mkdir(parents=True)
        roles.write_text(json.dumps({"roles": {}}) + "\n")

        printed = self.hook()

        self.assertEqual(printed.returncode, 0, printed.stderr)
        self.assertEqual(printed.stdout, CONTEXT.read_text())
