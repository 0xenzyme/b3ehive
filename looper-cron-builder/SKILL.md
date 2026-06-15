---
name: looper-cron-builder
description: Build or repair a resource-aware, reward-aware, ROI-tracked loop daemon for a DAG-driven repository. Use when blueprint nodes, bridge metrics, product validation goals, benchmark lanes, monitoring signals, or repeated validation failures need bounded loop attempts, explicit resource leases, evidence ledgers, no-reward pause rules, and re-funded resume under a master acceptance gate.
---

# Looper Cron Builder

## Overview

Build a repository-local looper cron that monitors explicit bridge metrics and
DAG nodes, allocates bounded resource leases, launches loop daemon attempts,
records resource consumption and reward signals, computes ROI, pauses loops that
consume resources without reward, and resumes paused loops only after explicit
re-funding plus a strategy change.

Looper is a feedback overlay, not a cycle inside the dependency graph:

```text
DAG = dependency order, still acyclic
Bridge metric = measurable validation surface between intent and execution
Loop daemon = conditional feedback actor around a node, subgraph, or metric
Resource broker = budget, lease, pause, and resume authority
Reward ledger = evidence that the loop produced value
Master lane = only actor allowed to accept final completion
```

Do not add cyclic dependency edges to the DAG. Attach loop specs beside DAG
nodes or bridge metrics, and let the master lane close checklist items only
after validation passes.

## Privacy and Generalization Rule

Generated looper specs, docs, prompts, ledgers, and examples must stay
project-neutral unless the user explicitly asks for a private, local-only
artifact.

Public or committed Looper artifacts must not include:

- private repository names
- customer names
- local absolute paths
- personal evidence directories
- internal product codenames
- private strategy document paths
- raw user conversations or account identifiers
- vendor secrets, API keys, or billing identifiers

Use generic labels such as `product_beta`, `repo_maintenance`,
`benchmark_lane`, `claim_audit`, `customer_workflow`, `growth_experiment`, and
`ops_review`. If a private name is necessary for local execution, keep it in
`.cron/`, `.ops/`, an ignored local config, or a prompt/log surface that is not
committed.

## Core Model

Every Looper installation must define these objects:

```text
LoopSpec
BridgeMetric
LoopInstance
ResourceEnvelope
ResourceLease
AttemptWorker
RewardSignal
ROILedger
PauseResumePolicy
```

### LoopSpec

`LoopSpec` is the static definition of a loop. Store committed generic specs
under a neutral docs path such as:

```text
Docs/looper/LOOP_SPEC.md
```

Runtime-expanded private specs may live under ignored paths such as:

```text
.b3ehive/looper/loops.yaml
.cron/looper/loops.local.yaml
```

Minimum fields:

```yaml
loop_id: LOOP-REPO-MAINTENANCE-REPAIR
attach_to:
  bridge_metric_ids:
    - build_test_fix_report_completed_count
  dag_node_ids:
    - ITEM-012
purpose: repair failing implementation attempts until validators pass or ROI stops justifying spend
trigger:
  any:
    - metric_below_target: build_test_fix_report_completed_count
    - gate_failed: unit_test
    - evidence_stale_days: 7
preconditions:
  validator_exists: true
  resource_envelope_available: true
  owned_paths_declared: true
  no_active_conflict: true
resource_envelope_ref: ENV-REPO-MAINTENANCE-WEEKLY
max_parallel_attempts: 3
owned_paths:
  - src/**
forbidden_paths:
  - .cron/**
  - .ops/**
validators:
  cheap:
    - command: "<lint or focused test command>"
  expensive:
    - command: "<full validation command>"
reward_model:
  primary_rewards:
    - accepted_patch
    - metric_target_progress
  secondary_rewards:
    - validator_added
    - failure_cause_classified
  negative_rewards:
    - non_reproducible_output
    - cost_without_new_evidence
pause_resume:
  pause_when:
    - no_reward_budget_exhausted
    - no_reward_attempt_limit_reached
    - validator_missing
  resume_when:
    - explicit_resource_refund
    - new_validator_added
    - new_evidence_arrived
    - bridge_target_changed
```

### BridgeMetric

`BridgeMetric` is the measurable surface Looper watches. It can represent a
product validation target, repository maintenance target, benchmark target,
claim-audit target, support workflow target, or operational KPI.

Minimum fields:

```yaml
metric_id: build_test_fix_report_completed_count
owner_loop: LOOP-REPO-MAINTENANCE-REPAIR
target: 3
window: 4w
current_value: 1
evidence_ref: Docs/looper/evidence/repo_maintenance.md
failure_signal: attempts consume budget without producing a replayable trajectory
reward_weight: 10
privacy_class: generic_committable
```

Bridge metrics drive three decisions:

- `trigger`: start or wake a loop when a metric is below target, stale, or failed.
- `reward`: count improvement as primary or secondary reward.
- `downgrade`: pause, split, or downgrade when spend accumulates without reward.

### ResourceEnvelope

`ResourceEnvelope` is the total budget granted to a loop for a period.

Track at least:

```json
{
  "envelope_id": "ENV-REPO-MAINTENANCE-WEEKLY",
  "loop_id": "LOOP-REPO-MAINTENANCE-REPAIR",
  "status": "active",
  "budget": {
    "usd": 30,
    "tokens": 3000000,
    "wall_clock_minutes": 720,
    "human_review_minutes": 90,
    "attempts": 20,
    "disk_gb": 8
  },
  "spent": {
    "usd": 0,
    "tokens": 0,
    "wall_clock_minutes": 0,
    "human_review_minutes": 0,
    "attempts": 0,
    "disk_gb": 0
  }
}
```

Generated guards must refuse new attempts when the envelope is exhausted.

### ResourceLease

`ResourceLease` is the short-lived budget granted to one daemon activation or
attempt worker.

No lease means no attempt.

Minimum fields:

```json
{
  "lease_id": "LEASE-0001",
  "loop_id": "LOOP-REPO-MAINTENANCE-REPAIR",
  "attempt_id": "ATTEMPT-0001",
  "ttl_minutes": 60,
  "max_usd": 3,
  "max_tokens": 250000,
  "max_wall_clock_minutes": 60,
  "max_diff_kib": 256,
  "workspace": ".cron/looper/workspaces/slot-01",
  "status": "leased"
}
```

Leases must have TTL, heartbeat, owner, workspace, and reclaim behavior. Expired
leases, dead daemon owners, and missing heartbeat files must be released before
new workers are spawned.

## Reward and ROI Accounting

Looper must record value after every attempt. A loop that consumes resources but
does not create reward must pause.

### Reward Classes

Primary rewards directly move the bridge metric or close validated work:

- accepted patch
- replayable execution trajectory
- benchmark workload completed
- product validation signal
- paid or committed conversion signal
- claim audit evidence completed
- operational KPI improved

Secondary rewards create reusable learning or infrastructure:

- validator added
- failure cause classified
- reproduction path recorded
- scope narrowed
- reusable workflow or skill extracted
- benchmark harness improved
- objection or support taxonomy created

Negative or no-reward outcomes consume resources without usable progress:

- no new evidence
- validator still missing
- output not reproducible
- patch not reviewable
- metric unchanged
- claim still unsupported
- only narrative summary was produced

### ROILedger

Every Looper cron must maintain a ROI ledger under an ignored runtime path and
may generate a sanitized committed report.

Runtime ledger example:

```json
{
  "loop_id": "LOOP-REPO-MAINTENANCE-REPAIR",
  "period": "2026-W25",
  "spent": {
    "usd": 6.4,
    "tokens": 580000,
    "wall_clock_minutes": 134,
    "human_review_minutes": 18
  },
  "rewards": {
    "primary": ["accepted_patch"],
    "secondary": ["failure_cause_classified", "validator_added"],
    "negative": ["one_attempt_not_reproducible"]
  },
  "bridge_metrics": {
    "build_test_fix_report_completed_count": {
      "before": 1,
      "after": 2,
      "target": 3
    }
  },
  "roi_score": 1.7,
  "decision": "continue_with_same_budget"
}
```

Default scoring model:

```text
gross_reward =
  10 * primary_reward_count
  + 3 * secondary_reward_count
  + 1 * evidence_point_count
  - 5 * negative_reward_count
  - 8 * unsupported_claim_penalty

resource_cost =
  usd_spent
  + 0.000002 * tokens_spent
  + 0.05 * wall_clock_minutes
  + 0.5 * human_review_minutes
  + 0.2 * disk_gb_hours

roi_score = gross_reward / max(resource_cost, 1)
```

Generated cron code may let users override weights, but it must not omit
resource cost, bridge metric delta, reward class, and decision fields.

Decision thresholds:

```text
roi_score >= 2.0:
  continue_or_increase_budget
1.0 <= roi_score < 2.0:
  continue_with_same_budget
0.3 <= roi_score < 1.0:
  continue_only_if_bridge_priority_high
roi_score < 0.3:
  cooldown_or_pause
roi_score <= 0 and no_reward_budget_exhausted:
  paused_no_reward
```

## No-Reward Pause

Each loop must maintain a no-reward accumulator.

```json
{
  "loop_id": "LOOP-PRODUCT-BETA",
  "no_reward": {
    "attempts": 3,
    "usd": 5.8,
    "tokens": 420000,
    "wall_clock_minutes": 190,
    "human_review_minutes": 25
  },
  "last_reward_at": "2026-06-15T00:00:00Z",
  "pause_threshold": {
    "attempts": 4,
    "usd": 8,
    "human_review_minutes": 30
  }
}
```

Accumulator decay:

- Primary reward clears the no-reward accumulator.
- Secondary reward halves the no-reward accumulator.
- Weak evidence reduces the accumulator by at most 20%.
- Negative reward continues accumulation.

When a threshold is reached:

```text
active -> paused_no_reward
```

The pause report must include:

- pause reason
- resource spent since last reward
- missing reward signals
- likely causes
- resume conditions
- required strategy changes for the next funded run

Paused loops must not resume automatically.

## Re-Funded Resume

`paused_no_reward` can return to `eligible` only when a clear resume event exists:

- explicit resource refund by operator
- new evidence arrived
- new validator added
- bridge target changed
- dependency unblocked
- human approval supplied

Resume must also change strategy. Same loop, same strategy, and no reward is
forbidden.

Minimum resume spec:

```yaml
resume_id: RESUME-PRODUCT-BETA-001
loop_id: LOOP-PRODUCT-BETA
reason: new_user_segment
new_resource_envelope:
  max_total_usd: 12
  max_human_review_minutes: 60
required_strategy_change:
  - target_more_specific_segment
  - record_friction_points
  - stop_after_defined_nonresponse_limit
expected_reward:
  - at_least_one_metric_delta
  - at_least_one_price_or_usage_signal
```

## State Machine

Loop state:

```text
draft
  -> eligible
  -> active
  -> cooling_down
  -> paused_no_reward
  -> paused_budget_exhausted
  -> paused_missing_validator
  -> paused_human_approval_required
  -> retired_success
  -> retired_invalidated
```

Runtime state:

```text
eligible
  -> resource_check
  -> lease_acquired
  -> daemon_running
  -> attempts_running
  -> reward_accounting
  -> roi_decision
  -> continue / cooldown / pause / retire / split
```

Reward accounting must happen before the next resource lease is granted.

## Concurrency Model

Looper adds a third cursor to b3ehive's existing worker/master pattern:

```text
DAG Claim Cursor:
  fills normal worker lanes from [ ] DAG items.

Loop Attempt Cursor:
  fills loop daemon lanes from eligible loops with active resource envelopes.

Master Integration Cursor:
  validates [_] outputs and looper candidates in DAG dependency order.
```

Required scheduler order:

1. Read authoritative blueprint, bridge metrics, loop ledgers, and resource ledgers.
2. Release expired leases and dead daemons.
3. Cheaply refresh finished attempt state.
4. Refill normal DAG workers first so core implementation does not starve.
5. Rank eligible loops by bridge priority, ROI, reward recency, and urgency.
6. Allocate leases through the resource broker.
7. Start or wake loop daemons.
8. Defer heavy ROI reports until after worker refill or behind an explicit refresh flag.
9. Let the master lane integrate validated candidates in DAG order.

High-concurrency rules:

- Finished attempts do not consume live worker capacity.
- Heavy integration or ROI scans must not block worker refill.
- Dependent loop outputs remain provisional until dependencies are `[x]`.
- Path-overlapping attempts must run in isolated workspaces.
- Resource broker, not individual daemons, controls global concurrency.
- Master lane resolves conflicts and writes accepted `[x]` marks.

## Dual-Cursor Checklist State Protocol

Looper must preserve b3ehive's existing checkbox grammar when attached to
checklist items:

- `[ ]` means not done and still claimable.
- `[_]` means worker self-tested or looper candidate exists, but master has not
  accepted it.
- `[x]` means master accepted after validation and integration.

Attempt workers and looper daemons may only create candidates or advance assigned
work to `[_]`. They must never write `[x]`.

Cleanup is forbidden while any attached item remains `[ ]` or `[_]`, or while
any loop has live leases, unaccounted attempts, or a pending pause/resume
decision.

## Runtime Files

Committed generic docs may live under:

```text
Docs/looper/LOOP_SPEC.md
Docs/looper/BRIDGE_METRICS.md
Docs/looper/ROI_REPORT.md
```

Private runtime files should be ignored and local:

```text
.b3ehive/looper/loops.yaml
.b3ehive/looper/bridge_metrics.yaml
.b3ehive/looper/resource_envelopes.json
.b3ehive/looper/leases.json
.b3ehive/looper/reward_ledger.jsonl
.b3ehive/looper/roi_ledger.jsonl
.b3ehive/looper/pause_ledger.jsonl
.cron/looper_guard.state
.cron/looper_guard.log
.cron/looper/workspaces/slot-N/
.cron/scripts/cron_space_guard.sh
.ops/install_looper_cron.sh
.ops/cleanup_looper_cron.sh
```

The generated cron must add `.b3ehive/looper/*.local.*`, `.cron/`, and `.ops/`
runtime paths to `.git/info/exclude` or an equivalent local ignore strategy
unless the user explicitly wants committed operational scaffolding.

## Agent Platform Compatibility

Generated looper cron code must support Codex, Claude Code, opencode, OpenClaw,
and Hermes through a single agent-runner abstraction.

Default platform selection:

- `B3EHIVE_AGENT_PLATFORM=codex` uses `codex exec`.
- `B3EHIVE_AGENT_PLATFORM=claude` uses `claude -p`.
- `B3EHIVE_AGENT_PLATFORM=opencode` uses `opencode run`.
- `B3EHIVE_AGENT_PLATFORM=openclaw` uses `openclaw agent`.
- `B3EHIVE_AGENT_PLATFORM=hermes` uses `hermes chat`.
- `B3EHIVE_AGENT_PLATFORM=auto` may choose Codex, then Claude Code, then
  opencode, then OpenClaw, then Hermes, based on installed CLIs.

Default command templates:

```bash
# Codex
codex exec --cd "$WORKER_REPO" --model "${CODEX_MODEL:-gpt-5.3-codex}" \
  -c model_reasoning_effort="${CODEX_REASONING_EFFORT:-xhigh}" \
  < "$PROMPT_FILE" > "$OUTPUT_FILE"

# Claude Code
claude -p --model "${CLAUDE_MODEL:-sonnet}" --effort "${CLAUDE_EFFORT:-max}" \
  --permission-mode "${CLAUDE_PERMISSION_MODE:-auto}" \
  --add-dir "$WORKER_REPO" < "$PROMPT_FILE" > "$OUTPUT_FILE"

# opencode
opencode run --dir "$WORKER_REPO" ${OPENCODE_MODEL:+--model "$OPENCODE_MODEL"} \
  ${OPENCODE_VARIANT:+--variant "$OPENCODE_VARIANT"} \
  ${OPENCODE_AGENT:+--agent "$OPENCODE_AGENT"} \
  < "$PROMPT_FILE" > "$OUTPUT_FILE"

# OpenClaw
openclaw ${OPENCLAW_PROFILE:+--profile "$OPENCLAW_PROFILE"} agent --local \
  ${OPENCLAW_AGENT:+--agent "$OPENCLAW_AGENT"} \
  ${OPENCLAW_THINKING:+--thinking "$OPENCLAW_THINKING"} \
  --message "$(cat "$PROMPT_FILE")" > "$OUTPUT_FILE"

# Hermes
hermes chat ${HERMES_MODEL:+--model "$HERMES_MODEL"} \
  --toolsets "${HERMES_TOOLSETS:-skills,terminal}" \
  ${HERMES_SKILLS:+-s "$HERMES_SKILLS"} \
  -q "$(cat "$PROMPT_FILE")" > "$OUTPUT_FILE"
```

If `B3EHIVE_AGENT_RUNNER` is set, use it as the authoritative command template
and print the resolved runner in validate-only output. Do not silently replace a
requested model, service tier, permission mode, variant, profile, agent, toolset,
or preloaded skill list.

## Workflow

1. Inspect the repository and identify the intended bridge metrics, DAG nodes,
   validators, and resource boundaries.
2. Confirm the loop is project-neutral if it will be committed. Move private
   names and local paths into ignored local config.
3. Create or update `Docs/looper/LOOP_SPEC.md` and `Docs/looper/BRIDGE_METRICS.md`
   with sanitized metrics and examples.
4. Add private runtime ledgers under `.b3ehive/looper/` and `.cron/looper/`, then
   hide them from git.
5. Create the required pieces:
   - loop spec validator
   - bridge metric reader
   - resource broker
   - lease allocator
   - looper guard
   - daemon runner
   - reward/ROI accountant
   - pause/resume ledger
   - cron space/log guard
   - installer and cleanup scripts
6. Run `VALIDATE_ONLY=1` before installing cron. Validate spec shape, privacy
   rules, metric shape, resource envelopes, leases, validators, and disk budgets.
7. Run one manual loop tick with a tiny resource envelope.
8. Verify attempts can create candidates or `[_]` evidence only.
9. Verify the master lane is the only actor that can accept `[x]`.
10. Install cron only after validate-only, one manual tick, budget guard, and
    privacy scan pass.
11. Pause loops automatically when no-reward thresholds are hit.
12. Resume paused loops only with explicit refund and required strategy change.
13. Clean up only when no live leases, no pending attempts, no unfinished attached
    checklist items, and no pending pause/resume decisions remain.

## Validation

Before declaring a Looper ready:

- validate YAML/JSON syntax for loop specs, bridge metrics, envelopes, and leases
- verify every loop has at least one bridge metric or DAG node attachment
- verify every loop has a validator or an explicit monitoring evidence source
- verify every attempt requires a resource lease
- verify no-reward accumulator thresholds exist
- verify ROI ledger fields exist
- verify paused loops cannot resume without refund and strategy change
- verify worker prompts cannot write `[x]`
- verify master integration gate is documented
- run the cron space guard once
- run `bash -n` on generated shell helpers
- run a privacy scan for local absolute paths and private names before committing

Recommended privacy scan patterns:

```bash
rg -n -i '(absolute home path|private repo|customer|secret|api[_-]?key|token|password)' .
```

Add any project-specific private names to a local-only denylist before publishing
or pushing public skill changes.

## Common Failure Modes

- adding feedback edges directly to the DAG and creating cycles
- starting attempts without resource leases
- treating no-reward attempts as harmless retries
- resuming a paused loop with the same strategy and fresh budget only
- measuring token spend but not human review time or disk/log pressure
- counting narrative summaries as reward without evidence
- allowing daemon workers to write `[x]`
- letting heavy ROI reporting block worker refill
- committing private metric names, local paths, or customer identifiers
- leaving paused loops undocumented so the operator cannot decide whether to
  refund, change strategy, or retire the loop
