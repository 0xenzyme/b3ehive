#!/bin/bash
# Smoke-test the three-way layout end to end with the mock runner.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$(mktemp -d "${TMPDIR:-/tmp}/b3ehive-compete-three-way.XXXXXX")"
trap 'rm -rf "$OUT_DIR"' EXIT

python3 "${ROOT_DIR}/compete-cron-builder/scripts/compete_cron_builder.py" \
  --task "Validate three-way artifact coverage" \
  --output "$OUT_DIR" \
  --question-type precision \
  --shape three_way_challenge \
  --artifact-layout old_three_way \
  --runner mock \
  --min-free-gb 0 >/dev/null

for file in compete_manifest.json classification.md decisions.log verification.md best_run.txt \
  final_repairs.md summary.md selected.json rejected.json synthesis.md selection_evidence.json; do
  [[ -f "${OUT_DIR}/${file}" ]] || { echo "ERROR: missing ${file}" >&2; exit 1; }
done

for candidate in run_a run_b run_c; do
  for file in result.md verification.md critique_round_1.md update_round_1.md critique_round_2.md \
    final_repair.md receipts.jsonl; do
    [[ -f "${OUT_DIR}/${candidate}/implementation/${file}" ]] || {
      echo "ERROR: missing ${candidate}/implementation/${file}" >&2; exit 1; }
  done
done

python3 - "$OUT_DIR" <<'PY'
import json, pathlib, sys
out = pathlib.Path(sys.argv[1])
m = json.loads((out / "compete_manifest.json").read_text())
best = (out / "best_run.txt").read_text().strip()
assert m["schema_version"] == "b3ehive.compete.v2"
assert m["competition_shape"] == "three_way_challenge"
assert m["artifact_layout"] == "old_three_way"
assert m["candidate_ids"] == ["run_a", "run_b", "run_c"]
assert m["handoff"]["state"] == "[_]"
assert m["selected_ids"] == [best]
assert json.loads((out / "selected.json").read_text())["selected_ids"] == [best]
PY

echo "Compete three-way artifact validation passed."
