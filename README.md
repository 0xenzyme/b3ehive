# b3ehive

[![Codex Skill](https://img.shields.io/badge/Codex-Skill-blue)](https://github.com/openai/codex)
[![Claude Code Skill](https://img.shields.io/badge/Claude%20Code-Skill-orange)](https://docs.anthropic.com/en/docs/claude-code)
[![opencode Skill](https://img.shields.io/badge/opencode-Skill-green)](https://opencode.ai)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://openclaw.ai)
[![Hermes Skill](https://img.shields.io/badge/Hermes-Skill-purple)](https://hermes-agent.nousresearch.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **"Fake it until make it"** — The Feynman Way

## The B3ehive Philosophy

I learned from one of the greatest physicists, **Richard Feynman**, whose nature was cheerful and whose intellect moved easily between worlds. He left behind the renowned **Feynman Technique**: learn by teaching, and prove understanding by making the thing clear enough to survive contact with another mind.

That is the seed of **b3ehive**. Let agents take a problem, give it a shape, divide the work, test the result, and keep moving until the work is real. Sometimes the hive debates. Sometimes it researches quietly. Sometimes it executes a blueprint, refines an architecture, migrates one contract into another, or runs a resource-aware feedback loop around a measurable bridge metric.

The best result is still, fundamentally, **a teacher for humanity**: not because it speaks well, but because it leaves a path another person can inspect, repeat, and improve.

### Why Swarms?

One agent is a voice. A swarm is an arrangement.

Different work needs different arrangements. A hard decision may need **debate**. A long implementation needs **execution** with checkpoints. An unknown codebase needs **research**. A mature system needs **optimization**. A useful body of work trapped in the wrong language, runtime, or toolchain needs **migration**. A repeated validation or product bridge needs a **looper** with explicit resources, reward signals, ROI accounting, and no-reward pause rules.

**b3ehive** is not just code generation. It is collective work shaped like the scientific method: observe the ground, choose the right organization, run bounded cycles, validate honestly, and leave evidence.

---

## Dual-Cursor Checklist Protocol

The execution, research, and migration skills use one shared progress grammar.
The checkbox mark is the cursor state:

- `[ ]` means not done, not researched, or not migrated. The item is still
  claimable by a worker.
- `[_]` means worker self-tested. A worker produced output and evidence, but
  master integration or curation has not accepted it.
- `[x]` means master accepted. The master lane validated, integrated,
  reconciled, and closed the item.

Workers may only move `[ ] -> [_]`. The master lane is the only actor that may
move `[_] -> [x]`. Cleanup requires zero `[ ]` and zero `[_]` items. Todos,
ledgers, progress summaries, and status commands must preserve these exact
marks; extra queue labels can add detail, but they do not replace the checkbox
state.

---

## Three Introductions

| English | 中文 | 日本語 |
|---|---|---|
| **b3ehive** is a collection of six swarm algorithms for agent work. Each skill has a narrow job, a hard boundary, and a cleanup rule. The point is not to sound smart. The point is to finish with traces you can inspect. | **b3ehive** 是一组面向 agent 工作的六个蜂群算法。每个 skill 都有明确职责、边界和收尾规则。目标不是说得漂亮，而是把事情做完，并留下能检查的证据。 | **b3ehive** は、agent 作業のための六つの swarm algorithm です。それぞれの skill は役割、境界、終了条件を持ちます。賢そうに見せるためではなく、検証できる形で仕事を終えるための道具です。 |

---

## The Six Hive Skills

| Skill | English | 中文 | 日本語 |
|---|---|---|---|
| `debating-cron-builder` | Three agents build, criticize, revise, vote, and produce the final repair path. Best when the answer needs pressure from more than one mind. | 三个 agent 并行产出、互相批评、更新、投票，再给出最终修复路径。适合需要多角度压测的任务。 | 三つの agent が並行して作り、批評し、直し、投票し、最後の修復方針を出します。複数視点で詰めたい仕事に向きます。 |
| `execution-cron-builder` | Turns one blueprint into a bounded execution cron: daily todo, isolated clone, validation gate, checkpoint, cleanup. It ships code only when the gate is real. | 把一个 blueprint 变成持续执行的 cron：每日 todo、隔离 clone、验证门、checkpoint、完成后清理。只有真实通过 gate 才算完成。 | 一つの blueprint を実行 cron に変えます。daily todo、隔離 clone、validation gate、checkpoint、cleanup まで持ちます。gate を通った実装だけを完了扱いにします。 |
| `research-cron-builder` | Walks a codebase, writes research notes, tracks progress, runs workers, rotates keys, and stops itself when the map is complete. | 持续扫描代码库，写 research 文档，追踪进度，并行跑 worker，轮换 key，完成后自动停掉。 | コードベースを読み、research docs を書き、進捗を追い、worker と key rotation を管理し、完了したら自分で止まります。 |
| `optimization-cron-builder` | Starts from a design idea, derives a bounded AR blueprint, researches each item, and pushes the repo toward clearer architecture. | 从设计理念出发，生成有边界的 AR blueprint，逐项研究，把仓库推向更清晰的架构。 | design philosophy から bounded AR blueprint を作り、項目ごとに調査し、repo をより明快な architecture へ寄せます。 |
| `migration-cron-builder` | Converts one artifact contract into another: tool assets, docs language, programming language, API shape, schema, or runtime layout. Claude to Codex is just one preset. | 把一种 artifact contract 迁移成另一种：工具资产、文档语言、程序语言、API 形态、schema、runtime 布局都可以。Claude 到 Codex 只是一个 preset。 | 一つの artifact contract を別の contract へ移します。tool assets、docs language、programming language、API shape、schema、runtime layout に使えます。Claude to Codex は preset の一つです。 |
| `looper-cron-builder` | Builds resource-aware loop daemons around DAG nodes or bridge metrics, with leases, rewards, ROI, no-reward pause, and re-funded resume. | 围绕 DAG 节点或 bridge 指标构建资源感知 loop daemon，包含 lease、reward、ROI、无奖励暂停和再注资恢复。 | DAG node または bridge metric の周りに、lease、reward、ROI、no-reward pause、re-funded resume を持つ resource-aware loop daemon を作ります。 |

---

## Install

Clone the whole hive:

```bash
git clone https://github.com/weiyangzen/b3ehive.git
```

Install all six skills for Codex, Claude Code, opencode, OpenClaw, and Hermes:

```bash
cd b3ehive
scripts/install_skills.sh --target all --scope user
```

Install only one target when needed:

```bash
scripts/install_skills.sh --target codex --scope user
scripts/install_skills.sh --target claude --scope user
scripts/install_skills.sh --target opencode --scope user
scripts/install_skills.sh --target openclaw --scope user
scripts/install_skills.sh --target hermes --scope user
```

Project-local installs are also supported:

```bash
scripts/install_skills.sh --target all --scope project --project-dir /path/to/repo
```

The portable skill layout is documented in
[docs/agent-platforms.md](docs/agent-platforms.md). Codex uses
`~/.codex/skills/<skill>/SKILL.md`; Claude Code uses
`~/.claude/skills/<skill>/SKILL.md`; opencode uses
`~/.config/opencode/skills/<skill>/SKILL.md`; OpenClaw uses
`~/.openclaw/skills/<skill>/SKILL.md`; Hermes uses
`~/.hermes/skills/<skill>/SKILL.md`.

## Quick Start

Run the original debating flow in dry-run mode:

```bash
python3 debating-cron-builder/scripts/debating_cron_builder.py \
  --task "Implement a thread-safe rate limiter" \
  --output ./debating-runs/rate-limiter \
  --runner mock
```

For a repository-local cron, call the matching skill by name:

```text
Use execution-cron-builder for this repo and this blueprint.
Use research-cron-builder to research this codebase.
Use optimization-cron-builder with this design philosophy.
Use migration-cron-builder to migrate one artifact contract into another.
Use looper-cron-builder to add resource-aware loop daemons around these bridge metrics.
```

In Claude Code you can also invoke a skill with slash syntax, for example
`/execution-cron-builder`.

opencode discovers the same `SKILL.md` directories from `.opencode/skills/`,
`~/.config/opencode/skills/`, `.claude/skills/`, and `~/.claude/skills/`.
OpenClaw and Hermes also use `SKILL.md`; for repository/tap installs they both
accept `skills/<skill>/SKILL.md`.

## What Makes b3ehive Different

| Traditional AI | b3ehive |
|---|---|
| One assistant, one shape | **Six swarm organizations** |
| Prompt in, answer out | **Checklist, worker, validator, cleanup** |
| Hidden state | **Inspectable specs, todos, logs, and artifacts** |
| "Looks done" | **Pass the gate, then checkpoint** |

## Repository Map

- [debating-cron-builder](debating-cron-builder/SKILL.md) — three-agent debate and selection
- [execution-cron-builder](execution-cron-builder/SKILL.md) — blueprint-driven implementation cron
- [research-cron-builder](research-cron-builder/SKILL.md) — code research cron
- [optimization-cron-builder](optimization-cron-builder/SKILL.md) — design-guided optimization cron
- [migration-cron-builder](migration-cron-builder/SKILL.md) — generalized source-to-target migration cron
- [looper-cron-builder](looper-cron-builder/SKILL.md) — resource-aware loop daemon cron
- [SKILL.md](SKILL.md) — original PCTF debating specification
- [docs/agent-platforms.md](docs/agent-platforms.md) — Codex / Claude Code / opencode / OpenClaw / Hermes compatibility contract
- [config.yaml](config.yaml) — root configuration

## The Name

**b3** = Blueprint, Batch, Behavior  
**hive** = Swarm intelligence

> **Choose the right swarm, run bounded work, and leave proof.**  
> So called b3ehive.

## License

MIT © Weiyang ([@weiyangzen](https://github.com/weiyangzen))

---

*"What I cannot create, I do not understand."* — Richard Feynman
