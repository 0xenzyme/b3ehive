# Measured Mode

## Oracle Contract

Freeze this before any candidate runs. Workers read it and never edit it.

| Field | Meaning | CUDA kernel example |
|---|---|---|
| definition | inputs, outputs, shapes, types, layout | shapes, dtypes, strides |
| workloads | cases drawn from real use, covering its dynamic range | sampled production traces |
| reference | a trusted implementation | PyTorch or CPU version |
| tolerance | what counts as correct | element-wise bound, relative L2, all finite, state error |
| measurement | how numbers are taken | warmup, repeats, events or CUPTI, cold cache, locked clocks |
| baseline | best known implementation with source and version; never chosen by the agent | current SOTA kernel |
| anti-gaming | checks a gamed result fails | refill inputs after timing and re-check; secret seeds; holdout cases; evaluator outside the workspace |
| `oracle.fast` | quick check for iteration | one shape |
| `oracle.full` | acceptance check | every shape, fresh inputs |
| tier | evidence fidelity needed for acceptance | named GPU model |

## Ledgers

`hypotheses.tsv`:

| Column | Meaning |
|---|---|
| `id` | stable id |
| `parent` | candidate it builds on |
| `evidence` | profile values behind it |
| `canon` | cited entries |
| `expected` | predicted gain |
| `measured` | `oracle.full` result on fresh inputs |
| `decision` | `kept`, `reverted`, or `rejected` |
| `reason` | one line |

`candidates.jsonl` holds one row per candidate: parent, change summary, receipt
path, per-workload rows, and the aggregate recomputed by the master.

## Instruments

`instruments.tsv`:

| Column | Meaning |
|---|---|
| `id` | `ncu`, `nsys`, `perf`, `py-spy`, `explain` |
| `probe` | command proving the instrument exists; failure means absent |
| `capability` | what it measures |
| `skill` | bound domain skill, if any |
| `playbook` | diagnosis playbook path |

Playbook entries read: signals → cause → first fix → deeper fixes → exceptions.

## Loop Discipline

- Shorten feedback: iterate on one workload with `oracle.fast`, widen with
  `oracle.full` before submitting.
- Change one thing per candidate; keep alternatives switchable for paired
  measurement.
- A stalled direction stops after five attempts unless new evidence appears.
- Stop reasons are exact: `target_reached`, `budget_spent`,
  `no_actionable_bottleneck`, `capability_exhausted`, `reference_parity`, or a
  written blocker.
