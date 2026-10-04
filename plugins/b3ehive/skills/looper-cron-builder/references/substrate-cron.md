# Cron And tmux Substrate

Read this file when a run uses cron, tmux, or an external agent runner. It holds
the shared runner abstraction and the disk and log guards. Every default here is
a safety cap and stays environment-overridable.

## Choosing A Substrate

- `in-session`: subagents or a workflow tool inside one agent session. Use for
  work that finishes within one session.
- `cron+tmux`: a repository-local guard on a schedule with tmux workers. Use for
  multi-hour or multi-day work.
- `flow`: an external flow runner that drives coding agents. Use when an item
  needs a relay, review, or lanes loop that the runner already implements.

Log the choice as a `DECIDE` line with the expected duration and cost.

## Agent Runner

Generated cron code must support Codex, Claude Code, Cursor,
Grok Build, opencode, OpenClaw, and Hermes via a single agent-runner
abstraction.

Default platform selection:
- `B3EHIVE_AGENT_PLATFORM=codex` uses one independent interactive Codex TUI
  process in a task-local tmux server with a private writable `CODEX_HOME` and
  exactly one submitted and authenticated `/goal` for each admitted worker
  generation. The target repository selects bounded executions or a persistent
  worker pool. Bounded results stop their TUI; persistent goals remain live and
  dead generations are replaced back to the exact target without exceeding its
  hard cap. Every request remains attributed and capped. `codex app-server`,
  shared Codex daemons, `codex exec`, and Codex without tmux are forbidden.
  Nested agents are forbidden unless the target repository explicitly enables
  and budgets them; every enabled child is an independent execution and consumes
  the same global transport, turn, request-rate, in-flight, and outstanding-
  request limits rather than hiding behind its parent worker.
- `B3EHIVE_AGENT_PLATFORM=claude` uses `claude -p`.
- `B3EHIVE_AGENT_PLATFORM=cursor` uses `scripts/run_cursor_agent.py`.
- `B3EHIVE_AGENT_PLATFORM=grok` uses `grok --always-approve --prompt-file`.
- `B3EHIVE_AGENT_PLATFORM=opencode` uses `opencode run`.
- `B3EHIVE_AGENT_PLATFORM=openclaw` uses `openclaw agent`.
- `B3EHIVE_AGENT_PLATFORM=hermes` uses `hermes chat`.
- `B3EHIVE_AGENT_PLATFORM=auto` may choose the first installed CLI from Codex,
  then Claude Code, then Cursor, then Grok Build, then opencode, then
  OpenClaw, then Hermes.

Default command templates:

```bash
# Codex interactive TUI
codex_argv=(codex -C "$WORKER_REPO" -c features.goals=true --no-alt-screen)
[[ -n "${CODEX_MODEL:-}" ]] && codex_argv+=(-m "$CODEX_MODEL")
[[ -n "${CODEX_REASONING_EFFORT:-}" ]] && \
  codex_argv+=(-c "model_reasoning_effort=$CODEX_REASONING_EFFORT")
[[ -n "${CODEX_SERVICE_TIER:-}" ]] && \
  codex_argv+=(-c "service_tier=$CODEX_SERVICE_TIER")
tmux -S "$TASK_ROOT/tmux.sock" -f /dev/null new-session -d \
  -s "$SESSION" -c "$WORKER_REPO" \
  env CODEX_HOME="$TASK_ROOT/codex-home" "${codex_argv[@]}"
# Wait for the composer, paste one short /goal with a claim-specific final
# token, poll joined composer text until that token is visible, submit once,
# then authenticate route/cwd/thread/goal before counting this lane as live.
tmux -S "$TASK_ROOT/tmux.sock" set-buffer -b goal \
  "/goal $GOAL Integrity token: $GOAL_COMPLETION_TOKEN"
tmux -S "$TASK_ROOT/tmux.sock" paste-buffer -b goal -t "$SESSION" -d
# Generated controller polls `capture-pane -p -J`; timeout fails without Enter.
tmux -S "$TASK_ROOT/tmux.sock" send-keys -t "$SESSION" C-m

# Claude Code
claude -p --model "${CLAUDE_MODEL:-sonnet}" --effort "${CLAUDE_EFFORT:-max}" \
  --permission-mode "${CLAUDE_PERMISSION_MODE:-auto}" \
  --add-dir "$WORKER_REPO" < "$PROMPT_FILE" > "$OUTPUT_FILE"

# Cursor
python3 "$B3EHIVE_ROOT/scripts/run_cursor_agent.py" \
  --workspace "$WORKER_REPO" --prompt-file "$PROMPT_FILE" > "$OUTPUT_FILE"

# Grok Build
GROK_TELEMETRY_ENABLED=0 GROK_TELEMETRY_TRACE_UPLOAD=0 \
  grok --always-approve --cwd "$WORKER_REPO" --prompt-file "$PROMPT_FILE" \
  ${GROK_MODEL:+-m "$GROK_MODEL"} ${GROK_EFFORT:+--effort "$GROK_EFFORT"} \
  > "$OUTPUT_FILE"

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

Validate-only output must print the selected platform and resolved runner. If
`B3EHIVE_AGENT_RUNNER` is set, use it instead of the default template.

## Guard Tick Budget

- Maintain `.cron/*state`, logs, progress, heartbeat, last-message files.
- Enforce disk/log safety on every tick before worker spawn:
  - default `MIN_FREE_GB=30`; when the Data/root volume has less free space,
    run cleanup and refuse to start new workers;
  - default `DANGER_FREE_GB=15`; below this threshold, write state
    `blocked_disk_space`, run lightweight cleanup, and exit immediately;
  - default `MAX_LOG_MB=20` for worker logs and `MAX_KEEPALIVE_MB=5` for
    keepalive/scheduler logs; retain only the tail after a file exceeds its cap;
  - default `LOG_RETENTION_DAYS=3`; delete old `.log`, `.out`, and `.err` files
    under the cron root;
  - default `WORKSPACE_TTL_HOURS=48`; remove only stale, non-live
    `.cron/automation_repo*` or `.cron/**/workspaces/slot*` directories;
  - default `MAX_CRON_ROOT_GB=30`; refuse new worker spawn when the cron root
    remains above this threshold after cleanup;
  - preserve every workspace whose path is referenced by a live selected
    agent-runner process, `tmux`, shell, or lock/pid file;
  - record cleanup decisions in a bounded janitor log, never an unbounded cron log.
- Support parallel `tmux` workers.
- Give each worker a disjoint, section-owned write scope.
- Reconcile worker outputs into the authoritative blueprint.
- Refresh today's todo after each successful merge.
- Classify empty or off-topic outputs as failure.
- Clean up cron when every item is `[x]`.

## Cron Space Guard

Every generated cron must include a repo-local janitor script, such as
`.cron/scripts/cron_space_guard.sh`. The guard calls it from the
top of the guard, before any `tmux` or agent-runner launch.

Minimum behavior:
- Derive the cron root from the script path, independent of the caller's current
  directory.
- Cap active logs by preserving the last `MAX_LOG_MB` with `tail -c`, a temp
  file, and atomic `mv`.
- Rotate or truncate scheduler redirection targets such as `keepalive.log`
  before appending output.
- Clean old logs and stale workspaces before checking the cron-root budget.
- Verify live worker paths with self-match-safe process checks before deleting
  any automation repo or workspace.
- Return a distinct nonzero code for "budget exceeded"; exit without marking
  progress.
- Keep every default overrideable through environment variables.

## Cleanup

- Remove only this controller's exact cron line.
- Stop guard and worker `tmux` sessions.
- With cleanup-on-complete enabled, remove repo-local `.cron/` and `.ops/`
  artifacts created only for this run.
- Keep the authoritative blueprint and completed research docs.
