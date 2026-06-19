---
name: learn-cron-builder
description: Build or repair a source-to-target learning cron for code understanding, subset learning, code-to-code transformation, API/schema/runtime/tool transformation, or human-language translation. Use when a repo needs code-to-human learning notes, strict one-to-one source file plus source-tree output coverage, explicit or fuzzy subset learning, code-to-code transformation, documentation translation, route-policy selection, dual-cursor checklists, master-only acceptance, or cleanup after all learning artifacts are validated.
---

# Learn Cron Builder

Build a repository-local learning pipeline that converts a frozen source scope
into validated learning or transformation artifacts.

Core frame:

```text
understand it until make it
```

## Modes

```text
learn_mode=understand
  code -> human language
  Produces one-to-one learning notes and source-tree understanding artifacts.

learn_mode=transform
  code -> code
  Produces code-to-code, API/schema/runtime transformation, SDK generation,
  adapter generation, or tool asset conversion artifacts.

learn_mode=translate
  human language -> human language
  Produces documentation language conversion and localization artifacts.
```

The workflow is always:

```text
source scope -> subset policy -> source manifest -> target contract
-> worker output [_] -> master validation [x] -> cleanup
```

## Non-Negotiable Contract

- Generate a locked `source_manifest.tsv` before workers claim items.
- Use `[ ]`, `[_]`, and `[x]` as the only checkbox states.
- Workers may only advance `[ ] -> [_]`.
- The master lane is the only actor that may advance `[_] -> [x]`.
- Cleanup treats `[ ]` and `[_]` as unfinished.
- Completion requires zero `[ ]`, zero `[_]`, and passing coverage indices.

For `learn_mode=understand`, final artifacts must be one-to-one with source
files and preserve source-tree shape.

Required final examples:

```text
src/app/main.ts
  -> Docs/learn/files/src/app/main.ts_learn.md

.github/workflows/ci.yml
  -> Docs/learn/files/.github/workflows/ci.yml_learn.md

src/app/
  -> Docs/learn/src/app/current_folder_learn.md

repo root
  -> Docs/learn/current_folder_learn.md
```

Opaque slug-only final paths are invalid. Group and chunk reports may exist only
as intermediate artifacts.

## Subset Support

Subset is first-class.

Explicit subset examples:

```text
src/auth/**
packages/compiler/**
files touched by this branch
language=rust
```

Fuzzy subset examples:

```text
algorithm subset
scheduler core
inference path
payment risk surface
```

For fuzzy subsets, generate:

```text
Docs/learn/subsets/<subset_id>/subset_candidates.tsv
Docs/learn/subsets/<subset_id>/subset_decision.md
Docs/learn/subsets/<subset_id>/source_manifest.tsv
```

Context-only files may be read by workers but must not produce final artifacts
or count toward completion unless promoted into the locked source manifest.

## Required Surfaces

Base files:

```text
Docs/learn/source_manifest.tsv
Docs/learn/learn_checklist.md
Docs/learn/todos_YYYYMMDD.md
Docs/learn/file_learn_index.tsv
Docs/learn/folder_learn_index.tsv
Docs/learn/route_decision.md
```

Transform mode additionally requires:

```text
Docs/learn/target_contract.md
Docs/learn/mapping_policy.tsv
Docs/learn/validation_policy.md
Docs/learn/traceability_index.tsv
```

## Route Policy

Route choice is part of the contract:

```text
route_policy=auto|high_reasoning|standard|cheap_translation|uncommon_translation|custom
```

Defaults:

- `understand`: high reasoning for complex code, standard for small/simple files.
- `transform`: high reasoning for code/API/schema/runtime, standard for
  mechanical tool asset conversion.
- `translate`: cheap or uncommon translation route by default; escalate only
  for high-stakes meaning, code-heavy semantics, glossary conflicts, repeated
  validator failure, or explicit human request.

Write route decisions to:

```text
Docs/learn/route_decision.md
```

## Validation

Before declaring a learn cron ready:

- Validate `source_manifest.tsv` covers exactly the locked source scope.
- Validate final per-file artifacts are exactly one-to-one with source files.
- Validate folder artifacts cover every represented folder.
- Validate `[_]` is never treated as complete.
- Validate workers cannot write `[x]`.
- Validate subset output excludes out-of-scope files.
- Validate transform outputs carry source-target traceability.
- Validate translate outputs preserve headings, anchors, links, code blocks,
  tables, glossary decisions, and section parity.
- Run the cron space guard.
- Run `bash -n` on generated shell helpers.

## Looper Embed Rules

When embedded in `looper-cron-builder`, learn may run only inside an active
`ResourceLease` with a `ParentLeaseRef`. Learn outputs are provisional until
the looper or owning master lane accepts them.

Nested learn runs cannot write `[x]`, cannot escape the parent lease budget,
and produce reward candidates only. Their token, wall-clock, human-review,
disk, and output costs roll into the parent looper attempt before reward and
ROI accounting. Paused loops cannot start nested learn runs.

## References

Read only the relevant reference:

- `references/coverage-contract.md` for strict 1:1 file tree, grouping,
  chunking, folder synthesis, and subset coverage rules.
- `references/route-policy.md` for mode-specific route selection and escalation.
- `references/learn-pattern.md` for full workflow, components, and behavior
  coverage.
