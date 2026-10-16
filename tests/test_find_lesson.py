import contextlib
import io
import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "learn-cron-builder" / "scripts"))
import find_lesson as fl  # noqa: E402

HEADER = "\t".join(fl.FIELDS)
ROWS = [
    ["L-001", "lesson", "receipt id dropped by follow-up command", "commit a1b2", "", "carry the receipt id through every follow-up", "rerun settle check", "stop when receipt is bound", "single host", "execution", "applied", "helpful"],
    ["I-002", "incident", "truncated listing read as proof of absence", "log 2026-10-01", "display cap", "page through the full listing", "", "", "", "learn", "", ""],
    ["I-003", "incident", "stale lease blocks scheduler refill", "ticket 7", "missing liveness proof", "prove owner death before release", "", "", "", "looper", "not_applied", "unknown"],
]


class FindLessonTests(unittest.TestCase):
    def setUp(self):
        self.ledger = pathlib.Path(tempfile.mkdtemp()) / "lessons.tsv"
        self.ledger.write_text(HEADER + "\n" + "\n".join("\t".join(r) for r in ROWS) + "\n")

    def call(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = fl.main(["--ledger", str(self.ledger), *args])
        return code, out.getvalue()

    def test_search_ranks_and_bounds(self):
        code, out = self.call("search", "lease refill blocked")
        self.assertEqual(code, 0)
        results = json.loads(out)["results"]
        self.assertEqual(results[0]["id"], "I-003")
        self.assertNotIn("action", results[0])

    def test_exact_id_ranks_first(self):
        code, out = self.call("search", "I-002 receipt")
        self.assertEqual(json.loads(out)["results"][0]["id"], "I-002")

    def test_show_returns_full_row(self):
        code, out = self.call("show", "L-001")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["stop"], "stop when receipt is bound")

    def test_activation_requires_recall_at_use_site(self):
        self.assertEqual(self.call("activate", "L-001", "receipt follow-up command")[0], 0)
        self.assertEqual(self.call("activate", "L-001", "gpu clocks drift")[0], 1)

    def test_check_passes_valid_ledger(self):
        self.assertEqual(self.call("check")[0], 0)

    def test_check_rejects_helpful_without_application(self):
        bad = ROWS[2][:]
        bad[-1] = "helpful"
        self.ledger.write_text(HEADER + "\n" + "\t".join(bad) + "\n")
        self.assertEqual(self.call("check")[0], 1)

    def test_check_requires_lesson_fields(self):
        bad = ROWS[0][:]
        bad[6] = ""
        self.ledger.write_text(HEADER + "\n" + "\t".join(bad) + "\n")
        self.assertEqual(self.call("check")[0], 1)


if __name__ == "__main__":
    unittest.main()
