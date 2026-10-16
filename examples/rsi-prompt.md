# RSI Example Prompt

[中文](rsi-prompt.zh-CN.md)

This is an **RSI (recursive self-improvement) example prompt** for b3ehive. It
runs two loops at once:

- the **object loop** improves a target (a repository, a kernel, a research
  result) under a frozen oracle;
- the **instrument loop** improves the tools doing the improving: b3ehive's own
  skills, validators, and scripts. Each accepted instrument change makes later
  object cycles better.

"Recursive" here means the engineering cycle (propose, test, review, retain)
applies to its own machinery. It is not a claim of autonomous model
improvement: the master accepts every change, the oracle stays frozen, and every
instrument change is revertible.

## The Prompt

Replace the angle-bracket fields, then paste it into an agent session with
b3ehive installed.

```text
Use b3ehive. Goal: improve <TARGET> against <OBJECTIVE> within <BUDGET>, and
improve the instruments you use while doing it.

Setup, once:
1. learn: build a canon for <TARGET> from its specs, docs MCP servers, and source;
   open canon/lessons.tsv.
2. execution: write <TARGET>_Blueprint.md. The first item builds the oracle:
   oracle.fast, oracle.full, a holdout set, anti-gaming checks, and statistics
   (paired fresh-process trials, interval must exclude zero). Every later item
   names its oracle, tier, budget, and canon.
3. looper: lease <BUDGET>; governance on.

Each cycle:
1. Recall: run find_lesson.py search "<current symptom>" before choosing work.
2. Propose: compete lanes with three hypotheses that differ in mechanism; each
   states its direction (grow, switch, verify) and mechanism distance.
3. Test: run the item loop. The ratchet compares against the best accepted
   state; REGRESSED fails a candidate; OBSERVED_ONLY is kept, never ranked.
4. Review: a non-author reviewer from another model family reads the repository,
   not the summary. Done means nothing was faked, stubbed, or special-cased.
5. Retain: the master accepts [x]. Add a lesson row (trigger, action, validation,
   stop, evidence) only for a validated attempt, then activate it with a
   use-site query.
6. Route on the result field: validated_progress moves on; repair_required gets
   one remediation per lineage; replan_required must cite evidence absent from
   the stalled window; two stalls open a replan obligation; three pause the loop.

Instrument loop:
- Log friction with every skill, script, validator, and route you use.
- After every <N> accepted items, cluster the friction into one improvement item
  for the instrument itself. Run it as its own [ ] -> [_] -> [x] item: shadow-mode
  compete on the frozen gold set (evals/scenarios.json), promote only when quality
  holds and token and latency ratios stay within caps. It must be revertible and
  weaken no core law.

Stop when the objective is met under oracle.full with intervals excluding zero,
when the lease ends, or when the third stall leaves the replan obligation open.

Report: accepted changes with receipts; rejected hypotheses with measurements;
lessons added and activated; instrument changes with their measured effect.
```

## How It Maps To b3ehive

| Step | Module |
|---|---|
| canon, lessons | learn `canon` mode; `scripts/find_lesson.py` |
| blueprint, oracle-first item | execution; core law 2 |
| hypotheses in lanes | compete; loop shape `lanes`; direction and mechanism distance |
| measurement and ratchet | optimization `measured` mode; `B3_STATS`; loop v2 ratchet |
| independent review | loop shape `review`; compete blind review |
| retention | lesson ledger; master acceptance |
| result routing, replan obligation, pause | loop v2 results; looper governance |
| instrument loop | core law 7; compete shadow mode; `evals/` ablation |

## Variants

- **Kernel optimization:** `<TARGET>` is a kernel; the canon includes the
  hardware vendor's docs MCP and papers; instruments include `ncu` and `nsys`;
  the oracle contract follows `optimization-cron-builder/references/measured-mode.md`.
- **Research:** the oracle is a dev set for iteration and a holdout set for
  acceptance; a finding becomes confirmed only after an independent reviewer
  approves the same evidence digest.
- **Repository maintenance:** run execution in `persistent_pool`; incidents go to
  the lesson ledger and are searched before every repair.
