# Codex TUI Transport

Read this file whenever the selected platform is Codex. It holds the complete
Codex worker transport contract moved verbatim from v1; the v2 SKILL.md keeps
only the transport-agnostic invariants.

## Transport Invariants

1. Codex transport for every admitted worker generation is exactly
   task-local tmux + interactive Codex TUI + one submitted and authenticated
   `/goal` + private writable `CODEX_HOME`. The frozen repository specification
   explicitly selects `bounded` or `persistent_pool`; logical/service identity
   implies a live goal only when that specification defines a one-to-one
   persistent worker mapping.
2. Codex app-server, app-server JSON-RPC, `codex exec`, shared Codex daemons,
   shared tmux servers, shared writable Codex state, and no-tmux Codex workers
   are hard failures. There is no fallback.
3. Goal authentication, a running model turn, an outbound request start, and
   an in-flight API request are distinct states with distinct counters. Every
   submission requires an atomic request lease before Enter; no scheduler,
   watchdog, cron, or goal continuation may bypass it.
4. Lifecycle is not inferred. In `bounded` mode a result/handoff terminalizes
   the goal and transport. In `persistent_pool` mode the authenticated goal is
   the long-running worker: it remains live until explicit stop or liveness
   failure, and the controller replaces a dead generation without exceeding the
   desired or hard worker cap. Authorized goal continuation is counted work,
   never an untracked request or an excuse to create an extra worker.
5. A parent execution does not hide child-agent or subagent concurrency. Unless
   the repository-local specification explicitly admits nested agents, they are
   forbidden. If admitted, every child has an independent execution identity,
   transport, turn, request lease, outstanding-request slot, terminal result,
   and full accounting under the same global caps; a child is never "free"
   capacity behind one worker count.

## Codex Transport

Generated controllers must freeze and test these equivalent values:

```text
WORKER_TRANSPORT=tmux_codex_tui
WORKER_GOAL_COMMAND=/goal
APP_SERVER_WORKERS=forbidden
CODEX_PROCESS_ISOLATION=one_process_tree_per_claim
CODEX_STATE_ISOLATION=one_writable_home_per_claim
WORKER_LIFECYCLE=repository_specified
PERSISTENT_SERVICE_TUI=repository_specified
AUTOMATIC_GOAL_CONTINUATION=repository_specified_and_counted
MAX_OUTSTANDING_REQUESTS_PER_EXECUTION=1
```

### Launch Shape

Construct argv as an array. Apply model, reasoning, provider, and service-tier
arguments only when explicitly selected by repository/operator policy;
otherwise let installed Codex configuration choose and record the resolved
route after startup.

```bash
codex_argv=(codex -C "$WORK_ROOT" -c features.goals=true --no-alt-screen)
[[ -n "${CODEX_MODEL:-}" ]] && codex_argv+=(-m "$CODEX_MODEL")
[[ -n "${CODEX_REASONING_EFFORT:-}" ]] && \
  codex_argv+=(-c "model_reasoning_effort=$CODEX_REASONING_EFFORT")
[[ -n "${CODEX_SERVICE_TIER:-}" ]] && \
  codex_argv+=(-c "service_tier=$CODEX_SERVICE_TIER")

tmux -S "$TASK_ROOT/tmux.sock" -f /dev/null new-session -d \
  -s "$SESSION" -c "$WORK_ROOT" \
  env -u CODEX_CI -u CODEX_THREAD_ID -u CODEX_REMOTE_PAYLOAD \
  CODEX_HOME="$TASK_ROOT/codex-home" \
  "${codex_argv[@]}"
```

Each claim receives its own tmux server/socket/session and ordinary interactive
Codex OS process tree. Do not host multiple claims in windows or panes of one
server. Do not import Codex into the controller, multiplex claims through a
service, or reuse another claim's wrapper/native process.

Bootstrap each `CODEX_HOME` with only required credentials and minimal
route/provider configuration. Do not copy project trust history, plugins,
marketplaces, MCP servers, prior threads, goals, logs, or SQLite registries.

### Goal Handshake

Use a controller-owned immutable claim card. Keep `/goal` short: identify the
claim, deliverable, task root, claim-card path/digest, result path, and hard
boundaries. Put detailed ownership, dependencies, acceptance commands, and
artifact rules in the claim card.

For exactly one goal per worker generation:

1. Start the TUI and handle only currently active first-run/trust prompts.
2. Detect the real idle composer, not a selector or stale scrollback glyph.
3. Paste `/goal <objective>` through a task-local tmux buffer.
4. Append a claim-specific completion token to the short objective and poll
   `capture-pane -p -J` until that final token is visible in the active composer.
   PTY input is ordered, so the final token proves the preceding `/goal` text
   arrived. Paste completion and key delivery are not assumed synchronous under
   load. A timeout retires the launch; it never submits partial input.
5. Atomically acquire both a running-turn lease and an outbound-request lease,
   then submit once. Never spray duplicate Enter keys or resend `/goal`
   blindly. If either lease is unavailable, leave the complete text unsubmitted
   or retire the prepared lane according to repository policy.
6. Authenticate thread, active goal, route, cwd, and task-local registry.
7. Apply the frozen lifecycle. A bounded result terminalizes the exact goal and
   transport. A persistent worker remains active across maintenance cycles;
   normal continuation is authorized only for that generation and counts under
   the same request/in-flight caps. On process/goal death, explicit stop, or
   identity ambiguity, retire that generation before admitting its replacement.

### Startup State Machine

Use lifecycle-specific durable states such as:

```text
reserved -> materialized -> tmux_started -> goal_pasted -> request_leased
         -> goal_submitted -> turn_running -> handoff_ready
         -> goal_terminal -> transport_stopped -> finished

persistent_reserved -> materialized -> tmux_started -> goal_pasted
                    -> request_leased -> goal_submitted -> authenticated_live
authenticated_live -> maintenance_cycle -> authenticated_live
authenticated_live -> dead_or_stopped -> generation_retired
generation_retired -> replacement_reserved
```

`tmux_started` consumes live-transport capacity; `request_leased` consumes
outbound request capacity; `goal_submitted` consumes one outstanding-request
slot; and only a proved `turn_running` consumes running-turn capacity. A
`goal_submitted` lane whose exact tmux/PID identity remains alive may stay
`starting` until a configurable hard deadline and be promoted by a later tick
when registry writes appear. Do not relaunch merely because authentication is
slow. Release or repair dead/mismatched lanes with bounded retries. A provider
event sequence that starts another turn after a bounded result without a new
controller request lease is unauthorized. In persistent mode, continuation is
authorized only while the exact generation and goal are live and the request is
accounted under the frozen caps. A replacement never overlaps a generation that
has not been proved dead, fenced, or explicitly stopped.

### Liveness

Count a Codex lane only when all are true:

- claim route and transport policy are valid
- task-local tmux server and session exist
- pane PID and process start time match the durable claim
- cwd equals the claim work root
- task-local `CODEX_HOME` is unique to the claim
- resolved route satisfies every explicitly frozen route field
- thread ID and active goal ID/status match the task-local registries
- goal objective names the claim

Broad process-name counts are telemetry, never liveness proof. Stop a bounded
claim immediately after its durable result; keep a persistent generation only
while all liveness facts remain true. Cleanup must
also terminate claim-descended subprocesses identified by recorded PID/start
time, task cwd, or task-local environment, without touching unrelated Codex
processes on the host.

## Other Agent Platforms

The controller may expose adapters for Claude Code, Cursor, Grok Build,
opencode, OpenClaw, or Hermes. Preserve explicit platform settings and validate
each adapter's own identity. `B3EHIVE_AGENT_RUNNER` may define non-Codex
runners. For Codex it may customize TUI argv only; it cannot bypass tmux,
interactive `/goal`, independent process/state, or authentication requirements.
Cursor workers use `scripts/run_cursor_agent.py`. Grok Build workers use
`grok --always-approve --prompt-file`.

## Startup Procedure

For one claim:

1. Create the task root, independent work files, immutable claim card, and
   minimal private CODEX_HOME.
2. Start one tmux server with one interactive Codex TUI process tree.
3. Record pane PID and `/proc` start time before sending input.
4. Handle active first-run/trust screens once.
5. Detect the real idle composer.
6. Paste one short `/goal` ending in a claim-specific completion token; poll
   joined composer text until that final token is visible, or fail without
   submitting partial input.
7. Acquire atomic turn and request leases, submit once, and persist
   `goal_submitted` plus the submission receipt.
8. Read the private thread/goal registries and verify route, cwd, objective, and
   active status before persisting authenticated transport state.
9. Apply the frozen lifecycle: terminalize and stop a bounded result, or keep an
   authenticated persistent generation alive across maintenance cycles. Every
   continued persistent request stays attributed to that generation and the
   same caps. Retire a dead generation before admitting its replacement.

If registration is delayed but tmux/PID identity remains exact, preserve the
starting lane until its hard deadline. A later tick promotes it. If identity is
lost, route is wrong, the objective mismatches, or the deadline expires, retire
that task safely and record the failure. Never switch transports.
