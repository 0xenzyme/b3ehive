# b3ehive Codex Plugin

[中文说明](README.zh-CN.md)

b3ehive is a Codex plugin for running bounded multi-agent work. It bundles five
skills that cover proposal competition, blueprint execution, source learning,
architecture optimization, and resource-aware feedback loops.

This plugin does not add an MCP server, app, or hook. Its behavior comes from
the bundled `SKILL.md` directories under `skills/`.

## Skills

- `compete-cron-builder`
- `execution-cron-builder`
- `learn-cron-builder`
- `optimization-cron-builder`
- `looper-cron-builder`

## How To Choose A Skill

| Need | Use | What it produces |
|---|---|---|
| Compare possible routes before committing to one | `compete-cron-builder` | Candidate proposals, selected plan, coverage union, repair queue, or execution handoff |
| Execute a confirmed blueprint in a repository | `execution-cron-builder` | DAG checklist, daily todo, worker batches, validation gates, checkpoints, cleanup |
| Understand, transform, or translate a source scope | `learn-cron-builder` | Source manifest, coverage contract, learning notes, transformed code, or translated docs |
| Turn a design philosophy into architecture refinement work | `optimization-cron-builder` | `Stage_*_AR_Blueprint.md` and per-item optimization research docs |
| Add bounded feedback, resource control, reward, and ROI tracking | `looper-cron-builder` | Loop specs, resource leases, evidence ledgers, reward/ROI records, pause/resume control |

The skills are not a fixed pipeline. Pick the first skill from the uncertainty
you actually have:

- If the route is unclear, start with `compete-cron-builder`.
- If the source is unclear, start with `learn-cron-builder`.
- If the architecture direction is clear but needs refinement work, start with
  `optimization-cron-builder`.
- If the blueprint is already confirmed, start with `execution-cron-builder`.
- If repeated attempts, metrics, budgets, or human feedback must be controlled,
  add `looper-cron-builder` around the work.

## Skill Details And Trigger Conditions

### `compete-cron-builder`

Use this when a task benefits from bounded competition between routes,
implementations, audits, or repairs.

Trigger it when you need:

- `n` workers, `m` proposals, and `choose k`.
- A three-way challenge under `run_a`, `run_b`, and `run_c`.
- Best-one selection, top-k synthesis, coverage union, risk union, or repair
  queue.
- Multiple independent proposals before writing a feature blueprint.
- A safer handoff into `execution-cron-builder` or `looper-cron-builder`.

Good prompts:

```text
Use compete-cron-builder to compare implementation routes for this feature and synthesize a blueprint.
Use compete-cron-builder with three proposals and choose the safest plan.
Use compete-cron-builder to run a coverage sweep for risks in this API.
```

Boundary: this skill may produce proposals, findings, selected plans, and
handoff metadata. It should not mark execution checklist items `[x]`; final
acceptance belongs to the execution or looper master lane.

### `execution-cron-builder`

Use this when there is one authoritative blueprint and the job is to implement
it with real validation.

Trigger it when you need:

- A repository-local execution cron for one blueprint.
- A dependency DAG for open checklist items.
- Worker/master split lanes, where workers produce `[_]` and the master lane
  accepts `[x]`.
- Validation gates, checkpoint commits, cleanup-on-complete, and bounded
  worker batches.
- Repair of an existing blueprint-execution cron whose gates or boundaries are
  wrong.

Good prompts:

```text
Use execution-cron-builder for this repo and this confirmed blueprint.
Use execution-cron-builder to build a DAG todo and validation gate for this spec.
Use execution-cron-builder to repair the existing execution cron boundaries.
```

Boundary: this is the main skill for doing implementation work from a confirmed
blueprint. It should read exactly one authoritative requirement source before
generating todos or worker prompts.

### `learn-cron-builder`

Use this when the work starts with understanding, transforming, or translating a
bounded source scope.

Trigger it when you need:

- Code-to-human learning notes.
- Strict one-to-one source file plus source-tree coverage.
- Explicit or fuzzy subset learning.
- Code-to-code transformation, API/schema/runtime/tool conversion, SDK
  generation, or adapter generation.
- Human-language documentation translation.
- A `source_manifest.tsv`, route policy, coverage contract, and master-only
  acceptance.

Good prompts:

```text
Use learn-cron-builder to understand this package into one-to-one learning notes.
Use learn-cron-builder in transform mode for this API schema migration.
Use learn-cron-builder to translate these docs with source coverage validation.
```

Boundary: this is not the default feature-implementation skill. Its main output
is validated learning, transform, or translation artifacts. Those artifacts can
feed a later blueprint, but they are not automatically accepted product code.

### `optimization-cron-builder`

Use this when the user provides a design philosophy and wants structured
architecture refinement rather than direct product implementation.

Trigger it when you need:

- A bounded `Stage_*_AR_Blueprint.md`.
- At most 100 architecture refinement checklist items.
- Per-item research docs under `Docs/researches/Stage_*_AR/`.
- Parallel worker ownership by blueprint section.
- A repo-specific optimization plan filtered through a stated design
  philosophy.

Good prompts:

```text
Use optimization-cron-builder with this design philosophy: reduce cognitive load and simplify extension points.
Use optimization-cron-builder to derive an AR blueprint for this stage.
Use optimization-cron-builder to research each architecture refinement item before implementation.
```

Boundary: this skill does not directly implement product code by default. It
creates optimization research and an AR blueprint that can later be executed by
`execution-cron-builder`.

### `looper-cron-builder`

Use this when work needs repeated attempts under explicit resource, reward, and
side-effect control.

Trigger it when you need:

- Bounded attempts around DAG nodes, bridge surfaces, bridge metrics, product
  validation goals, benchmark lanes, or monitoring signals.
- Resource leases, budgets, compact evidence ledgers, reward signals, ROI
  tracking, and no-reward pause rules.
- Side-effect gates for risky writes, publishing, deletion, spend, or external
  calls.
- Operator-controlled feedback loops and re-funded resume after a paused loop.
- Nested b3ehive skill attempts with attribution and master acceptance.

Good prompts:

```text
Use looper-cron-builder to control repeated validation attempts around this benchmark lane.
Use looper-cron-builder to add ROI tracking and no-reward pause rules to this workflow.
Use looper-cron-builder around these bridge surfaces and side-effect gates.
```

Boundary: looper is a feedback overlay, not a cyclic dependency graph. It should
attach loops beside DAG nodes or bridge surfaces and let the master lane accept
final completion only after validation passes.

## Common Workflows

### New Feature With Unclear Route

```text
compete-cron-builder -> execution-cron-builder
```

Use `compete-cron-builder` to generate and compare proposals, then hand the
selected blueprint to `execution-cron-builder` for implementation.

### Existing Codebase You Do Not Understand Yet

```text
learn-cron-builder -> compete-cron-builder -> execution-cron-builder
```

Use `learn-cron-builder` to freeze source coverage and produce validated notes
or transforms. Use `compete-cron-builder` only if multiple implementation
routes remain plausible.

### Architecture Improvement

```text
optimization-cron-builder -> execution-cron-builder
```

Use `optimization-cron-builder` to derive the AR blueprint and research docs.
Use `execution-cron-builder` only after the AR blueprint is accepted as the
authoritative implementation source.

### Long-Running Work With Feedback Or Budget Risk

```text
execution-cron-builder + looper-cron-builder
```

Use `execution-cron-builder` for the DAG implementation path and
`looper-cron-builder` for repeated attempts, metric movement, reward/ROI
accounting, side-effect gates, and pause/resume control.

## Shared Concepts

`DAG` means `Directed Acyclic Graph`: a directed dependency graph with no
cycles. In b3ehive, it is the task dependency order. Downstream work should not
be accepted until upstream dependencies are accepted.

All five skills share the dual-cursor checklist protocol:

- `[ ]` means not done.
- `[_]` means worker self-tested, awaiting master acceptance.
- `[x]` means master accepted after validation.

Workers may move `[ ] -> [_]`. The master lane is the only actor that may move
`[_] -> [x]`.

## Install

From the repository root:

```bash
codex plugin marketplace add .
codex plugin add b3ehive@b3ehive
```

From GitHub:

```bash
codex plugin marketplace add weiyangzen/b3ehive
codex plugin add b3ehive@b3ehive
```

Start a new Codex thread after installation so the bundled skills are loaded.

## Source Of Truth

The root skill directories are the source of truth:

```text
compete-cron-builder/
execution-cron-builder/
learn-cron-builder/
optimization-cron-builder/
looper-cron-builder/
```

`plugins/b3ehive/skills/` is the packaged copy. Before release, run the sync
command from the repository root:

```bash
scripts/sync_codex_plugin.sh
```

See [docs/codex-plugin.md](../../docs/codex-plugin.md) for the full install,
maintenance, validation, and release contract.
