---
name: execution-cron-builder
description: Build or repair a blueprint-driven execution cron for a repository using one authoritative blueprint, a daily todo snapshot, an isolated automation clone, bounded agent-runner batches for Codex, Claude Code, opencode, OpenClaw, or Hermes, validation gates, checkpoint commits, and cleanup-on-complete. Use when a repo should continuously implement a blueprint, when an execution cron needs to be added to a new repository, or when an existing blueprint-execution cron needs boundary/gate fixes.
---

# Execution Cron Builder

## Overview

Build a repository-local execution cron that wakes on a schedule, clones or syncs isolated automation repos, reads exactly one blueprint, keeps a dependency DAG for open checklist items, runs bounded agent-runner batches, validates real implementation, checkpoints commits, and removes its own cron when the blueprint is truly complete.
Default gate posture is strict: no mock completion, and no upper-layer completion while finer layers remain open.
Default commit posture is code-first: never commit cron/private artifacts, never commit tests from automation batches, and keep docs commits less than or equal to code commits per batch.
Default orchestration posture is split-lane DAG aware: tmux workers claim implementation work in DAG/topological order up to the user-requested max concurrency, while the main session integrates, validates, and closes work strictly in DAG dependency order with conflict and completion gates enforced.

## Dual-Cursor Checklist State Protocol

All execution checklists and generated todos must use exactly these three
checkbox states:

- `[ ]` means not done: unclaimed, not yet implemented, or still requiring a worker.
- `[_]` means worker self-tested: worker output exists and the worker's local
  validation passed, but the main/master integration lane has not accepted,
  merged, and revalidated it yet.
- `[x]` means master accepted: the main/master lane integrated the output into
  the authoritative checkout, reran the required gates, reconciled completion
  surfaces, and accepted the item as complete.

This is a two-cursor protocol, and the checkbox mark itself is the cursor
state. The worker cursor advances items from `[ ]` to `[_]`. The master cursor
advances items from `[_]` to `[x]`. Workers must never write `[x]`, and the
scheduler must never treat `[_]` as done.

Required behavior:

- Checklist parsers must recognize `[ ]`, `[_]`, and `[x]`; any other checkbox
  state is invalid.
- Generated blueprints, todos, ledgers, progress tables, summaries, and status
  commands must preserve this exact state vocabulary instead of inventing
  aliases such as `done`, `pending`, `landed`, or `validated` as replacement
  completion states. Extra fields may add detail, but the checkbox remains the
  source of truth.
- Bootstrap generators initialize new items as `[ ]`.
- Regenerators preserve existing `[ ]`, `[_]`, and `[x]` marks by item id and
  may only downgrade a mark when a guard has explicit evidence that the current
  mark is invalid.
- Worker prompts must instruct workers to mark only their assigned items as
  `[_]` after implementation and self-test evidence exists.
- Worker completion evidence must include changed paths, validation commands,
  validation output summary, and branch/worktree/commit reference when
  applicable.
- Daily todos must report counts for `not_done`, `worker_self_tested`, and
  `master_accepted`.
- Worker claim frontiers are computed from `[ ]` items only.
- Main-session integration frontiers are computed from `[_]` items whose
  dependencies are `[x]` and whose path conflicts are resolved.
- Live worker capacity is consumed by live claims only, not by `[_]` finished
  items waiting for master integration.
- Dependency closure treats `[ ]` and `[_]` as unfinished. A dependent item can
  be master-accepted only after all dependencies are `[x]`.
- Cleanup is forbidden while any `[ ]` or `[_]` item remains.
- Progress math must report three counts separately and may derive
  `unfinished = count([ ]) + count([_])`; `[_]` must never be collapsed into
  `[x]` for percentages, cleanup, or release gates.
- If an item remains `[_]` across repeated master validation attempts, create a
  repair child item as `[ ]`, keep the parent `[_]`, and record the failed gate.
- If a worker incorrectly writes `[x]`, the guard must downgrade it to `[_]`
  unless master validation evidence for that item already exists in the
  authoritative checkout.
- If master validation fails after integrating a worker output, the authoritative
  item stays `[_]`, the failed gate is recorded, and any follow-up repair item
  starts as `[ ]`.

## Workflow

1. Inspect the repository and identify the single blueprint source.
2. Freeze the execution boundary.
   The cron must treat exactly one file as the requirement source.
3. If the blueprint is prose-first, generate an authoritative execution checklist section into that same blueprint before enabling cron.
   Initialize every execution item as `[ ]` on first bootstrap, preserve existing `[_]` and `[x]` states on regeneration, and generate daily todos from that authoritative checklist section only.
4. Add private `.ops/` and `.cron/` helpers locally and hide them from git where appropriate.
5. Create the four required pieces:
   - authoritative checklist/bootstrap generator
   - blueprint/todo generator
   - execution guard
   - cron installer
   - cron cleanup script
6. Run `VALIDATE_ONLY=1` once before enabling cron.
   `VALIDATE_ONLY=1` is a dry gate only: it must validate configuration, DAG shape, sync state, and budgets, then exit without spawning or claiming workers. Never use validate-only for an execution tick whose purpose is to fill worker lanes.
7. Install cron only after the automation repo, checklist bootstrap, blueprint seeding, and todo generation all work.
8. Keep the batch size small and cluster-bounded.
   For fragmented small files, merge same-directory file tasks into one batch with combined source size <=100KB; if a single file is >100KB, allow it as a single-file batch.
9. Enforce strict layer gating: only execute the finest still-open layer; if lower layers are open, upper layers must stay unchecked.
   If a tick finds upper-layer `[x]` while lower layers are still open, auto-reset the violating upper-layer `[x]` items to `[ ]`, report the correction, and continue from the lower layer.
10. Treat the main session as the integration/master lane, not only a scheduler.
   The main session may claim checklist items under the active user goal, but its default responsibility is to merge worker output, enforce DAG dependencies, validate the combined tree, and clear merge/conflict blockers caused when worker worktrees or automation branches are merged back to `main`.
11. Generate todos with the current dependency DAG for all unfinished checklist items.
   The todo must list item ids, dependency ids, worker-claim order state, integration-ready/blocked state, claimed worker/session, owned paths, and the main-session integration frontier.
   The DAG must be acyclic; cycle detection is a hard todo-generation failure.
12. When launching new `tmux` agent workers, use user-saturated ordered DAG concurrency instead of ready-frontier lane limiting.
   `worker_count = user_max_concurrency - live_worker_count`, capped by the count of unclaimed open DAG nodes available in topological order.
   Workers must claim nodes from the earliest still-open layer/cluster in stable DAG/topological order, but worker spawn is not blocked by unfinished dependencies or overlapping path families. Dependent or path-overlapping worker results are provisional until the main session integrates them in DAG dependency order.
13. Maintain a claim ledger for tmux workers.
   The ledger must record item id, original blueprint id, dependency ids, session name, slot, workspace path, status, claim time, and owned path scopes. Todo generation must display each open item's claim state as `live:<session>`, `finished:<session>`, or `unclaimed`, and must include the claim ledger path.
14. Every newly launched `tmux` agent worker must use the selected platform's requested/latest high-capability model and effort settings.
   Honor explicit environment/config values such as `B3EHIVE_AGENT_PLATFORM`, `B3EHIVE_AGENT_RUNNER`, `CODEX_MODEL`, `CODEX_REASONING_EFFORT`, `CODEX_SERVICE_TIER`, `CLAUDE_MODEL`, `CLAUDE_EFFORT`, `CLAUDE_PERMISSION_MODE`, `OPENCODE_MODEL`, `OPENCODE_VARIANT`, `OPENCODE_AGENT`, `OPENCLAW_PROFILE`, `OPENCLAW_AGENT`, `OPENCLAW_THINKING`, `HERMES_MODEL`, `HERMES_TOOLSETS`, and `HERMES_SKILLS`; do not silently replace a requested service tier, permission mode, variant, agent, profile, toolset, or preloaded skill list. If no platform-specific runtime option is specified, the cron may choose its repo default and must print that value in the guard output.
15. Add a main-session integration queue for landed worker outputs.
   The queue must scan claimed worker workspaces, report changed files and diff byte counts, detect path conflicts, and classify outputs whose combined diff is <=256KiB as small-diff batch candidates.
16. Keep worker claim and master integration as separate cursors.
   The worker cursor is saturated from open DAG nodes whose claim state is `unclaimed` or `live`; `finished` claims correspond to `[_]` checklist items, belong to the master integration queue, and must not consume worker capacity or stop later unclaimed nodes from being claimed.
   Todo generation must show both cursors: the worker claim frontier for concurrency filling, and the master integration frontier/queue for DAG-ordered validation and closure.
   Heavy integration queue scans must not block worker refill; run them after refill, incrementally, or behind an explicit refresh flag.
17. Allow batch integration of small worker diffs, with strict closure gates.
   The main session may batch apply multiple worker diffs when their combined diff is <=256KiB and path conflicts are absent or explicitly resolved. It must still validate and close checklist items in DAG dependency order, and must update the authoritative blueprint/todo after each accepted closure or coherent validated batch.
   Batch application is an integration acceleration path, not a dependency bypass: apply the non-conflicting diffs together, run validation on the combined tree, then write `[x]` marks only for the longest dependency-ordered prefix whose gates pass.
18. After every successful batch, sync completion back to the authoritative blueprint and refresh today's todo in the main repo.
   Worker batches may sync only `[_]` marks and evidence; only the main/master lane may sync `[x]` marks.
19. Enforce documentation reconciliation as a success gate:
   - if a batch closes checklist items, all required completion surfaces must be updated in the same batch (for example `Overall Blueprint + Stage Blueprint + today's todo`)
   - todo references must use stable repository paths, never automation clone absolute paths
   - "code done but completion docs stale" is a failed tick and must trigger a repair batch
20. If the same `[ ]` item remains unresolved for repeated ticks (default >=5), auto-split it into child checklist items in the blueprint, regenerate today's todo, and notify the human with the split details.
21. Clean up the cron when the blueprint is complete and validation passes.
   Cleanup must use hard conditions:
   - authoritative blueprint has zero `[ ]` items
   - authoritative blueprint has zero `[_]` items
   - latest todo snapshot shows `Unfinished = 0`
   - no running selected agent-runner process in automation repos
   - no pending checkpoint artifact remains
   - cleanup script succeeds and cron entry is actually removed
22. Enforce commit-surface policy at checkpoint time:
   - never stage/commit `.cron/`, `.ops/`, logs, state, generated todo snapshots, model binaries
   - never stage/commit `spec/` or `tests/` changes from execution batches
   - reject batch commit when staged docs files outnumber staged code files
   - reject docs-only batch commits
   - classify executable validation assets that live under docs-style folders as `code/evidence`, not prose docs
   - at minimum, treat paths like `Docs/Stage3IOSPathValidation/**` and `Docs/scripts/*.sh` as `code/evidence` during commit hygiene counting
23. Enforce sync-first push policy:
   - before coding (at tick start) and before checkpoint commit, local authoritative repo must `fetch --prune` + `ff-only` sync
   - at tick start, explicitly verify development machine branch HEAD equals remote tracking HEAD; if not equal, block the tick before any implementation
   - after every successful push, local authoritative repo must be synced again and verified equal to remote HEAD
   - if local sync fails (dirty tracked changes, detached HEAD, non-ff, or network failure), block the tick and do not treat batch as success
24. Add a `repo force sync` best-practice path for stuck ticks:
   - trigger condition: repeated sync blocks caused by local tracked changes
   - sequence: `stash -u` -> `fetch --prune` + `pull/rebase or ff-only merge` -> `stash pop`
   - if `stash pop` conflicts, stop and resolve conflicts explicitly, then run one consolidation commit+push
   - always log the force-sync attempt and result so operators can audit it later
25. Add lock hygiene when the guard uses `flock` and also spawns `tmux` workers:
   - never let the scheduler's locked file descriptor leak into `tmux new-session`, `tmux new-window`, or `tmux respawn-pane`
   - explicitly close the lock fd on those launches (for example `9>&-`) before `tmux` starts its server/client process tree
   - keep scheduler/global state separate from worker/slot state so a no-focus worker cannot overwrite the scheduler's authoritative status
   - if a historical lock was already leaked into a long-lived `tmux` server, rotate the lock path version or restart the affected `tmux` server/session before resuming cron
26. Ensure worker prompts use the actual automation clone as `Repository root`.
   If a worker process is launched with `cd .cron/automation_repo_slotN`, the prompt must name that clone path as the repository root and explicitly forbid direct edits to the scheduler's authoritative checkout.
   Never put the main checkout path in a worker prompt unless the worker is intentionally running in the main checkout.
27. Treat claim and dirty-sync recovery as part of the guard, not manual cleanup:
   - release claims for items that are already closed in the authoritative blueprint
   - release claims for still-open items when the assigned worker process is no longer alive
   - detect active workers with self-match-safe process patterns such as `[c]odex exec...`
   - if the main checkout has tracked dirty files and no active workers, stash with an audit label before syncing
   - if tracked dirty files exist while workers are active, block protectively instead of stashing their live work
28. Add a disk/log budget guard before installing or repairing cron.
   The guard must run at the start of every scheduler tick, before spawning workers, and must block new workers when budgets are exceeded.

## Agent Platform Compatibility

Generated execution cron code must support Codex, Claude Code, opencode,
OpenClaw, and Hermes through a single agent-runner abstraction.

Default platform selection:
- `B3EHIVE_AGENT_PLATFORM=codex` uses `codex exec`.
- `B3EHIVE_AGENT_PLATFORM=claude` uses `claude -p`.
- `B3EHIVE_AGENT_PLATFORM=opencode` uses `opencode run`.
- `B3EHIVE_AGENT_PLATFORM=openclaw` uses `openclaw agent`.
- `B3EHIVE_AGENT_PLATFORM=hermes` uses `hermes chat`.
- `B3EHIVE_AGENT_PLATFORM=auto` may choose Codex when `codex` is available,
  otherwise Claude Code when `claude` is available, otherwise opencode when
  `opencode` is available, otherwise OpenClaw when `openclaw` is available,
  otherwise Hermes when `hermes` is available.

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

If `B3EHIVE_AGENT_RUNNER` is set, it is the authoritative template. Validate-only
output must print the resolved platform, model/effort/variant/profile settings,
permission/service-tier/agent setting, and command template without leaking
secrets.

## Required Components

### Blueprint / Todo Surface

Requirements:
- Use exactly one blueprint requirement source.
- Put the authoritative execution checklist in that same blueprint.
- If the blueprint starts as prose, generate an execution checklist section into the blueprint and seed it with all `[ ]` marks before the first cron tick.
- Generate a daily `todos_YYYYMMDD.md` from that authoritative checklist section.
- Daily todos must include the current DAG of unfinished checklist items:
  - one node per `[ ]` or `[_]` unfinished item
  - dependency ids for every node
  - checkbox state (`[ ]`, `[_]`, or `[x]`)
  - worker claim state and integration-ready/blocked state
  - claim owner, if any
  - owned path scope
  - worker claim frontier, main-session integration frontier, and user concurrency saturation status
  - cycle detection result
- Daily todos must show separate counts for `[ ]`, `[_]`, and `[x]`.
- `[_]` items must appear in an integration-ready or integration-blocked section, never in the worker-claim section unless a repair child was generated.
- Successful batches must update the authoritative blueprint and then refresh today's todo.
- Worker successful batches update assigned items to `[_]`; master successful integration batches update accepted items to `[x]`.
- If the repo requires multiple completion surfaces, successful batches must reconcile all of them in the same batch.
- Todo item source references must be stable repository-relative paths (do not leak `.cron/automation_repo*` absolute paths).
- Do not let other docs become accidental requirement sources.

### Automation Repo

Run implementation in isolated clone(s) under `.cron/automation_repo*` when the main repo may be dirty.

Requirements:
- Clone/sync from the repo's authoritative remote.
- Seed the blueprint into the automation repo if it is intentionally gitignored or local-only.
- Keep `.ops/` private via `.git/info/exclude` or equivalent.
- Keep local-only artifacts ignored: typically `.cron/`, `*.log`, `Docs/todos_*.md`, `.venv/`, `tests/`, `spec/`, `target/`, `node_modules/` depending on the repo.
- Keep execution-only docs/log artifacts ignored (`docs/*validation_log*`, research handoff docs, cron-generated ledgers) unless explicitly promoted by a human.
- If local-only artifacts were historically tracked, clean them once with `git rm --cached ...` and keep local files via ignore/exclude rules.
- For multi-worker mode, use separate worker clones such as `.cron/automation_repo`, `.cron/automation_repo_slot2`, and `.cron/automation_repo_slotN` so git index and worktree writes never collide.
- Before each worker batch: `fetch + pull --ff-only` or `fetch + rebase` against the authoritative branch.
- After each worker batch: `rebase/resolve within owned scope -> push`.
- Local authoritative repo must also stay synced (`fetch + merge --ff-only`) so "remote updated but local stale" is impossible by design.
- Newly launched `tmux` agent workers must honor the selected platform configuration; for Codex, preserve the requested service tier in `codex exec`; for Claude Code, preserve the requested `--permission-mode`; for opencode, preserve the requested `--variant` and `--agent`; for OpenClaw, preserve profile, agent, and thinking level; for Hermes, preserve model, toolsets, and preloaded skill list; if unset, use and print the repo default.
- Worker count is saturated from the todo DAG order: never exceed the user's max concurrency, but do not reduce worker count merely because dependencies are unfinished or owned paths overlap.
- The main session is allowed to claim work directly, but should preferentially own integration, validation, dependency-gated closure, merge, and conflict-unblocking tasks when worker branches/worktrees land.
- Workers must not mark checklist items `[x]`. Their terminal success state is `[_]` plus evidence.
- The main session is the only actor allowed to promote `[_]` to `[x]`.
- Worker prompt root rule:
  - the prompt's `Repository root` must equal the automation clone path where the command is launched
  - include a line like `Work only inside this worker automation clone: <clone path>`
  - include a line like `Do not edit the scheduler's authoritative checkout directly: <main checkout path>`
  - generated todos, evidence paths, and blueprint references inside committed files must remain stable repo-relative paths, not clone absolute paths

### Execution Guard

Requirements:
- Maintain `.cron/*state`, log, block-count, pending-checkpoint, and last-message files.
- Enforce disk/log safety on every tick before worker spawn:
  - default `MIN_FREE_GB=30`; if the Data/root volume has less free space, run cleanup and refuse to start new workers
  - default `DANGER_FREE_GB=15`; if below this, write state `blocked_disk_space` and exit immediately after lightweight cleanup
  - default `MAX_LOG_MB=20` for worker logs and `MAX_KEEPALIVE_MB=5` for keepalive/scheduler logs; keep only the tail when files exceed the cap
  - default `LOG_RETENTION_DAYS=3`; delete old `.log`, `.out`, and `.err` files under the cron root
  - default `WORKSPACE_TTL_HOURS=48`; remove only stale, non-live `.cron/automation_repo*` or `.cron/**/workspaces/slot*` directories
  - default `MAX_CRON_ROOT_GB=30`; if the cron root remains above this after cleanup, refuse new worker spawn
  - never delete a workspace whose path is referenced by a live selected agent-runner process, `tmux`, shell, or lock/pid file
  - write cleanup decisions to a bounded janitor log, not to an unbounded cron log
- Skip overlap if another selected agent runner is already running in the same worker repo.
- Enforce a single blueprint source.
- Enforce one authoritative execution checklist inside that blueprint.
- Enforce the dual-cursor checkbox protocol: `[ ]` for not done, `[_]` for worker self-tested, `[x]` for master accepted.
- Enforce todo DAG generation for unfinished checklist items before selecting work:
  - parse item ids and dependency metadata from the authoritative checklist or a repo-local dependency map generated from it
  - reject cycles and duplicate ids
  - compute worker-claim order from `[ ]` nodes in DAG topological order and first-open layer/cluster
  - compute the main-session integration frontier from `[_]` nodes by excluding nodes whose dependencies are incomplete, whose prerequisite worker output has not landed, or whose path conflicts are unresolved
  - write both the worker claim frontier and the integration frontier into today's todo before spawning or claiming work
- Select only the first still-open cluster and keep each run bounded.
- Select the first still-open cluster before removing claimed items.
  Worker spawn may claim additional unclaimed `[ ]` nodes from that cluster in DAG/topological order until user-requested concurrency is full, even when earlier nodes are already claimed by live workers.
  Do not choose the first unclaimed cluster; that skips lower-layer ordering and violates strict layer execution. Only the main-session integration lane may decide that a later cluster can close, and only after lower DAG dependencies are complete.
- Keep worker claiming separate from integration readiness.
  The scheduler must fill available worker slots from the ordered DAG claim frontier up to the user concurrency cap, even when those nodes depend on earlier unfinished work or touch overlapping path families.
  Mark such outputs as provisional and let the main session decide merge order, conflict resolution, validation, and closure.
- Implement worker and master ledgers as independent queues.
  The worker claim ledger records reservations and liveness; only `live` reservations reduce available worker lanes.
  `finished` reservations are inputs to the integration queue and must not prevent the scheduler from scanning forward to later unclaimed open DAG nodes.
  Refresh worker self-test manifests into the claim ledger at the start of every guard tick, including drain/no-new-claim mode.
  Drain mode may disable new claims, but it must still promote completed worker self-tests from `live` or `selftest_missing` to `finished` and regenerate the todo so the worker cursor cannot freeze behind stale ledger state.
  Self-test manifest lookup must accept both session-only and item-qualified names, for example `worker_12.json` and `item_id.worker_12.json`.
  The integration queue records landed outputs, diff bytes, changed files, path conflicts, validation hints, and small-diff batch eligibility.
  Refreshing that integration metadata is master work and must not be placed on the critical path before worker refill unless the operator explicitly requests it.
- When high concurrency is requested, parallelize worker preparation safely.
  Select claim items in stable DAG/topological order under one lock, append reservations atomically, then prepare isolated workspaces and start `tmux` sessions with bounded parallelism.
  Use a configurable preparation fan-out so clone/rsync/startup overhead does not make a 90-lane request behave like a serial launcher.
- For file-level fragmented work, enforce small-file merge batching:
  - prefer same-directory grouping
  - total source bytes per batch <=100KB
  - if one file alone exceeds 100KB, run it as a single-file batch (do not skip)
- Enforce strict layer order when the blueprint defines layered work.
  - Allow execution only in the finest still-open layer.
  - If any lower-layer items remain unchecked, upper-layer items must stay unchecked.
  - If upper-layer `[x]` is detected while lower-layer `[ ]` still exists, auto-reset those upper-layer `[x]` items to `[ ]` in the authoritative blueprint, regenerate todo, and continue.
  - Block only when autoclear is disabled or re-validation still fails after autoclear.
- Detect repeated unresolved items: when the same checklist item remains unresolved for repeated ticks (default >=5), split it into child checklist items and sync blueprint/todo.
- Parent-child closure rule: if all child checklist items are `[x]`, auto-close parent as `[x]`; if any child is `[ ]`, parent must remain `[ ]`; if any child is `[_]` and none are `[ ]`, parent may become `[_]` but not `[x]`.
- Record milestone progress counts for successful commit/push batches when the repo uses notifications.
- Treat the main session as worker id `main-session` for integration claims, progress, and conflict cleanup.
  The main session may claim integration-ready DAG nodes under the active goal and may claim repair nodes that unblock merge/rebase conflicts from worker worktrees.
  Conflict cleanup must be explicit: identify both sides, preserve user/worker changes where possible, run validation, and checkpoint the consolidation only after the merged tree is coherent.
- On success, checkpoint and push changes, then sync completion back to the main blueprint and today's todo.
- Worker success means `[_]`; master success means `[x]`.
- Treat incomplete completion-surface backfill as a hard failure (for example: stage blueprint updated but overall blueprint or today's todo not updated when required).
- On no-op completion, validate and then stop instead of inventing work.
- Enforce commit-surface filtering before commit:
  - hard-drop `.cron/`, `.ops/`, logs/state artifacts, generated todo files, and model binaries from staged set
  - hard-drop `spec/` and `tests/` from staged set
  - fail commit when `docs_count > code_count` or when `code_count == 0` and `docs_count > 0`
  - if a repo keeps runnable validation packages or executable scripts under `Docs/`, classify those paths as `code/evidence` instead of prose docs for commit hygiene
  - at minimum, treat paths like `Docs/Stage3IOSPathValidation/**` and `Docs/scripts/*.sh` as `code/evidence` when they contain runnable validation logic
- Enforce sync gate around push:
  - start-of-tick sync check: local authoritative repo must complete `fetch --prune` + `ff-only` sync and HEAD equality verification before any coding
  - pre-commit sync check: local authoritative repo must be clean enough for `ff-only` sync
  - post-push sync check: local authoritative repo must fast-forward to and match remote HEAD
  - never swallow sync errors with `|| true` on the success path
  - when blocked by local tracked changes, prefer a bounded `repo force sync` (`stash -u` -> sync -> `stash pop`) before escalating to manual intervention
- Enforce live claim hygiene:
  - claims are reservations, not proof of progress
  - remove claims for completed blueprint items
  - remove claims for open items whose worker pid/process is gone
  - keep claims for open items whose worker process is still live
  - append released claims to an audit ledger with timestamp, original claim time, item id, and worker id
  - run stale-claim pruning before sync and again after sync, so a dirty main checkout cannot trap stale reservations forever
- Enforce safe dirty-sync behavior:
  - if tracked dirty files exist and active workers are still running, write a clear `blocked_sync` state and leave the worktree untouched
  - if tracked dirty files exist and no worker is active, create an audit-named `git stash push -u`, then `fetch --prune` and `merge --ff-only`
  - after syncing, verify local HEAD equals upstream HEAD before spawning workers
  - never auto-apply a stash during the success path; stash-pop conflicts require explicit operator repair
- For multi-worker mode, use a scheduler lock plus worker-specific locks.
- When lock files are managed with `flock`, treat lock-fd inheritance as a first-class failure mode:
  - close the held lock fd before every `tmux` spawn/respawn path
  - keep workers on their own state files instead of sharing the scheduler state file
  - if the guard reports repeated "previous run still active" while no real scheduler is active, inspect inherited lock holders (for example `/proc/<pid>/fd/*`) and repair before continuing
- Prefer split-lane DAG ownership over worker-side dependency throttling:
  - workers own `[ ]` implementation claims from the first-open layer/cluster in stable DAG/topological order, up to the user concurrency cap
  - the main session owns `[_]` integration closure, validation, dependency gating, and merge/conflict repair by default
  - no worker may claim outside the current ordered DAG claim frontier, but workers may produce provisional output for nodes whose dependencies are not yet integrated
- Add an integration batching lane:
  - maintain a queue of landed worker outputs with item id, dependencies, owned paths, changed files, diff bytes, and validation command hints
  - group non-conflicting landed outputs when the combined diff is <=256KiB
  - apply the group as one coherent integration batch, validate the combined tree once or with the smallest sufficient validator set, then close items in DAG order only after each item's gates pass
  - if a later item in the applied group passes code validation but an earlier dependency is not closable, leave the later item provisional in the todo/queue rather than checking it in the blueprint
  - report both worker saturation and integration throughput so operators can distinguish spawn underfill from master validation bottlenecks
- Only the integration owner should update the authoritative blueprint/todo after integrated validation; other workers should land code and evidence only.

### Cron Space Guard

Every generated execution cron must include a repo-local janitor script, for example `.cron/scripts/cron_space_guard.sh`, and call it from the top of the scheduler before any `tmux` or agent-runner launch.

Minimum behavior:
- determine the cron root from the script path, not from the caller's current directory
- cap active logs by preserving the last `MAX_LOG_MB` with `tail -c`, using a temp file plus atomic `mv`
- rotate or truncate scheduler redirection targets such as `keepalive.log` before appending more output
- clean old logs and stale workspaces before checking the cron-root budget
- verify live worker paths with self-match-safe process checks before deleting any automation repo or workspace
- return a distinct nonzero code for "budget exceeded" so the scheduler can exit without treating the tick as completed work
- keep all defaults overrideable via environment variables

### Cleanup Script

Requirements:
- Remove only the target repo's execution cron line.
- Be safe to run repeatedly.
- Leave a cleanup state/log artifact.
- Return success only when cron entry is confirmed removed (not just "script ran").

## Completion Gate

A blueprint item may be checked only when all required gates pass.

Minimum gate set:
- operable entry: CLI, service, console, or UI entry actually works
- foundation completion: model/algorithm artifacts are really downloaded and runnable; never accept mock weights or fake inference paths
- feature implemented: input -> run -> result -> evidence path is real
- feature completion: expose a real API path, run a successful call, and verify output quality matches expected behavior
- algorithm complete: core data/model/scheduling/retrieval logic exists with real inputs/outputs
- validation evidenced: `Validation Log` records commands and results

Bootstrap and reporting rule:
- before the first cron tick, the authoritative blueprint checklist must exist and start with `[ ]` marks
- after each successful worker batch, the authoritative blueprint and today's todo must both reflect `[_]` state with worker evidence
- after each successful master integration batch, the authoritative blueprint and today's todo must both reflect `[x]` state with master validation evidence
- after repeated unresolved ticks for the same `[ ]` item (default >=5), the cron must auto-split that item into child checklist items and report the split explicitly

Cleanup hard-gate rule:
- Cron cleanup must not be triggered by blueprint-only signal.
- Require at least these signals at the same tick: blueprint `[ ]` count=0 + blueprint `[_]` count=0 + latest todo `Unfinished=0` + no active automation agent-runner process + no pending checkpoint files.
- Set final state to `completed` only after cleanup script succeeds and crontab no longer contains the target guard line.

Do not mark items done for:
- doc-only work
- placeholder handlers
- fake success responses
- mocked model downloads or mocked inference/evaluation paths
- schema without runnable path
- tests without real implementation

Do not commit batch outputs for:
- test-only changes (`spec/`, `tests/`)
- validation logs / research handoff docs generated by cron loops
- todo snapshots and cron state logs

## Batch Design Rules

- Prefer the repository's own layer/order semantics.
- If the blueprint is layered, execute only the finest still-open layer first.
- Never close upper-layer items while lower-layer items remain open.
- Stay inside one cluster per batch.
- For fragmented file checklist items, merge nearby same-directory files into one bounded batch (<=100KB combined) to avoid over-fragmented single-file ticks.
- Stop after 6-8 coherent items at most.
- If the blueprint is already fully checked, validate the current tree and exit cleanly without fabricating more work.
- In multi-worker mode, keep workers claiming from the ordered DAG queue and let integration happen through git rebase/push plus authoritative repo re-sync, not by letting workers close blueprint/todo state directly.
- Scale worker count to the user-requested concurrency cap from the DAG claim frontier. If dependencies or path conflicts exist, workers may still prepare provisional implementation output; the main session must merge, validate, and close those nodes only when the DAG dependency constraints are satisfied.
- For landed worker outputs with no path conflicts and combined diff <=256KiB, prefer batch apply + combined validation over one-worker-at-a-time master validation. Blueprint closure remains dependency ordered and may be a prefix of the applied batch.

## Looper Embed Rules

When embedded in `looper-cron-builder`, execution may run only inside an active
`ResourceLease` with a `ParentLeaseRef`. Nested execution attempts can create
child implementation candidates, repair child items, or validation-focused
patches, but they cannot write `[x]` or escape parent lease budget.

The parent looper attempt owns final reward classification, no-reward
accounting, and ROI. Execution outputs remain provisional until the master lane
integrates them in DAG order and validates the authoritative checkout.

## Validation

Use the smallest real validation commands the repo supports.

Examples:
- Rust/Tauri repos: `cargo check`, `cargo test`
- Python repos: `uv sync --extra dev`, `uv run pytest -q tests`
- Node repos: `npm`/`pnpm` install plus actual test/build commands

## Local References

Read these only when needed:
- `references/execution-pattern.md` for the pattern and local repo examples
- `references/gate-rules.md` for completion gate and cleanup rules
