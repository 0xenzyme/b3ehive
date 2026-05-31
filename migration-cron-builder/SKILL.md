---
name: migration-cron-builder
description: Build or repair a generalized migration cron for a repository. Use when artifacts need to be continuously translated from one contract to another, such as Claude-compatible assets to Codex-compatible assets, one human language of documentation to another, one programming language to another, one API/schema/runtime shape to another, or when an execution cron needs to be generalized into a source-to-target transformation pipeline with validation, checkpoints, and cleanup.
---

# Migration Cron Builder

## Overview

Build a repository-local migration pipeline that converts a frozen source set into a frozen target contract over repeated cron ticks.

Migration here means **contracted transformation**, not only tool compatibility. Typical migrations include:

- AI tool assets: Claude Code agents, skills, hooks, rules, docs, templates, and settings -> Codex-ready equivalents
- Documentation language: Chinese docs -> English docs, English docs -> Japanese docs, or multilingual doc parity
- Programming language: Python module -> Rust crate, JavaScript SDK -> TypeScript SDK, shell utility -> Python CLI
- Interface shape: REST API -> typed SDK, JSON schema v1 -> schema v2, legacy config -> new config
- Runtime or architecture: one service layout -> another service layout, old execution surfaces -> new execution surfaces

This skill is the migration generalization of an execution cron: instead of "read blueprint -> implement missing work", it runs "read source contract -> produce target artifact -> validate equivalence -> checkpoint progress".

## Core Contract

Every migration cron must freeze these five things before installation:

1. **Source scope**: the exact files, directories, schemas, languages, APIs, or artifacts being migrated.
2. **Target contract**: the destination format, language, runtime, compatibility layer, or behavioral interface.
3. **Mapping policy**: one-to-one by default; allow one-to-many, many-to-one, or generated index artifacts only when explicitly recorded.
4. **Validation policy**: type-specific gates that prove the target artifact is useful and traceable.
5. **Output root**: the only place migrated artifacts may be written, unless the user explicitly chooses in-place migration.

Default output root: `Docs/migrated/`.

For code migrations, prefer a runnable target package or module tree under a target-specific root, for example `migrations/rust/`, `sdk/typescript/`, or `translated/python/`, when `Docs/migrated/` would hide executable artifacts in a docs folder.

## Workflow

1. Inspect the repository and identify the migration intent.
   Do not assume Claude -> Codex unless the source tree or user request says so.
2. Create an authoritative migration spec before building cron:
   - source scope
   - target contract
   - mapping policy
   - output root
   - validators
   - explicit non-goals
3. Generate an authoritative migration checklist from the spec.
   Each item must name one source artifact, one target artifact, and one validation gate.
4. Add private runtime state under `.cron/` and repo-local helpers under `.ops/`.
5. Create the required pieces:
   - migration spec/checklist generator
   - daily todo generator
   - migration execution/status helper
   - migration guard
   - cron space/log guard
   - worker runner
   - cron installer
   - cron cleanup script
6. Use isolated worker clones for parallel execution unless the migration is read-only plus generated-output-only and the repo is clean.
7. Workers must not mutate source artifacts.
   If in-place migration is required, use a separate staging clone and merge only after validation.
8. Validate every target artifact before copying or syncing it back into the authoritative repo.
9. Defer repeat validation failures within each shard so fresh items keep flowing.
10. Run the guard manually before installing cron.
11. Install cron only after checklist generation, todo generation, status reporting, one manual worker pass, and one disk/log budget guard pass all succeed.
12. Remove only this migration cron when all checklist items are complete and cleanup gates pass.

## Migration Spec

Create a stable spec file, usually:

```text
Docs/migration/MIGRATION_SPEC.md
```

Minimum fields:

- `Migration name`
- `Source contract`
- `Target contract`
- `Source scope`
- `Output root`
- `Mapping policy`
- `Validation policy`
- `Traceability policy`
- `Rollback policy`
- `Completion gate`

The spec is the single source of truth. Daily todos and worker prompts must be generated from it and the authoritative checklist, not from ad hoc repo scans after installation.

## Output Contract

Default checklist item format:

```text
- [ ] source/path.ext -> target/path.ext | validator: <command or rule>
```

Default target artifact requirements:

- carries source path and migration spec id
- states target contract version when relevant
- preserves semantics or documents intentional changes
- has a type-appropriate validator
- does not overwrite source artifacts

Allowed mapping modes:

- `one-to-one`: one source artifact produces one target artifact
- `one-to-many`: one source artifact produces several target files, with an index entry
- `many-to-one`: several source artifacts consolidate into one target artifact, with all source paths listed
- `generated-support`: indexes, manifests, adapters, and compatibility helpers required by migrated outputs

Use `one-to-one` unless another mode is necessary and recorded in the spec.

## Presets

### Claude Code -> Codex Assets

Use this preset when the source scope is Claude-native:

- `.claude/agents/*.md` -> `Docs/migrated/agents/*.md`
- `.claude/skills/*/SKILL.md` -> `Docs/migrated/skills/*/SKILL.md`
- `.claude/hooks/*.sh` -> `Docs/migrated/tools/hooks/*.sh`
- `.claude/rules/*.md` -> `Docs/migrated/tools/rules/*.md`
- `.claude/settings.json` -> `Docs/migrated/tools/settings.json`
- `.claude/docs/**` -> `Docs/migrated/docs/**`
- Claude-only templates -> `Docs/migrated/project-templates/**`

Validation examples:

- agent markdown: frontmatter + explicit Codex traceability + required workflow sections
- skill markdown: Codex skill frontmatter + required sections
- hook shell: shebang + `set -euo pipefail` + `bash -n`
- settings JSON: valid JSON with Codex runtime fields

### Documentation Language Migration

Use this preset when the source and target are natural languages.

Requirements:

- preserve headings, anchors, code blocks, tables, admonitions, and links
- maintain glossary decisions in `Docs/migration/GLOSSARY.md`
- validate that every source section has a target section
- flag untranslatable product names instead of inventing replacements
- keep target docs reviewable as diffs

### Programming Language Migration

Use this preset when code is translated across languages.

Requirements:

- create target build files before broad translation
- migrate one module or package at a time
- preserve public API behavior or record intentional API changes
- add parity tests, fixtures, or golden outputs
- run target compiler/typechecker/test command before marking complete
- keep generated compatibility adapters separate from hand-authored migrated code

### Schema / API / Runtime Migration

Use this preset when the migration changes interfaces rather than files alone.

Requirements:

- define old and new contracts in the spec
- produce adapters, changelogs, or compatibility shims when needed
- validate representative old inputs against new outputs
- record breaking changes explicitly
- keep a rollback path until all consumers are migrated

## Validation Rules

Type-specific validation should be strict enough to block junk outputs:

- markdown/docs: structure parity, link sanity, traceability, glossary compliance when relevant
- code: compile/typecheck/lint/test or a runnable smoke command
- shell: shebang + `set -euo pipefail` + `bash -n`
- JSON/YAML/TOML: parser validation plus schema or shape checks
- API/schema: sample input/output parity and compatibility notes
- generated adapters: runnable example or integration smoke test
- multilingual docs: source section coverage and glossary consistency

Do not mark a migration item complete for:

- summary-only rewrites
- target files without source traceability
- code that compiles only because behavior was stubbed
- docs that omit sections silently
- translated text that changes technical meaning without recording the change
- adapters with no runnable smoke path

## Runtime Rules

- Default concurrency: `5` when shards have disjoint target paths.
- Default model: `gpt-5.4`.
- Default reasoning effort: `xhigh`.
- Scheduler should only spawn one worker per slot when its pid is not alive.
- Every scheduler tick must run a repo-local cron space guard before spawning workers:
  - default `MIN_FREE_GB=30`; if the Data/root volume has less free space, run cleanup and refuse to start new workers
  - default `DANGER_FREE_GB=15`; if below this, write state `blocked_disk_space` and exit after lightweight cleanup
  - default `MAX_LOG_MB=20` for worker logs and `MAX_KEEPALIVE_MB=5` for scheduler logs; keep only the tail when files exceed the cap
  - default `LOG_RETENTION_DAYS=3`; delete old `.log`, `.out`, and `.err` files under the cron root
  - default `WORKSPACE_TTL_HOURS=48`; remove only stale, non-live `.cron/automation_repo*` or `.cron/**/workspaces/slot*` directories
  - default `MAX_CRON_ROOT_GB=30`; if the cron root remains above this after cleanup, refuse new worker spawn
  - never delete a workspace whose path is referenced by a live worker process, pid file, lock file, or `tmux` session
  - write cleanup decisions to a bounded janitor log, not to an unbounded cron log
- Workers must write only the target artifact(s) assigned by the current checklist item.
- Workers must not edit source artifacts.
- Scheduler progress should be queryable via a machine-readable status command.
- Keep failed items in the checklist with a failure ledger instead of repeatedly blocking the same shard.
- Sync only validated outputs into the authoritative repo.

## Cron Space Guard

Every generated migration cron must include `.cron/scripts/cron_space_guard.sh` or an equivalent helper and call it from the top of the migration guard.

Minimum behavior:
- determine the cron root from the script path, not from the caller's current directory
- cap active logs by preserving the last `MAX_LOG_MB` with `tail -c`, using a temp file plus atomic `mv`
- rotate or truncate scheduler redirection targets such as `keepalive.log` before appending more output
- clean old logs and stale workspaces before checking the cron-root budget
- verify live worker paths with self-match-safe process checks before deleting any automation repo or workspace
- return a distinct nonzero code for "budget exceeded" so the guard can exit without marking migration progress
- keep all defaults overrideable via environment variables

## Cleanup Gate

Only clean up when:

- authoritative migration checklist has zero unchecked items
- current todo shows zero unfinished items
- every completed item has a target artifact or recorded generated-support output
- validators pass for the completed target set
- no worker pid file points to a live process
- cleanup script successfully removes the migration cron entries
