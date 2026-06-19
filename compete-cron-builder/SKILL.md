---
name: compete-cron-builder
description: Run or embed a bounded proposal competition for coding, research, planning, coverage, repair, blueprint, SEO, audit, or execution-choice tasks. Use when a task needs n workers, m proposals, choose k, all-valid coverage union, three-way challenge output under run_a/run_b/run_c, verifier checks, peer review, revision, vote selection, repair synthesis, or execution/looper handoff.
---

# Compete Cron Builder

Use this skill to turn one local question into a bounded proposal competition.

## Core Model

```text
n workers
m proposals, optional or auto
choose k, optional or auto
or union all valid findings
```

Inputs:

- `task`: the question or work request.
- `budget_workers`: human-provided worker/resource budget.
- `proposal_count`: explicit count or `auto`.
- `choose_count`: explicit count, `auto`, or `all_valid`.
- `question_type`: `auto`, `precision`, `coverage`, `audit`,
  `blueprint`, `seo`, `execution_choice`, or `repair`.
- `competition_shape`: `auto`, `three_way_challenge`,
  `parallel_proposals`, `coverage_sweep`, `repair_search`, or
  `top_k_synthesis`.
- `selection_mode`: `auto`, `best_one`, `top_k`, `coverage_union`,
  `risk_union`, `vote_then_tiebreak`, or `repair_queue`.
- `artifact_layout`: `native` or `old_three_way`.

Compete may create candidates, selected plans, repair assignments, coverage
findings, validation hints, and handoff metadata. It must not mark execution
checklist items `[x]`; only the execution or looper master lane may accept final
completion.

## Quick Start

Run the fully covered old three-agent workflow with new compete terminology:

```bash
python3 scripts/compete_cron_builder.py \
  --task "Improve this module and test the result" \
  --output ./competition-runs/manual-test \
  --budget-workers 3 \
  --competition-shape three_way_challenge \
  --artifact-layout old_three_way \
  --runner mock \
  --max-output-mb 20 \
  --min-free-gb 0
```

Run a coverage-style competition:

```bash
python3 scripts/compete_cron_builder.py \
  --task "Find security and validation risks in this API surface" \
  --output ./competition-runs/security-sweep \
  --budget-workers 6 \
  --question-type coverage \
  --selection-mode coverage_union \
  --choose-count all-valid \
  --runner mock
```

Use `--runner command --command '<agent command template>'` when wiring a real
agent runner.

Template variables available to `--command`:

- `{agent_id}`: candidate id, such as `run_a` or `proposal_001`
- `{run_id}`: same stable candidate id
- `{candidate_id}`: same stable candidate id
- `{stage}`: workflow stage
- `{prompt_file}`: generated prompt file
- `{output_file}`: file where stdout is intended to be captured
- `{competition_id}`: run id from the manifest
- `{question_type}`: resolved question type
- `{selection_mode}`: resolved selection mode

## Three-Way Challenge Coverage

`competition_shape=three_way_challenge` provides the deterministic
three-candidate challenge surface:

```text
candidate_ids = run_a, run_b, run_c
selected_count = 1
selection_mode = vote_then_tiebreak
tie_break = stable_candidate_id
```

Stages:

1. `proposal`: three candidates produce first results.
2. `initial_verification`: verifier checks candidate outputs.
3. `peer_review_round_1`: each candidate critiques the other two.
4. `revision_round_1`: each candidate revises its own result.
5. `peer_review_round_2`: each candidate critiques revised peers and votes.
6. `repair_synthesis`: each candidate writes final repair assignments.

When `artifact_layout=old_three_way`, preserve:

```text
<output>/
  run_a/implementation/
  run_b/implementation/
  run_c/implementation/
  verification.md
  best_run.txt
  final_repairs.md
  summary.md
```

Each candidate directory receives:

- `result.md`
- `verification.md`
- `critique_round_1.md`
- `update_round_1.md`
- `critique_round_2.md`
- `final_repair.md`

The native manifest and JSON summaries may be added, but they must not replace
these artifacts when the old layout is requested.

## m/k Policy

If the user only provides worker budget `n`, resolve proposal and selection
counts from question type:

- `precision`: `m=min(n,4)`, `k=1` or `2`, choose best or fallback pair.
- `coverage`: `m` bounded by budget, `k=all_valid`, merge valid findings.
- `audit`: `m` bounded by budget, `k=all_valid`, severity-rank risks.
- `blueprint`: `m=min(n,5)`, `k=2` or `3`, synthesize a blueprint patch.
- `seo`: strategy uses synthesis, coverage uses union, execution uses repair.
- `execution_choice`: `m=min(n,3)`, `k=1`, choose one local implementation path.
- `repair`: `m=min(n,4)`, choose primary repair plus fallback.
- `three_way_challenge`: `m=3`, `k=1`, vote then stable tie-break.

## Execution Embed Rules

When embedded in `execution-cron-builder`:

- Preserve the single authoritative blueprint source.
- Keep the DAG acyclic.
- Workers and compete candidates may only produce proposals or `[_]` evidence.
- Compete must never write `[x]`.
- Repair or coverage outputs start as `[ ]` child items after master dedupe.
- Master remains the only actor that promotes `[_] -> [x]`.

Valid handoff actions:

- `create_child_items`
- `enqueue_integration_hint`
- `write_blueprint_patch_proposal`
- `write_validation_hint`
- `write_repair_assignment`
- `request_master_review`

## Looper Embed Rules

When embedded in `looper-cron-builder`, compete may run only inside an active
`ResourceLease` with a `ParentLeaseRef`. Its token, wall-clock, human-review,
disk, and diff costs count against that parent lease. Candidate outputs remain
provisional until master accepts them in DAG order.

If a compete-heavy loop produces no primary or secondary reward, record it in
the no-reward accumulator. Paused loops require explicit resource refund plus a
strategy change before resume.

Nested compete runs cannot write `[x]`, cannot escape the parent lease budget,
and produce reward candidates only. The parent looper attempt owns final reward
classification and ROI accounting.

## Operating Rules

- Use all-settled behavior for parallel candidates.
- One failed candidate must not fail the competition if another candidate
  succeeded.
- If no valid candidates exist, stop and write a failure summary.
- Keep captured output bounded with `--max-output-mb`.
- Run the cron space guard before cron-launched competitions.
- Do not let parallel candidates mutate the same authoritative source tree.
- Prefer patches, plans, diffs, findings, or artifacts under candidate output
  directories.
- Tie-break deterministically by stable candidate id.

## References

Read `references/competition-pattern.md` when adapting compete to another
runtime, embedding it in execution cron, or wiring it to looper attempts.
