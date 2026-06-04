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
   New `tmux` workers must honor explicit `CODEX_MODEL`, `CODEX_REASONING_EFFORT`, and `CODEX_SERVICE_TIER` values. If no service tier is specified, print and use the repo default instead of silently changing the operator's requested tier.
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
15. Treat `VALIDATE_ONLY=1` as a dry gate only.
   It may validate sync, DAG, budget, and configuration state, but it must exit before worker claims or `tmux` spawn. Do not use validate-only when the purpose is to saturate worker lanes.
16. Sync the main blueprint and today's todo after each successful batch.
17. Enforce documentation reconciliation after every completion backfill:
   - if a batch closes checklist items, it must update every required status surface in the same batch (for example: authoritative blueprint + stage blueprint mirror + today's todo)
   - todo entries must point to stable repository paths (never automation clone absolute paths) so diffs stay reviewable and do not leak local runtime paths
   - treat "code done but blueprint/todo stale" as an execution failure, not a cosmetic issue
18. If the same `[ ]` item remains unresolved for repeated ticks (default >=5), auto-split it into child checklist items, regenerate today's todo, and notify the human clearly.
19. Let the main session participate as worker id `main-session` when a user goal is active.
   It may claim integration-ready DAG items directly, and it is the default owner for dependency-gated validation, integration, and merge/conflict cleanup after worker worktrees or branches land on `main`.
20. Spawn `tmux` workers from the ordered DAG claim frontier.
   Worker count is `user_max_concurrency - live_worker_count`, capped by the count of unclaimed open DAG nodes in topological order. Do not subtract main-session integration claims from worker capacity, and do not reduce worker count because dependencies are unfinished or path scopes overlap.
21. Maintain a claim ledger.
   Record item id, original blueprint id, dependency ids, session name, slot, workspace path, status, claim time, and owned path scopes. Todos must display `live:<session>`, `finished:<session>`, or `unclaimed`, plus the claim ledger path.
22. Maintain a main-session integration queue for worker outputs.
   It must scan worker workspaces, report changed files and diff byte counts, detect path conflicts, and classify combined diffs <=256KiB as small-diff batch candidates. The main session may batch apply those small diffs when conflicts are absent or explicitly resolved, but it must validate and close checklist items in DAG dependency order.
23. Run a cron space guard before spawning workers.
   Cap worker logs at 20MB, scheduler/keepalive logs at 5MB, delete logs older than 3 days, remove only stale non-live workspaces after 48 hours, refuse new workers below 30GB free space, and refuse new workers when the cron root remains above 30GB after cleanup.
24. Remove cron when complete.

## Split-lane DAG worker pattern

Use this when one worker is leaving material throughput on the table and the user has requested concurrent implementation workers. Workers prepare implementation output in DAG/topological order; the main session integrates and closes nodes in dependency order.

- Keep worker concurrency bounded by the user-provided max concurrency and the number of unclaimed open DAG nodes.
- Do not throttle worker spawn by independent ready capacity, unfinished dependencies, or overlapping path scopes. Those constraints are main-session integration gates, not worker-claim gates.
- If path scopes overlap, mark the affected nodes as integration-conflicting and require the main session to merge or serialize closure; do not use overlap alone to leave worker slots idle.
- Give each worker its own automation clone:
  - `.cron/automation_repo`
  - `.cron/automation_repo_slot2`
  - `.cron/automation_repo_slotN`
- Use a scheduler lock to spawn/respawn workers, and worker-specific locks so the same slot never overlaps with itself.
- When spawning workers from a locked scheduler, close the scheduler lock fd on every `tmux` launch/respawn path (for example `9>&-`) so the lock dies with the scheduler instead of living inside the `tmux` server.
- Keep the scheduler's state file authoritative; workers should write only to slot-specific state files.
- Force explicit ownership from DAG nodes and path scopes.
- The main session owns dependency-gated integration closure, validation, and merge/conflict repair unless a human assigns that role elsewhere.
- Every newly launched `tmux` worker command must honor the requested service tier; if none is set, use and print the repo default.
- Require every worker batch to start with `fetch + pull --ff-only` or `fetch + rebase`.
- Require every worker push to rebase and resolve only inside that worker's owned paths when possible; if a dependency or path conflict requires cross-node judgment, leave it for the main-session integration lane.
- Keep blueprint/todo mutation centralized to one integration lane after honest validation on the combined tree and after DAG dependencies are satisfied.
- Re-sync or mirror the authoritative local repo after successful worker pushes so future blueprint seeding does not revert checkmarks and today's todo stays current.
- Track repeated unresolved checklist items; if one item survives >=5 ticks unresolved, split it into child checklist items and keep execution on that branch until children close.
- Never let worker prompts name the scheduler checkout as `Repository root` when the worker process is actually launched inside an automation clone. This mistake causes workers to dirty the main checkout, creates false sync blocks, and defeats clone isolation.
- When selecting worker work, compute the first still-open layer/cluster and then its ordered DAG claim frontier before filtering claims. Fill worker slots from unclaimed nodes in that frontier, even if earlier nodes are live, dependency-blocked for integration, or path-overlapping.
- When selecting integration work, compute the dependency-ready frontier from landed worker outputs and close only nodes whose dependencies, validation gates, and merge/conflict constraints are satisfied.
- When integrating worker work, batch small outputs only when combined diff bytes are <=256KiB and path conflicts are absent or explicitly resolved. Apply diffs as a coherent group for speed, then close blueprint items in DAG dependency order after validation.

## Todo DAG surface

Daily todos must include a machine-readable or consistently parseable DAG section for unfinished checklist items:

- `node_id`: stable checklist item id
- `title`: short item title
- `depends_on`: zero or more item ids
- `worker_state`: `unclaimed`, `claimed`, `landed`, or `done_in_blueprint`
- `integration_state`: `blocked`, `integration_ready`, `integrating`, or `closed`
- `claim_owner`: `main-session`, `worker-N`, or empty
- `owned_paths`: repo-relative path scopes
- `blocks`: reverse dependencies when useful for humans

The todo generator must reject cycles, duplicate node ids, and dependencies that point to missing checklist items. The guard uses the DAG to compute two frontiers: an ordered worker claim frontier for saturating worker sessions up to the user concurrency cap, and a dependency-ready integration frontier for the main session.

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
- `.cron/scripts/cron_space_guard.sh`

## Space and log budget

Every scheduler tick must call a bounded cleanup helper before `tmux` or `codex exec` launch.

- Use environment-overridable defaults: `MIN_FREE_GB=30`, `DANGER_FREE_GB=15`, `MAX_LOG_MB=20`, `MAX_KEEPALIVE_MB=5`, `LOG_RETENTION_DAYS=3`, `WORKSPACE_TTL_HOURS=48`, `MAX_CRON_ROOT_GB=30`.
- Trim active logs by keeping the tail with `tail -c` and atomic `mv`; avoid unbounded `>> keepalive.log` growth.
- Delete only stale workspaces whose paths are not referenced by live `codex`, `tmux`, shell, pid, or lock state.
- If cleanup cannot bring the cron root under budget, write `blocked_disk_space` state and skip worker spawn.

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
- validate-only dry runs misread as execution ticks, so no workers are launched even though concurrency is available
- repeated unresolved checklist items without automatic split into executable child items
- todo DAG missing, stale, cyclic, or inconsistent with current unchecked blueprint items
- throttling worker sessions to the dependency-ready frontier instead of filling the user-requested concurrency from the ordered DAG claim frontier
- silently overriding the operator-requested worker service tier
- treating the main session as scheduler-only, leaving merge conflicts from worker landings unresolved
- stale claims reserve open items for 24h even though the worker exited or failed
- first-unclaimed selection skips a lower open cluster and starts upper-cluster work
- process checks match the guard's own `pgrep` command and falsely report active workers
- worker clones pushing code while the authoritative local repo blueprint stays stale, causing later seed steps to roll completed checkmarks back
- worker clones updating the automation repo todo while the main repo todo stays stale, leaving humans with the wrong completion picture
- todo snapshots embedding `.cron/automation_repo*` absolute paths, causing noisy diffs and misleading progress references
- implementation merged while blueprint/todo completion surfaces stayed stale, creating false "not done" reports
- allowing workers to close blueprint/todo state directly instead of leaving dependency-gated closure to the main-session integration lane
- unbounded slot logs, keepalive logs, or stale automation workspaces consuming the Data volume
- master integration validating worker outputs one by one even when multiple non-conflicting diffs total <=256KiB and could be batch-applied before dependency-ordered closure

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
