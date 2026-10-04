# b3ehive loop v1

A loop repeats attempts on one item until its oracle passes and the master
accepts, or until its lease ends.

## Shapes

- `single`: one worker per attempt.
- `relay`: model families alternate; each turn opens a fresh session; the
  repository and its notes are the only memory.
- `review`: an actor works; each round a fresh, read-only, non-author reviewer
  judges the repository, not the actor's summary.
- `lanes`: attempts run in parallel; compete selects.

## Rules

- Each attempt submits a receipt and reports `ADVANCED`, `STALLED`, or `REGRESSED`.
- Two stalls: replan. Three: pause the loop and report why.
- Ratchet: keep a change only if the oracle measures it better and still
  correct; otherwise revert.
- Log each rejected hypothesis with its measurement; retry it only on new evidence.
- A verdict that can end a loop carries a round cap.
- Iterate on `oracle.fast`; submit on `oracle.full`.
- Paused loops resume on new budget and a new strategy, never alone.

## Ablation

`B3_LOOP=full|single|null` selects the module variant: all shapes, `single` only,
or one attempt without retry. Evaluations compare variants; the loop version
changes apart from core.
