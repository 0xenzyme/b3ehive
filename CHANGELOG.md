# Changelog

## 2.2.0 — 2026-10-16

- loop v2: closed result vocabulary (`validated_progress`, `repair_required`,
  `replan_required`, `user_action_required`, `wait`, `failed`); `repair_noop`
  counts as a stall; the ratchet compares against the best accepted state; two
  stalls open a replan obligation that only new evidence clears; direction
  (`grow`, `switch`, `verify`) with mechanism distance; one remediation per
  lineage; `observed_only` evidence; typed item closure.
- optimization: statistics rule (`B3_STATS`: paired alternating fresh-process
  trials, interval must exclude zero and clear the minimum effect) and
  experiment identity over the full toolchain closure.
- learn: experience ledger (`canon/lessons.tsv`, lesson and incident rows) with
  `scripts/find_lesson.py` for bounded search, activation by use-site recall,
  and separate `applied` and `helpful` records.
- compete: guard-set regressions (`REGRESSED:`), `OBSERVED_ONLY`, integrity
  suspicion (`SUSPECT:`) confirmed only by two channels, shadow mode for prompt
  and policy changes.
- execution: effect intent and readback with blocking on unknown, retry table by
  failure kind, revision fence at every admission, receipt fingerprint over
  untracked content.
- looper: `replan` before pause, novelty as secondary reward, no-spend closeouts.
- examples: RSI example prompt (`examples/rsi-prompt.md`).
- evals: four new scenarios; 10 new unit tests.

## 2.1.0 — 2026-10-08

- learn: `learn_depth=what|how|why` with per-glob `depth_map`. `how` lists the
  quality principles followed, each with evidence; `why` records driver,
  alternatives and why each is worse, tradeoff, significance, and a `V` or `I`
  level. Applies to understand, transform, translate, and canon.
- learn: `references/depth.md` and `scripts/check_depth.py`; `why` runs in loop
  shape `review`.
- evals: scenario `learn-4`.

## 2.0.0 — 2026-10-04

- One law (`core/core.md`), one loop (`looper-cron-builder/loop.md`), five skills.
- Oracle-first acceptance with receipts and fresh re-runs; blueprint grammar adds
  `oracle`, `tier`, `budget`, `canon`, and cross-blueprint dependencies.
- learn canon mode; optimization measured mode; looper as thin governance.
- compete selection fixed: oracle, blind review, votes without self-votes.
- Structure and lexicon lint, unit tests, behavior evals; install `--link`,
  version stamps, `b3ehive doctor`.
