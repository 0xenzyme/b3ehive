---
name: research-cron-builder
description: Build or repair a code-research cron for a repository using a generated research checklist, daily todo snapshots, parallel workers, key rotation, checkpoints, and cleanup-on-complete. Use when a repo needs long-running codebase research, progress tracking, cron/tmux worker orchestration, repair of broken research progress tables, or migration of the existing research-cron pattern to a new repository.
---

# Research Cron Builder

## Overview

Build a code-only research pipeline that continuously reads source files, writes research docs into `Docs/researches/`, tracks progress in a generated checklist, rotates `kimi` keys, checkpoints progress, and removes its own cron entries when research is complete.

Final research artifacts must be one-to-one with the original researched files and must preserve the source tree shape under `Docs/researches/`: every source file in scope must have exactly one per-file research document at `Docs/researches/<source_path>_research.md`, even if files were grouped together for efficient worker prompts. Every represented source folder must have exactly one folder report at `Docs/researches/<folder_path>/current_folder_research.md`; the repository root report is `Docs/researches/current_folder_research.md`.

## Workflow

1. Inspect the target repository state before changing anything.
2. Decide the research scope.
   Default: code-only scope. Exclude docs, `Docs/researches/`, dependency caches, runtime directories, and generated artifacts unless the user explicitly wants doc research too.
3. Add private `.ops/` and `.cron/` helpers locally and hide them from git with `.git/info/exclude` or repo-local ignore strategy.
4. Create the four required scripts:
   - `generate_research_blueprint_checklist.sh`
   - `generate_daily_research_todo.sh`
   - `research_guard.sh`
   - `cleanup_research_cron.sh`
5. Also create `.cron/scripts/cron_space_guard.sh` and call it at the top of every `research_guard.sh` tick before spawning workers.
6. If small-file grouping is used, also create a deterministic split/index step that converts each completed group report into per-file reports at their source-tree-aligned paths.
7. If oversized files are in scope, create a chunk manifest and a deterministic merge step that researches 256 KiB chunks before writing one merged per-file report.
8. Generate folder-level research after file-level research completes, using the per-file research index as the source of truth.
9. Generate the checklist once, then verify it contains real pending items and a manifest mapping every source file to exactly one work item or chunk set.
10. Run the guard manually once before installing cron.
11. Install cron only after the manual run proves the pipeline can claim work, write bounded logs, and pass the disk/log budget guard.
12. Use dual cursors for parallel research.
   The researcher claim cursor keeps claiming unchecked, unclaimed source shards up to the requested worker concurrency.
   Finished group/chunk/file reports move to a curator queue for split, merge, index reconciliation, folder synthesis, and checklist closure; they must not consume researcher capacity or prevent later unclaimed shards from starting.
13. If progress tables are broken, regenerate the checklist from repository state and reconcile `[x]` marks from existing research documents.
14. On completion, remove cron entries and set the state file to `completed` only after the per-file 1:1 output check and folder-level index check pass.

## Grouped Input, Per-File Output

Workers may group many small files into a single prompt to reduce overhead. When doing so:
- Group small files only at the research-input stage; the final artifact contract remains per-file.
- Keep each group at or below 256 KiB of source input by default unless the user sets a different limit.
- Put oversized single files in their own group.
- Require each group prompt to return a separate, clearly titled section for every file in that group, in manifest order.
- After a group completes, immediately split its report into `Docs/researches/<source_path>_research.md` so every original file gets its own research document in a path that mirrors the original repository tree.
- Maintain `Docs/researches/file_research_index.tsv` with `source_path`, `research_file`, `group_id`, `group_research_file`, and `status`.
- Treat the run as incomplete if any source file lacks a non-empty per-file research document or if any index row has a non-OK status.
- Do not use opaque slug-only directories such as `Docs/researches/files/<slug>_research.md` for final per-file artifacts. Slugs are allowed only for internal temporary artifacts such as grouped reports or chunk reports.

## Oversized File Chunking, Per-File Merge

Files larger than the group input limit must not be sampled when the user asks for complete research. Instead:
- Split each oversized file into ordered chunks at or below 256 KiB of source input by default, preferably on line boundaries.
- Maintain `Docs/researches/chunk_manifest.tsv` with `source_path`, `chunk_id`, `chunk_order`, `chunk_start_line`, `chunk_end_line`, `chunk_research_file`, and `status`.
- Prompt each chunk as a partial view of exactly one source file and require chunk reports to cover APIs, control flow, state, dependencies, risks, and unresolved cross-chunk references visible in that chunk.
- After all chunks for a file are OK, merge their chunk reports into one `Docs/researches/<source_path>_research.md` document for the original file.
- The merged per-file report must explicitly say it was synthesized from chunks, preserve the original `source_path`, summarize whole-file purpose/exports/control flow/integration/risk, and include a compact chunk map.
- Maintain only one final per-file row in `Docs/researches/file_research_index.tsv` for the original source file; chunk rows belong only in `chunk_manifest.tsv`.
- Treat the run as incomplete if any oversized file has missing chunks, non-OK chunk rows, or a missing/non-empty merged per-file research document.

## Folder-Level Research

After file-level research is complete, create folder-level code-function summaries:
- Generate `Docs/researches/<folder_path>/current_folder_research.md` for every folder represented by researched files, including the repository root as `Docs/researches/current_folder_research.md`.
- Maintain `Docs/researches/folder_research_index.tsv` with `folder_path`, `research_file`, `direct_file_count`, `recursive_file_count`, `direct_child_folder_count`, and `status`.
- Derive folder summaries from `file_research_index.tsv` and the per-file research docs unless the user explicitly asks for a second model pass over folder contents.
- Each folder report should include child folders, direct files, recursive purpose signals, integration signals, risk/test signals, and an explicit note when its role is inferred from file-level research rather than direct folder-level model reading.
- Treat the run as incomplete if any represented folder lacks a non-empty folder research document or if any folder index row has a non-OK status.

## Required Output Layout

The final research tree must visually mirror the original repository tree.

Required examples:
- Source file `src/app/main.ts` -> `Docs/researches/src/app/main.ts_research.md`
- Source file `.github/workflows/ci.yml` -> `Docs/researches/.github/workflows/ci.yml_research.md`
- Source folder `src/app` -> `Docs/researches/src/app/current_folder_research.md`
- Repository root folder `.` -> `Docs/researches/current_folder_research.md`

Validation must fail if final file reports live only under slug buckets such as `Docs/researches/files/` or final folder reports live only under `Docs/researches/folders/`. Internal grouped/chunk reports may remain in `Docs/researches/groups/` and `Docs/researches/chunks/`, but `file_research_index.tsv` and `folder_research_index.tsv` must point to the source-tree-aligned final report paths.

## Required Components

### Checklist Generator

Create `Docs/researches/blueprint_checklist.md` from the repository tree.

Requirements:
- Preserve existing `[x]` marks when regenerating.
- Write atomically via a temp file then `mv`.
- Exclude `.git/`, `.cron/`, `Docs/researches/`, caches, build outputs, and dependency directories.
- Prefer code-only filtering unless the user explicitly wants doc research.
- Represent ungrouped work as `- [ ] [FILE] path` or grouped work as `- [ ] [GROUP] group-id ...`.
- For grouped work, write a stable manifest such as `Docs/researches/research_groups.tsv` that lists every file in each group and preserves group order.
- For oversized chunked files, write `Docs/researches/chunk_manifest.tsv` and represent chunk work as `- [ ] [CHUNK] chunk-id source-path ...` or as grouped chunk work when chunks can be batched safely.
- The manifest must cover each in-scope file exactly once.

### Daily Todo Generator

Create `Docs/researches/todos_YYYYMMDD.md` from the checklist.

Requirements:
- Show snapshot counts: done, pending, pending groups/files, and total source files covered.
- List only unchecked items.
- If pending is zero, render a single completed line instead of an empty section.
- Regenerate idempotently.

### Research Guard

The guard owns runtime behavior.

Requirements:
- Maintain `.cron/research_guard.state`, `.cron/research_guard.log`, `.cron/research_guard.block_count`.
- Enforce disk/log safety on every tick before worker spawn:
  - default `MIN_FREE_GB=30`; if the Data/root volume has less free space, run cleanup and refuse to start new workers
  - default `DANGER_FREE_GB=15`; if below this, write state `blocked_disk_space` and exit immediately after lightweight cleanup
  - default `MAX_LOG_MB=20` for worker logs and `MAX_KEEPALIVE_MB=5` for keepalive/scheduler logs; keep only the tail when files exceed the cap
  - default `LOG_RETENTION_DAYS=3`; delete old `.log`, `.out`, and `.err` files under the cron root
  - default `WORKSPACE_TTL_HOURS=48`; remove only stale, non-live `.cron/automation_repo*` or `.cron/**/workspaces/slot*` directories
  - default `MAX_CRON_ROOT_GB=30`; if the cron root remains above this after cleanup, refuse new worker spawn
  - never delete a workspace whose path is referenced by a live `codex exec`, `tmux`, shell, or lock/pid file
  - write cleanup decisions to a bounded janitor log, not to an unbounded cron log
- Support `tmux` worker fan-out for parallel research.
- Claim work under a lock so workers do not duplicate batches.
- Keep researcher claims and curator validation as separate queues:
  - claim ledger states must distinguish `live`, `finished`, `curating`, `ok`, and `failed`
  - only live researcher processes reduce available worker lanes
  - finished worker outputs enter a curator queue and do not block the guard from scanning forward to unclaimed unchecked items
  - daily todos must show both the researcher claim frontier and the curator frontier, with counts for live, finished-awaiting-curation, ok, failed, and unclaimed
  - heavy curator scans such as per-file split validation, chunk merge checks, and folder-index synthesis should run after worker refill, incrementally, or behind an explicit refresh flag
- When the requested concurrency is high, select claims under one lock but prepare worker prompts/workspaces with bounded parallelism so clone, sync, and startup overhead do not serialize the whole run.
- Rotate `kimi` keys on auth/quota/rate-limit failures.
- Distinguish between `completed`, `idle_waiting`, `exec_failed`, `exec_timeout`, and `running_exec`.
- Reconcile checklist marks from existing non-empty research docs.
- For grouped input, split completed group reports into per-file reports before marking the run complete.
- For oversized files, reconcile chunk reports first, then merge all OK chunks for a source file into exactly one per-file research document before marking the source file OK.
- Generate or refresh folder-level research only after the per-file 1:1 check is OK.
- Do not set state to `completed` until the per-file output count equals the source file count and every index row is OK.
- Do not set state to `completed` until the folder research index also covers every represented folder with OK rows.
- Commit checkpoint progress with `docs(research): ...` messages when appropriate.
- Emit milestone notifications if the repository uses progress alerts.
- Run cleanup when pending items reach zero and cleanup is enabled.

### Cron Space Guard

Every generated research cron must include a repo-local janitor script, for example `.cron/scripts/cron_space_guard.sh`, and call it from the top of `research_guard.sh`.

Minimum behavior:
- determine the cron root from the script path, not from the caller's current directory
- cap active logs by preserving the last `MAX_LOG_MB` with `tail -c`, using a temp file plus atomic `mv`
- rotate or truncate scheduler redirection targets such as `keepalive.log` before appending more output
- clean old logs and stale workspaces before checking the cron-root budget
- verify live worker paths with self-match-safe process checks before deleting any automation repo or workspace
- return a distinct nonzero code for "budget exceeded" so the guard can exit without marking research complete
- keep all defaults overrideable via environment variables

### Cleanup Script

Remove only the target repo's research cron lines.

Requirements:
- Match both the daily todo line and the research guard line.
- Be safe when run multiple times.
- Record a cleanup state/log file under `.cron/`.

## Repair Rules

When a research repo is already in motion and the progress table is wrong:
- Stop workers first.
- Regenerate the checklist from repository state.
- Reconcile `[x]` marks from existing `*_research.md` and `current_folder_research.md` files.
- Regenerate today's todo.
- Resume workers only after counts look sane.

When the checklist file becomes `0 bytes`:
- Fix the generator to use atomic writes.
- Rebuild the checklist immediately.
- Copy the repaired checklist to any alternate progress-table alias the repo expects.

## Validation

Always perform these checks before declaring the cron ready:
- `bash -n` on all `.ops/*.sh`
- manual checklist generation
- manual todo generation
- one manual `research_guard.sh` run
- if grouping is used, run the split/index step and verify `source_file_count == per_file_research_doc_count == file_research_index_rows`, where `per_file_research_doc_count` counts only `Docs/researches/<source_path>_research.md` final artifacts
- if oversized files are chunked, verify every `chunk_manifest.tsv` row is OK and every oversized source file has exactly one merged per-file research document
- run folder research generation and verify `folder_research_index_rows == folder_research_doc_count` with all rows OK, where folder docs are `current_folder_research.md` files in source-tree-aligned directories
- sample several `file_research_index.tsv` rows and confirm each per-file document names the same source path and contains substantive content from the matching group section
- sample at least one folder report and confirm it lists real child folders/files and derives signals from matching per-file docs
- `crontab -l` verification after install
- log/state verification under `.cron/`

## Best Practices

### Key Pool vs Concurrency

When scaling research concurrency, treat key-pool size as a first-class capacity limit.

Required practice:
- Before increasing `MAX_PARALLEL_RESEARCH`, proactively gather keys from all approved sources and deduplicate them.
- Recommended key sources: `KIMI_KEYS_FILE`, `KIMI_KEYS_EXTRA_FILES`, `KIMI_API_KEYS`, `KIMI_API_KEY`.
- Target `unique_key_count >= MAX_PARALLEL_RESEARCH` whenever possible.
- If keys are fewer than workers, keep worker-slot key sharding enabled and log an explicit warning with both counts.
- If sustained auth/quota/rate-limit failures appear, first expand key pool, then re-balance worker-to-key spread; do not only increase retries.

Implementation guidance:
- Use deterministic worker-slot offsets so workers start from different key indices.
- Persist per-worker key index state to avoid synchronized retries on the same key.
- Keep global fallback rotation for non-worker runs and crash recovery.
- Include `worker_slot` and `key_index` in failure logs so skew is visible during incident review.

## Local References

Read these only when needed:
- `references/research-pattern.md` for the full pattern and repository examples
- `references/repair-playbook.md` for progress-table repair and cleanup rules
