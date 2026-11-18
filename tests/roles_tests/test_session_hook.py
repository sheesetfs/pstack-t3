"""The roles file's sessionHook key, which the Claude Code session-start hook reads."""

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
import tempfile
import unittest
from .support import Repo, setUpModule


PROVIDER = "opencode-go"
MODEL = "deepseek-v4.1-flash"
PARENT = f"{PROVIDER}/{MODEL}"


def catalog():
    return {"providers": [{
        "providerInstanceId": PROVIDER,
        "driverKind": "opencode",
        "canRunChildTask": True,
        "constraints": [],
        "models": [{"id": MODEL, "options": [], "cost": 0}],
    }]}


class SessionHookKeyTest(unittest.TestCase):
    def repo(self, directory, document):
        repo = Repo(directory)
        path = repo.directory / "catalog.json"
        repo.put(path, catalog())
        repo.put(repo.user, document)
        return repo, path

    def validate(self, document):
        with tempfile.TemporaryDirectory() as directory:
            repo, path = self.repo(directory, document)
            return repo.run("validate", "--catalog", str(path), "--parent", PARENT)

    def test_validate_accepts_a_true_or_false_session_hook(self):
        for value in (True, False):
            with self.subTest(value=value):
                completed = self.validate({"roles": {}, "sessionHook": value})
                self.assertEqual(completed.returncode, 0, completed.stderr)
                self.assertEqual(completed.stdout, "ok\n")
                self.assertEqual(completed.stderr, "")

    def test_validate_rejects_a_session_hook_that_is_not_a_boolean(self):
        for value in ("no", 0, 1, [], None):
            with self.subTest(value=value):
                completed = self.validate({"roles": {}, "sessionHook": value})
                self.assertEqual(completed.returncode, 2, completed.stdout)
                self.assertEqual(completed.stdout, "")
                self.assertIn("sessionHook must be true or false", completed.stderr)

    def test_write_keeps_the_session_hook_key(self):
        with tempfile.TemporaryDirectory() as directory:
            repo, path = self.repo(directory, {"roles": {}, "sessionHook": False})

            written = repo.run("write", "--catalog", str(path), "--parent", PARENT, "--set", f"bug-fix={PARENT}")

            self.assertEqual(written.returncode, 0, written.stderr)
            kept = json.loads(repo.user.read_text())
            self.assertIs(kept["sessionHook"], False)
            self.assertEqual(kept["roles"], {"bug-fix": [{"providerInstanceId": PROVIDER, "model": MODEL}]})
