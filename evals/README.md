# Evaluations

`scenarios.json` holds fifteen behavior scenarios, three per skill. Each names a
prompt, a fixture, and the observable results a passing run produces.

Run a scenario by loading the skill under test in a fresh agent session, placing
the fixture in a scratch repository, sending the prompt, and checking each
`expect` line against the artifacts. Score pass rate, false-accept rate (an
`[x]` the oracle would reject), loaded tokens, and wall-clock time.

Ablation crosses the switches under `ablation`. A mechanism stays only when it
raises pass rate or lowers false accepts at acceptable cost. Record results in
the skill's `references/lessons.md`, then freeze the winning configuration.
