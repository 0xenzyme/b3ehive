---
name: b3ehive
description: Root guide for b3ehive's five portable swarm skills: compete, execution, learn, optimization, and looper cron builders for Codex, Claude Code, opencode, OpenClaw, and Hermes.
---

# b3ehive Skill Index

b3ehive provides five portable `SKILL.md` directories:

- `compete-cron-builder`: bounded proposal competitions with `n` workers,
  `m` proposals, choose `k`, all-valid coverage union, repair queues, blueprint
  synthesis, and three-way challenge artifact coverage.
- `execution-cron-builder`: blueprint-driven DAG execution with worker/master
  cursors, validation gates, checkpointing, and cleanup.
- `learn-cron-builder`: source-to-target learning cron for code understanding,
  subset learning, code-to-code transform, and human-language translation.
- `optimization-cron-builder`: design-guided architecture and optimization
  cron.
- `looper-cron-builder`: resource-aware bridge controller for DAG nodes,
  BridgeSurfaces, BridgeMetrics, ResourceEnvelopes, ResourceLeases,
  SideEffectGates, OperatorSignals, nested run ledgers, compact evidence,
  reward ledgers, ROI, and no-reward pause.

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

`research-cron-builder` and `migration-cron-builder` were removed from the
public toolset. Their behavior is covered by `learn-cron-builder`:

```text
learn_mode=understand  # code -> human learning notes
learn_mode=transform   # code -> code/source contract transform
learn_mode=translate   # human language -> human language
```
