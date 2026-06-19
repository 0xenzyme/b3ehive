---
name: b3ehive
description: Root guide for b3ehive's six portable swarm skills: compete, execution, research, optimization, migration, and looper cron builders for Codex, Claude Code, opencode, OpenClaw, and Hermes.
---

# b3ehive Skill Index

b3ehive provides six portable `SKILL.md` directories:

- `compete-cron-builder`: bounded proposal competitions with `n` workers,
  `m` proposals, choose `k`, all-valid coverage union, repair queues, blueprint
  synthesis, and three-way challenge artifact coverage.
- `execution-cron-builder`: blueprint-driven DAG execution with worker/master
  cursors, validation gates, checkpointing, and cleanup.
- `research-cron-builder`: codebase research cron with bounded workers,
  research notes, progress tracking, and cleanup.
- `optimization-cron-builder`: design-guided architecture and optimization
  cron.
- `migration-cron-builder`: artifact-contract migration across language,
  runtime, API, schema, docs, or tool shapes.
- `looper-cron-builder`: resource-aware feedback loop daemons with
  BridgeMetrics, ResourceEnvelopes, ResourceLeases, reward ledgers, ROI, and
  no-reward pause.

## Removed Tool

`debating-cron-builder` was removed from the public toolset. Its old
three-agent workflow is covered by `compete-cron-builder` through:

```text
competition_shape = three_way_challenge
artifact_layout = old_three_way
selection_mode = vote_then_tiebreak
candidate_ids = run_a, run_b, run_c
```

Use `compete-cron-builder` for all proposal competition work.
