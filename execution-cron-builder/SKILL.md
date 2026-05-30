---
name: execution-cron-builder
description: Build or repair a blueprint-driven execution cron for a repository using one authoritative blueprint, a daily todo snapshot, an isolated automation clone, bounded codex exec batches, validation gates, checkpoint commits, and cleanup-on-complete. Use when a repo should continuously implement a blueprint, when an execution cron needs to be added to a new repository, or when an existing blueprint-execution cron needs boundary/gate fixes.
---

# Execution Cron Builder

## Overview

Build a repository-local execution cron that wakes on a schedule, clones or syncs isolated automation repos, reads exactly one blueprint, keeps a dependency DAG for open checklist items, runs bounded `codex exec` batches, validates real implementation, checkpoints commits, and removes its own cron when the blueprint is truly complete.
Default gate posture is strict: no mock completion, and no upper-layer completion while finer layers remain open.
Default commit posture is code-first: never commit cron/private artifacts, never commit tests from automation batches, and keep docs commits less than or equal to code commits per batch.
Default orchestration posture is DAG-aware: the main session may claim work under a user goal, while tmux workers scale only up to the smaller of user-requested max concurrency and the DAG's current independent-item capacity.

## Workflow

1. Inspect the repository and identify the single blueprint source.
2. Freeze the execution boundary.
   The cron must treat exactly one file as the requirement source.
3. If the blueprint is prose-first, generate an authoritative execution checklist section into that same blueprint before enabling cron.
   Initialize every execution item as `[ ]` on first bootstrap, and generate daily todos from that authoritative checklist section only.
4. Add private `.ops/` and `.cron/` helpers locally and hide them from git where appropriate.
5. Create the four required pieces:
   - authoritative checklist/bootstrap generator
   - blueprint/todo generator
   - execution guard
   - cron installer
   - cron cleanup script
6. Run `VALIDATE_ONLY=1` once before enabling cron.
7. Install cron only after the automation repo, checklist bootstrap, blueprint seeding, and todo generation all work.
8. Keep the batch size small and cluster-bounded.
   For fragmented small files, merge same-directory file tasks into one batch with combined source size <=100KB; if a single file is >100KB, allow it as a single-file batch.
9. Enforce strict layer gating: only execute the finest still-open layer; if lower layers are open, upper layers must stay unchecked.
   If a tick finds upper-layer `[x]` while lower layers are still open, auto-reset the violating upper-layer `[x]` items to `[ ]`, report the correction, and continue from the lower layer.
10. Treat the main session as an execution participant, not only a scheduler.
   The main session may claim checklist items under the active user goal, do implementation work directly, and is responsible for clearing merge/conflict blockers caused when worker worktrees or automation branches are merged back to `main`.
11. Generate todos with the current dependency DAG for all unfinished checklist items.
   The todo must list item ids, dependency ids, blocked/ready state, claimed worker/session, owned paths, and the ready frontier.
   The DAG must be acyclic; cycle detection is a hard todo-generation failure.
12. When launching new `tmux` codex workers, use adaptive DAG concurrency instead of a fixed worker count.
   `worker_count = min(user_max_concurrency, current_ready_independent_item_count, available_disjoint_path_lanes)`, minus already-live workers and main-session claims.
   Do not spawn a worker for an item that depends on an unfinished item or conflicts with another live item's owned paths.
13. Every newly launched `tmux` codex worker must use the requested/latest high-capability model and must set `service_tier=flex` in the `codex exec` configuration.
   For example, include `-c service_tier=\"flex\"` or the equivalent supported config form in the worker launch command.
14. After every successful batch, sync completion back to the authoritative blueprint and refresh today's todo in the main repo.
15. Enforce documentation reconciliation as a success gate:
   - if a batch closes checklist items, all required completion surfaces must be updated in the same batch (for example `Overall Blueprint + Stage Blueprint + today's todo`)
   - todo references must use stable repository paths, never automation clone absolute paths
   - "code done but completion docs stale" is a failed tick and must trigger a repair batch
16. If the same `[ ]` item remains unresolved for repeated ticks (default >=5), auto-split it into child checklist items in the blueprint, regenerate today's todo, and notify the human with the split details.
17. Clean up the cron when the blueprint is complete and validation passes.
   Cleanup must use hard conditions:
   - authoritative blueprint has zero unchecked items
   - latest todo snapshot shows `Unfinished = 0`
   - no running `codex` process in automation repos
   - no pending checkpoint artifact remains
   - cleanup script succeeds and cron entry is actually removed
18. Enforce commit-surface policy at checkpoint time:
   - never stage/commit `.cron/`, `.ops/`, logs, state, generated todo snapshots, model binaries
   - never stage/commit `spec/` or `tests/` changes from execution batches
   - reject batch commit when staged docs files outnumber staged code files
   - reject docs-only batch commits
   - classify executable validation assets that live under docs-style folders as `code/evidence`, not prose docs
   - at minimum, treat paths like `Docs/Stage3IOSPathValidation/**` and `Docs/scripts/*.sh` as `code/evidence` during commit hygiene counting
19. Enforce sync-first push policy:
   - before coding (at tick start) and before checkpoint commit, local authoritative repo must `fetch --prune` + `ff-only` sync
   - at tick start, explicitly verify development machine branch HEAD equals remote tracking HEAD; if not equal, block the tick before any implementation
   - after every successful push, local authoritative repo must be synced again and verified equal to remote HEAD
   - if local sync fails (dirty tracked changes, detached HEAD, non-ff, or network failure), block the tick and do not treat batch as success
20. Add a `repo force sync` best-practice path for stuck ticks:
   - trigger condition: repeated sync blocks caused by local tracked changes
   - sequence: `stash -u` -> `fetch --prune` + `pull/rebase or ff-only merge` -> `stash pop`
   - if `stash pop` conflicts, stop and resolve conflicts explicitly, then run one consolidation commit+push
   - always log the force-sync attempt and result so operators can audit it later
21. Add lock hygiene when the guard uses `flock` and also spawns `tmux` workers:
   - never let the scheduler's locked file descriptor leak into `tmux new-session`, `tmux new-window`, or `tmux respawn-pane`
   - explicitly close the lock fd on those launches (for example `9>&-`) before `tmux` starts its server/client process tree
   - keep scheduler/global state separate from worker/slot state so a no-focus worker cannot overwrite the scheduler's authoritative status
   - if a historical lock was already leaked into a long-lived `tmux` server, rotate the lock path version or restart the affected `tmux` server/session before resuming cron
22. Ensure worker prompts use the actual automation clone as `Repository root`.
   If a worker process is launched with `cd .cron/automation_repo_slotN`, the prompt must name that clone path as the repository root and explicitly forbid direct edits to the scheduler's authoritative checkout.
   Never put the main checkout path in a worker prompt unless the worker is intentionally running in the main checkout.
23. Treat claim and dirty-sync recovery as part of the guard, not manual cleanup:
   - release claims for items that are already closed in the authoritative blueprint
   - release claims for still-open items when the assigned worker process is no longer alive
   - detect active workers with self-match-safe process patterns such as `[c]odex exec...`
   - if the main checkout has tracked dirty files and no active workers, stash with an audit label before syncing
   - if tracked dirty files exist while workers are active, block protectively instead of stashing their live work

## Required Components

### Blueprint / Todo Surface

Requirements:
- Use exactly one blueprint requirement source.
- Put the authoritative execution checklist in that same blueprint.
- If the blueprint starts as prose, generate an execution checklist section into the blueprint and seed it with all `[ ]` marks before the first cron tick.
- Generate a daily `todos_YYYYMMDD.md` from that authoritative checklist section.
- Daily todos must include the current DAG of unfinished checklist items:
  - one node per unfinished item
  - dependency ids for every node
  - blocked/ready state
  - claim owner, if any
  - owned path scope
  - ready frontier and maximum independent ready item count
  - cycle detection result
- Successful batches must update the authoritative blueprint and then refresh today's todo.
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
- Newly launched `tmux` codex workers must set `service_tier=flex` in their `codex exec` configuration.
- Worker count is adaptive from the todo DAG: never exceed the user's max concurrency, the ready independent item count, or the number of disjoint owned-path lanes.
- The main session is allowed to claim work directly and should preferentially claim integration, validation, merge, and conflict-unblocking tasks when worker branches/worktrees land.
- Worker prompt root rule:
  - the prompt's `Repository root` must equal the automation clone path where the command is launched
  - include a line like `Work only inside this worker automation clone: <clone path>`
  - include a line like `Do not edit the scheduler's authoritative checkout directly: <main checkout path>`
  - generated todos, evidence paths, and blueprint references inside committed files must remain stable repo-relative paths, not clone absolute paths

### Execution Guard

Requirements:
- Maintain `.cron/*state`, log, block-count, pending-checkpoint, and last-message files.
- Skip overlap if another `codex exec` is already running in the same worker repo.
- Enforce a single blueprint source.
- Enforce one authoritative execution checklist inside that blueprint.
- Enforce todo DAG generation for unfinished checklist items before selecting work:
  - parse item ids and dependency metadata from the authoritative checklist or a repo-local dependency map generated from it
  - reject cycles and duplicate ids
  - compute ready nodes whose dependencies are complete
  - compute independent ready capacity by excluding path-overlapping nodes and live claims
  - write the DAG summary into today's todo before spawning or claiming work
- Select only the first still-open cluster and keep each run bounded.
- Select the first still-open cluster before removing claimed items.
  If every item in that first-open cluster is currently claimed by a live worker, spawn no upper-cluster work in that tick.
  Do not choose the first unclaimed cluster; that skips lower-layer blockers and violates strict layer execution.
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
- Parent-child closure rule: if all child checklist items are `[x]`, auto-close parent as `[x]`; if any child is `[ ]`, parent must remain `[ ]`.
- Record milestone progress counts for successful commit/push batches when the repo uses notifications.
- Treat the main session as worker id `main-session` for claims, progress, and conflict cleanup.
  The main session may claim ready DAG nodes under the active goal and may claim repair nodes that unblock merge/rebase conflicts from worker worktrees.
  Conflict cleanup must be explicit: identify both sides, preserve user/worker changes where possible, run validation, and checkpoint the consolidation only after the merged tree is coherent.
- On success, checkpoint and push changes, then sync completion back to the main blueprint and today's todo.
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
- Prefer DAG lane ownership over optimistic overlap:
  - workers own ready nodes with disjoint path scopes
  - the main session owns integration closure, validation, and merge/conflict repair by default
  - no worker may start a node outside the current ready frontier
- Only the integration owner should update the authoritative blueprint/todo after integrated validation; other workers should land code and evidence only.

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
- after each successful batch, the authoritative blueprint and today's todo must both reflect the new completion state
- after repeated unresolved ticks for the same `[ ]` item (default >=5), the cron must auto-split that item into child checklist items and report the split explicitly

Cleanup hard-gate rule:
- Cron cleanup must not be triggered by blueprint-only signal.
- Require at least these signals at the same tick: blueprint unchecked=0 + latest todo `Unfinished=0` + no active automation `codex` run + no pending checkpoint files.
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
- In multi-worker mode, keep workers on DAG-independent modules and let integration happen through git rebase/push plus authoritative repo re-sync, not by editing the same files concurrently.
- Scale worker count from the DAG ready frontier, not a fixed target. If the DAG has only one ready independent item, run one worker or let the main session claim it. If the user max is lower than DAG capacity, obey the user max.

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
