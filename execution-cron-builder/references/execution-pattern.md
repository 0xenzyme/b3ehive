# Execution Cron Pattern

## Local reference repositories

- `/home/sansha/Github/clawdb/.ops/`
- `/home/sansha/Github/celviz/.ops/`
- `/home/sansha/Github/cvbackbone/.ops/`

## Best-practice pattern

1. Choose one blueprint file.
2. If the blueprint is prose-first, generate an authoritative execution checklist section into that same blueprint.
3. Seed the execution checklist with all `[ ]` marks before the first cron tick.
4. Generate a daily todo from that authoritative checklist section, including the current dependency DAG for unfinished items.
5. Use an isolated automation repo when the main repo may be dirty.
6. Run `codex exec --model <requested-or-latest-high-model> -c model_reasoning_effort="xhigh"` in bounded clusters.
   New `tmux` workers must also include `-c service_tier=\"flex\"` or the equivalent supported config form.
7. Enforce strict layer gate: only work on the finest still-open layer; do not close upper layers while lower layers are open.
8. Validate honestly.
9. Commit/push only real work.
10. Apply commit hygiene before every checkpoint:
   - never commit `.cron/`, logs, generated todos, or tests/spec
   - never commit model binaries; commit reproducible download scripts instead
   - docs cannot outnumber code changes in a batch, and docs-only batch commits are invalid
   - runnable validation packages/scripts stored under `Docs/` count as `code/evidence`, not prose docs
   - patterns like `Docs/Stage3IOSPathValidation/**` and `Docs/scripts/*.sh` count as `code/evidence` when they hold runnable validation logic
11. Apply sync-first push gate:
   - tick start: development machine must sync first (`fetch --prune + ff-only`) and local HEAD must equal remote tracking HEAD before coding
   - pre-commit: local authoritative repo must be syncable with `fetch + ff-only`
   - post-push: local authoritative repo must be synced and verified equal to remote HEAD
   - any sync failure blocks success and must be reported
12. Apply lock hygiene when the guard holds `flock` locks and also uses `tmux`:
   - close the held lock fd before `tmux new-session`, `tmux new-window`, and `tmux respawn-pane` so the `tmux` server cannot inherit and pin the lock
   - keep scheduler/global state separate from worker/slot state files
   - if a stale `tmux` server already inherited the lock, rotate the lock-file version or kill/restart that server before the next tick
13. Make worker prompts clone-accurate:
   - if the worker command runs in `.cron/automation_repo_slotN`, the prompt must say `Repository root: <that automation clone>`
   - explicitly instruct the worker to work only inside that clone
   - explicitly forbid direct edits to the scheduler's authoritative checkout
   - committed artifacts must still use stable repo-relative paths, not automation clone absolute paths
14. Treat claims as live reservations:
   - prune claims for items that are already `[x]`
   - prune claims for `[ ]` items when the assigned worker process is gone
   - keep claims only when the item is open and the assigned worker is still live
   - log every released claim to an audit ledger
   - use self-match-safe process checks such as `[c]odex exec...`
15. Sync the main blueprint and today's todo after each successful batch.
16. Enforce documentation reconciliation after every completion backfill:
   - if a batch closes checklist items, it must update every required status surface in the same batch (for example: authoritative blueprint + stage blueprint mirror + today's todo)
   - todo entries must point to stable repository paths (never automation clone absolute paths) so diffs stay reviewable and do not leak local runtime paths
   - treat "code done but blueprint/todo stale" as an execution failure, not a cosmetic issue
17. If the same `[ ]` item remains unresolved for repeated ticks (default >=5), auto-split it into child checklist items, regenerate today's todo, and notify the human clearly.
18. Let the main session participate as worker id `main-session` when a user goal is active.
   It may claim ready DAG items directly, and it is the default owner for validation, integration, and merge/conflict cleanup after worker worktrees or branches land on `main`.
19. Spawn `tmux` workers from the DAG ready frontier.
   Worker count is `min(user_max_concurrency, ready_independent_item_count, disjoint_path_lane_count)` minus live workers and main-session claims.
20. Remove cron when complete.

## DAG-adaptive worker pattern

Use this only when one worker is leaving material throughput on the table and the current todo DAG has multiple ready independent items with disjoint write lanes.

- Keep concurrency bounded by the user-provided max concurrency and by the DAG's independent ready capacity.
- If the DAG exposes fewer independent ready items than the user max, spawn only what the DAG can safely carry.
- If path scopes overlap, treat those nodes as dependent for scheduling even if their logical dependency lists are empty.
- Give each worker its own automation clone:
  - `.cron/automation_repo`
  - `.cron/automation_repo_slot2`
  - `.cron/automation_repo_slotN`
- Use a scheduler lock to spawn/respawn workers, and worker-specific locks so the same slot never overlaps with itself.
- When spawning workers from a locked scheduler, close the scheduler lock fd on every `tmux` launch/respawn path (for example `9>&-`) so the lock dies with the scheduler instead of living inside the `tmux` server.
- Keep the scheduler's state file authoritative; workers should write only to slot-specific state files.
- Force explicit ownership from DAG nodes and path scopes.
- The main session owns integration closure, validation, and merge/conflict repair unless a human assigns that role elsewhere.
- Every newly launched `tmux` worker command must set `service_tier=flex`.
- Require every worker batch to start with `fetch + pull --ff-only` or `fetch + rebase`.
- Require every worker push to rebase and resolve only inside that worker's owned paths.
- Keep blueprint/todo mutation centralized to one integration lane after honest validation on the combined tree.
- Re-sync or mirror the authoritative local repo after successful worker pushes so future blueprint seeding does not revert checkmarks and today's todo stays current.
- Track repeated unresolved checklist items; if one item survives >=5 ticks unresolved, split it into child checklist items and keep execution on that branch until children close.
- Never let worker prompts name the scheduler checkout as `Repository root` when the worker process is actually launched inside an automation clone. This mistake causes workers to dirty the main checkout, creates false sync blocks, and defeats clone isolation.
- When selecting work, compute the first still-open layer/cluster and then its DAG ready frontier before filtering claims. If all ready nodes in that first-open layer are claimed by live workers or the main session, do not spawn work from later layers.

## Todo DAG surface

Daily todos must include a machine-readable or consistently parseable DAG section for unfinished checklist items:

- `node_id`: stable checklist item id
- `title`: short item title
- `depends_on`: zero or more item ids
- `state`: `blocked`, `ready`, `claimed`, or `done_in_blueprint`
- `claim_owner`: `main-session`, `worker-N`, or empty
- `owned_paths`: repo-relative path scopes
- `blocks`: reverse dependencies when useful for humans

The todo generator must reject cycles, duplicate node ids, and dependencies that point to missing checklist items. The guard uses the DAG to compute the ready frontier and maximum independent ready item count before spawning workers.

## Blueprint surface styles

### Authoritative checklist in blueprint
Preferred for new execution crons.
- keep the checklist in the same blueprint file that defines the work
- initialize it with all `[ ]` marks before first execution
- generate todos from that section only
- write completed `[x]` marks back to that same blueprint after real validation

### Legacy private mirror
Allowed only as a convenience mirror after the authoritative blueprint checklist already exists.
- never treat the mirror as a second requirement source
- never let the mirror become the only place where completion is reported

## Typical runtime files

- `.cron/<project>_guard.state`
- `.cron/<project>_guard.log`
- `.cron/<project>_guard.pending_checkpoint`
- `.cron/<project>_guard.last_message.txt`
- `.cron/<project>_guard.progress`

## Common failure modes

- multiple requirement sources leaking into the prompt
- dirty automation repo blocking every tick
- worker prompt points at the main checkout while the command runs in an automation clone, so workers dirty the scheduler checkout directly
- local-only docs/tests accidentally being committed
- `.cron/`/log/state artifacts accidentally being committed
- docs-only commits or docs volume outgrowing code volume
- historical tracked local-only files not being cleaned, causing repeated accidental staging
- starting implementation while local development machine HEAD is stale versus remote
- local authoritative checkout has tracked dirty files from old or misprompted workers and the guard has no safe auto-stash/sync path
- push succeeded but local authoritative repo stayed stale due swallowed sync failure
- `tmux` server inherited the scheduler `flock` fd, so future ticks report "previous run still active" even though no real scheduler is running
- claiming model/algorithm completion with mock downloads or fake inference paths
- checking upper-layer items while finer layers still contain unchecked items
- completion never cleaning up because the guard only validates and never exits
- repeated empty no-op runs after blueprint completion
- repeated real commits with zero checklist movement because the cron keeps hammering one non-closable cluster
- repeated unresolved checklist items without automatic split into executable child items
- todo DAG missing, stale, cyclic, or inconsistent with current unchecked blueprint items
- spawning more workers than the DAG ready frontier can safely carry
- starting `tmux` workers without `service_tier=flex`
- treating the main session as scheduler-only, leaving merge conflicts from worker landings unresolved
- stale claims reserve open items for 24h even though the worker exited or failed
- first-unclaimed selection skips a lower open cluster and starts upper-cluster work
- process checks match the guard's own `pgrep` command and falsely report active workers
- worker clones pushing code while the authoritative local repo blueprint stays stale, causing later seed steps to roll completed checkmarks back
- worker clones updating the automation repo todo while the main repo todo stays stale, leaving humans with the wrong completion picture
- todo snapshots embedding `.cron/automation_repo*` absolute paths, causing noisy diffs and misleading progress references
- implementation merged while blueprint/todo completion surfaces stayed stale, creating false "not done" reports
- allowing both workers to edit root manifests or blueprint files directly, creating avoidable merge conflicts

## Dirty sync and stale claim recovery

- At tick start, prune stale claims before sync and again after sync.
- If the main checkout is tracked-dirty while live workers exist, block protectively and do not stash.
- If the main checkout is tracked-dirty and no live workers exist, run an audit-named `git stash push -u`, then `fetch --prune` and `merge --ff-only`.
- Do not auto-pop the stash on the success path. Stash pop conflicts require explicit repair.
- After every recovery sync, verify local HEAD equals upstream HEAD before spawning workers.
- Treat a successful push plus failed local sync as blocked, not successful.

## Lock leak recovery

- Symptom: repeated `skip: previous run still active` with no corresponding live scheduler workload.
- First confirm the lock holder:
  - inspect `/proc/<pid>/fd/*` for the lock path
  - if the holder is a long-lived `tmux` server or unrelated child, treat it as leaked
- Recovery sequence:
  - stop the affected session/server
  - remove stale lock files only after the holder is gone
  - if needed, rotate to a new versioned lock path so old inherited fds cannot block the new scheduler
  - relaunch the scheduler and verify the next tick acquires the lock normally
