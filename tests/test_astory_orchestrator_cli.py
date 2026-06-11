import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CLI = REPO_ROOT / "scripts" / "astory_orchestrator_cli.py"


def _run(*args, cwd=REPO_ROOT):
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )


class OrchestratorCliTests(unittest.TestCase):
    def test_spine_command_prints_32_states(self):
        result = _run("spine")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(len(payload), 32)
        self.assertEqual(payload[0]["name"], "INIT_RUN")

    def test_validate_spine_command_ok(self):
        result = _run("validate-spine")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)["ok"])

    def test_init_then_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            init = _run("--repo-root", tmp, "init", "--run-id", "demo")
            self.assertEqual(init.returncode, 0, init.stderr)
            self.assertEqual(json.loads(init.stdout)["status"], "created")

            status = _run("--repo-root", tmp, "status", "--run-id", "demo")
            self.assertEqual(status.returncode, 0, status.stderr)
            body = json.loads(status.stdout)
            self.assertEqual(body["current_state"], "INIT_RUN")
            self.assertEqual(body["next_state"], "PARSE_CREATIVE_INPUT")

    def test_init_refuses_existing_without_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(
                _run("--repo-root", tmp, "init", "--run-id", "demo").returncode, 0
            )
            second = _run("--repo-root", tmp, "init", "--run-id", "demo")
            self.assertEqual(second.returncode, 1)
            self.assertEqual(json.loads(second.stdout)["status"], "exists")

    def test_status_without_state_returns_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = _run("--repo-root", tmp, "status", "--run-id", "demo")
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout)["status"], "no_state")


if __name__ == "__main__":
    unittest.main()
