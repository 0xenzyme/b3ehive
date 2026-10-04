import contextlib
import io
import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "compete-cron-builder" / "scripts"))
import compete_cron_builder as cc  # noqa: E402


def run(tmp, *extra):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return cc.main(["--task", "t", "--output", str(tmp), "--min-free-gb", "0", *extra])


def load(tmp, name):
    return json.loads((pathlib.Path(tmp) / name).read_text())


ECHO = 'echo "{candidate_id} {stage}"'


class CompeteTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def test_oracle_outranks_votes_and_id_order(self):
        votes = ECHO + '; [ "{stage}" = peer_review_round_2 ] && echo "selected_candidate_id: proposal_001"; true'
        oracle = '[ "{candidate_id}" = proposal_002 ] && echo "SCORE: 2"'
        self.assertEqual(run(self.tmp, "--question-type", "precision", "--command", votes,
                             "--oracle-command", oracle), 0)
        self.assertEqual(load(self.tmp, "selected.json")["selected_ids"], ["proposal_002"])

    def test_self_votes_are_void(self):
        votes = ECHO + '; [ "{stage}" = peer_review_round_2 ] && echo "selected_candidate_id: {candidate_id}"; true'
        self.assertEqual(run(self.tmp, "--question-type", "precision", "--command", votes), 0)
        evidence = load(self.tmp, "selection_evidence.json")
        self.assertEqual(len(evidence["void_votes"]), 3)
        self.assertEqual(set(evidence["votes"].values()), {0})

    def test_peer_vote_counts(self):
        votes = ECHO + '; [ "{stage}" = peer_review_round_2 ] && echo "selected_candidate_id: proposal_003"; true'
        self.assertEqual(run(self.tmp, "--question-type", "precision", "--command", votes), 0)
        self.assertEqual(load(self.tmp, "selected.json")["selected_ids"], ["proposal_003"])

    def test_chinese_coverage_union_dedupes(self):
        self.assertEqual(run(self.tmp, "--question-type", "audit", "--runner", "mock",
                             "--why", "安全审计，不能遗漏"), 0)
        findings = load(self.tmp, "findings.json")["findings"]
        shared = [f for f in findings if f["claim"] == "missing input validation"]
        self.assertEqual(len(shared), 1)
        self.assertEqual(len(shared[0]["sources"]), 3)
        self.assertEqual(len(findings), 4)
        self.assertEqual(findings[0]["severity"], "high")

    def test_finding_without_reproduction_is_dropped(self):
        cmd = 'echo "FINDING: a.py:1 | claim only |"; echo "FINDING: b.py:2 | real bug | make test"'
        self.assertEqual(run(self.tmp, "--question-type", "coverage", "--command", cmd, "--rounds", "0"), 0)
        data = load(self.tmp, "findings.json")
        self.assertEqual([f["location"] for f in data["findings"]], ["b.py:2"])
        self.assertEqual(len(data["dropped"]), 3)

    def test_one_failure_does_not_stop_the_competition(self):
        cmd = ('if [ "{candidate_id}" = proposal_002 ] && [ "{stage}" = peer_review_round_1 ]; '
               'then exit 1; fi; ' + ECHO)
        self.assertEqual(run(self.tmp, "--question-type", "precision", "--command", cmd), 0)
        manifest = load(self.tmp, "compete_manifest.json")
        self.assertEqual(manifest["failed"], {"proposal_002": "peer_review_round_1"})
        self.assertNotIn("proposal_002", load(self.tmp, "selected.json")["selected_ids"])

    def test_fresh_reruns_catch_gaming(self):
        oracle = ('if [ "{candidate_id}" = proposal_001 ] && [ "$B3_ORACLE_RUN" != 0 ]; then exit 1; fi; '
                  'echo "SCORE: 1"')
        self.assertEqual(run(self.tmp, "--question-type", "precision", "--command", ECHO,
                             "--oracle-command", oracle, "--oracle-runs", "3"), 0)
        self.assertEqual(load(self.tmp, "selected.json")["selected_ids"], ["proposal_002"])

    def test_no_candidate_passing_the_oracle_fails(self):
        self.assertEqual(run(self.tmp, "--question-type", "precision", "--command", ECHO,
                             "--oracle-command", "exit 1"), 3)

    def test_question_type_is_required(self):
        with self.assertRaises(SystemExit):
            run(self.tmp, "--runner", "mock")

    def test_looper_attempt_requires_parent_lease(self):
        with self.assertRaises(SystemExit):
            run(self.tmp, "--question-type", "repair", "--runner", "mock", "--handoff-mode", "looper_attempt")

    def test_old_three_way_layout(self):
        self.assertEqual(run(self.tmp, "--question-type", "precision", "--runner", "mock",
                             "--shape", "three_way_challenge", "--artifact-layout", "old_three_way"), 0)
        root = pathlib.Path(self.tmp)
        for name in ("compete_manifest.json", "verification.md", "best_run.txt", "final_repairs.md",
                     "summary.md", "selected.json", "rejected.json", "synthesis.md", "decisions.log"):
            self.assertTrue((root / name).is_file(), name)
        for cid in cc.THREE_WAY_IDS:
            for name in ("result.md", "verification.md", "critique_round_1.md", "update_round_1.md",
                         "critique_round_2.md", "final_repair.md", "receipts.jsonl"):
                self.assertTrue((root / cid / "implementation" / name).is_file(), f"{cid}/{name}")
        self.assertIn((root / "best_run.txt").read_text().strip(), cc.THREE_WAY_IDS)


if __name__ == "__main__":
    unittest.main()
