import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILLS = ["compete-cron-builder", "execution-cron-builder", "learn-cron-builder",
          "optimization-cron-builder", "looper-cron-builder"]


def lint(root):
    env = {**os.environ, "B3EHIVE_ROOT": str(root)}
    return subprocess.run([sys.executable, str(ROOT / "scripts" / "lint_skills.py")],
                          env=env, capture_output=True, text=True)


class LintTests(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        for d in SKILLS + ["core"]:
            shutil.copytree(ROOT / d, self.tmp / d)
        self.compete = self.tmp / "compete-cron-builder" / "SKILL.md"

    def append(self, text):
        self.compete.write_text(self.compete.read_text() + "\n" + text + "\n")

    def test_repository_passes(self):
        self.assertEqual(lint(ROOT).returncode, 0)

    def test_forbidden_subject_verb(self):
        self.append("Workers accept their own patches.")
        result = lint(self.tmp)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("lexicon violation", result.stderr)

    def test_restating_core(self):
        self.append("Each worker runs alone in its own task root. Every model process and request counts, so nested agents are declared and counted.")
        self.append("Two stalls: replan. Each attempt submits a receipt and reports `ADVANCED`, `STALLED`, or `REGRESSED`.")
        result = lint(self.tmp)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("restates a core/loop sentence", result.stderr)

    def test_loop_drift(self):
        (self.tmp / "looper-cron-builder" / "loop.md").write_text("# changed\n")
        result = lint(self.tmp)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("run scripts/sync_loop.sh", result.stderr)

    def test_unquoted_colon_description(self):
        text = self.compete.read_text().replace("Runs bounded proposal competitions with", "Runs competitions: with", 1)
        self.compete.write_text(text)
        self.assertNotEqual(lint(self.tmp).returncode, 0)

    def test_cross_skill_path(self):
        self.append("See `../looper-cron-builder/loop.md`.")
        self.assertNotEqual(lint(self.tmp).returncode, 0)


if __name__ == "__main__":
    unittest.main()
