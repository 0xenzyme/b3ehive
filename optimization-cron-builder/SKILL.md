---
name: optimization-cron-builder
description: Build or repair a design-idea-guided optimization cron for a repository. Use when the user provides a design philosophy and wants a Stage_*_AR_Blueprint.md with <=100 checklist items, per-item SOTA optimization research docs under Docs/researches/Stage_*_AR/, parallel tmux workers, Codex or Claude Code agent-runner batches, and cleanup-on-complete.
---

# Optimization Cron Builder

## Overview

Build a repository-local optimization pipeline that does not implement product code directly. Instead, it continuously scans one stage blueprint through a user-supplied design philosophy, derives a bounded AR checklist, writes per-item optimization research docs, tracks progress, runs parallel `tmux` workers with a selected agent runner, and removes its own cron setup when the AR blueprint is complete.

`AR` means `Architecture Refinement` here, but the pattern works for any stage-specific optimization blueprint.

## Workflow

1. Inspect the target repository and find the single authoritative blueprint source for the stage.
2. Capture the user-supplied design philosophy in one short stable sentence.
3. Generate one authoritative `Docs/Stage_*_AR_Blueprint.md` with:
   - a bounded checklist count
   - exactly one item per optimization topic
   - no more than 100 items
   - grouped sections that can be owned by parallel workers
4. Define the completion gate for every `[ ]` item:
   the item may be checked only when a corresponding doc exists under `Docs/researches/Stage_*_AR/` and that doc is:
   - fully about that item
   - aligned to the design philosophy
   - based on stable SOTA or mature frontier practice
   - translated into concrete recommendations for the repository
5. Add private `.ops/` and `.cron/` helpers locally and hide them from git where appropriate.
6. Create the required pieces:
   - AR blueprint tools
   - daily todo generator
   - optimization guard
   - cron space/log guard
   - worker runner
   - install script
   - cleanup script
7. Run the guard once in `VALIDATE_ONLY=1`.
8. Install cron only after validate-only succeeds and the disk/log budget guard passes.
9. Start parallel `tmux` workers with disjoint section ownership.
10. Reconcile section snapshots back into the authoritative AR blueprint and refresh today's todo after each worker batch.
11. When all AR items are complete, remove cron entries, stop tmux sessions, and clean repo-local cron helpers if cleanup is requested.

## Required Components

### AR Blueprint

Requirements:
- Use exactly one authoritative AR blueprint file.
- Keep total checklist items `<= 100`.
- Choose a research grain that is specific enough for one item to map to one optimization doc.
- Put stable repository-relative output paths into checklist items whenever useful.
- Group checklist items into worker-ownable sections.

### Per-Item Research Output

Requirements:
- Output root: `Docs/researches/Stage_*_AR/`
- One doc per checklist item.
- Every doc must stay inside its own topic boundary.
- Every doc must explicitly filter recommendations through the user design philosophy.
- Prefer stable SOTA over novelty theater.
- Prefer decisions that reduce complexity, cognitive load, and future rework.

### Optimization Guard

Requirements:
- Maintain `.cron/*state`, logs, progress, heartbeat, last-message files.
- Enforce disk/log safety on every tick before worker spawn:
  - default `MIN_FREE_GB=30`; if the Data/root volume has less free space, run cleanup and refuse to start new workers
  - default `DANGER_FREE_GB=15`; if below this, write state `blocked_disk_space` and exit immediately after lightweight cleanup
  - default `MAX_LOG_MB=20` for worker logs and `MAX_KEEPALIVE_MB=5` for keepalive/scheduler logs; keep only the tail when files exceed the cap
  - default `LOG_RETENTION_DAYS=3`; delete old `.log`, `.out`, and `.err` files under the cron root
  - default `WORKSPACE_TTL_HOURS=48`; remove only stale, non-live `.cron/automation_repo*` or `.cron/**/workspaces/slot*` directories
  - default `MAX_CRON_ROOT_GB=30`; if the cron root remains above this after cleanup, refuse new worker spawn
  - never delete a workspace whose path is referenced by a live selected agent-runner process, `tmux`, shell, or lock/pid file
  - write cleanup decisions to a bounded janitor log, not to an unbounded cron log
- Support parallel `tmux` workers.
- Assign workers by section ownership, not overlapping write scopes.
- Reconcile worker section snapshots back into the main AR blueprint.
- Refresh today's todo after each successful merge.
- Treat empty or off-topic docs as failure, not progress.
- Clean up cron when all AR items are checked.

### Cron Space Guard

Every generated optimization cron must include a repo-local janitor script, for example `.cron/scripts/cron_space_guard.sh`, and call it from the top of the optimization guard before any `tmux` or agent-runner launch.

Minimum behavior:
- determine the cron root from the script path, not from the caller's current directory
- cap active logs by preserving the last `MAX_LOG_MB` with `tail -c`, using a temp file plus atomic `mv`
- rotate or truncate scheduler redirection targets such as `keepalive.log` before appending more output
- clean old logs and stale workspaces before checking the cron-root budget
- verify live worker paths with self-match-safe process checks before deleting any automation repo or workspace
- return a distinct nonzero code for "budget exceeded" so the guard can exit without marking optimization progress
- keep all defaults overrideable via environment variables

### Cleanup

Requirements:
- Remove only this repo's optimization cron line.
- Stop guard and worker `tmux` sessions.
- Remove repo-local `.cron/` and `.ops/` artifacts created only for the optimization run when cleanup-on-complete is enabled.
- Keep the authoritative blueprint and completed research docs.

## Codex / Claude Code Compatibility

Generated optimization cron code must support both Codex and Claude Code via a
single agent-runner abstraction.

Default platform selection:
- `B3EHIVE_AGENT_PLATFORM=codex` uses `codex exec`.
- `B3EHIVE_AGENT_PLATFORM=claude` uses `claude -p`.
- `B3EHIVE_AGENT_PLATFORM=auto` may choose the first installed CLI from Codex,
  then Claude Code.

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
```

Validate-only output must print the selected platform and resolved runner. If
`B3EHIVE_AGENT_RUNNER` is set, use it instead of the default template.

## Batch Rules

- Prefer exactly 5 workers when the blueprint can be partitioned cleanly into 5 sections.
- Each worker owns one section only.
- Workers may update only:
  - their owned section in the clone-local AR blueprint
  - their owned output directory under `Docs/researches/Stage_*_AR/`
- The main repo authoritative blueprint is updated only by the guard merge step.
- Keep prompts explicit about design philosophy, completion rules, and owned output scope.

## Validation

Always do these checks before declaring the optimization cron ready:
- `bash -n` on all created shell scripts
- one authoritative AR blueprint generation pass
- one daily todo generation pass
- one `VALIDATE_ONLY=1` guard run
- `crontab -l` verification after install
- `tmux ls` verification after worker launch
- non-empty output verification for completed items

## Repair Rules

When the AR blueprint is wrong:
- stop workers first
- regenerate the blueprint from the same design philosophy and source scope
- preserve existing `[x]` marks only when the corresponding research docs still exist and remain non-empty
- regenerate today's todo before resuming

When workers produce docs that are broad but not item-pure:
- do not mark the item complete
- split the checklist item or narrow the doc title and scope
- rerun only the affected section

## Local References

Read these only when needed:
- `references/optimization-pattern.md`
- `references/repair-playbook.md`
