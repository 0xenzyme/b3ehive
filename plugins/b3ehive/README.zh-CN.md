# b3ehive Codex Plugin

[English](README.md)

b3ehive 是一个面向 Codex 的 plugin，用来组织有边界的 multi-agent 工作。它打包了五个 skill，分别覆盖方案竞争、blueprint 执行、source 学习、架构优化，以及带资源和反馈控制的 loop。

这个 plugin 不提供 MCP server、app 或 hook。它的能力来自 `skills/` 目录下的五个 `SKILL.md`。

## Skills

- `compete-cron-builder`
- `execution-cron-builder`
- `learn-cron-builder`
- `optimization-cron-builder`
- `looper-cron-builder`

## 如何选择 Skill

| 需求 | 使用 | 产物 |
|---|---|---|
| 在真正执行前比较多条路线 | `compete-cron-builder` | candidate proposals、selected plan、coverage union、repair queue 或 execution handoff |
| 在仓库里执行一个已确认的 blueprint | `execution-cron-builder` | DAG checklist、daily todo、worker batches、validation gates、checkpoints、cleanup |
| 理解、转换或翻译一个 source scope | `learn-cron-builder` | source manifest、coverage contract、learning notes、transformed code 或 translated docs |
| 把设计理念转成架构优化工作 | `optimization-cron-builder` | `Stage_*_AR_Blueprint.md` 和逐项 optimization research docs |
| 给长期尝试加入反馈、资源、reward 和 ROI 控制 | `looper-cron-builder` | loop specs、resource leases、evidence ledgers、reward/ROI records、pause/resume control |

这五个 skill 不是固定流水线。应该从当前最大的不确定性出发选择：

- 路线不确定时，先用 `compete-cron-builder`。
- source 不清楚时，先用 `learn-cron-builder`。
- 架构方向明确但需要系统性 refinement 时，用 `optimization-cron-builder`。
- blueprint 已经确认时，用 `execution-cron-builder`。
- 需要反复尝试、指标反馈、预算控制或人工反馈时，把 `looper-cron-builder` 加在外层。

## Skill 作用和触发条件

### `compete-cron-builder`

当任务需要在多条路线、实现方式、audit 结果或 repair 策略之间做有边界竞争时使用。

适合触发的场景：

- 需要 `n` 个 workers、`m` 个 proposals、再 `choose k`。
- 需要 `run_a`、`run_b`、`run_c` 形式的 three-way challenge。
- 需要 best-one selection、top-k synthesis、coverage union、risk union 或 repair queue。
- 做新功能前，需要多个独立方案再合成 feature blueprint。
- 想把更稳的 plan handoff 给 `execution-cron-builder` 或 `looper-cron-builder`。

示例 prompt：

```text
Use compete-cron-builder to compare implementation routes for this feature and synthesize a blueprint.
Use compete-cron-builder with three proposals and choose the safest plan.
Use compete-cron-builder to run a coverage sweep for risks in this API.
```

边界：这个 skill 可以产出 proposals、findings、selected plans 和 handoff metadata，但不应该把 execution checklist item 标成 `[x]`。最终接受权属于 execution 或 looper 的 master lane。

### `execution-cron-builder`

当已经有一个 authoritative blueprint，目标是按它真实实现并验证时使用。

适合触发的场景：

- 需要为一个 blueprint 建 repo-local execution cron。
- 需要为 checklist items 建 dependency DAG。
- 需要 worker/master 双通道：worker 只能产出 `[_]`，master lane 才能接受 `[x]`。
- 需要 validation gates、checkpoint commits、cleanup-on-complete 和 bounded worker batches。
- 需要修复已有 blueprint-execution cron 的边界或 gate。

示例 prompt：

```text
Use execution-cron-builder for this repo and this confirmed blueprint.
Use execution-cron-builder to build a DAG todo and validation gate for this spec.
Use execution-cron-builder to repair the existing execution cron boundaries.
```

边界：这是根据已确认 blueprint 真正推进实现的主 skill。它应该先读取唯一 authoritative requirement source，再生成 todos 或 worker prompts。

### `learn-cron-builder`

当工作起点是理解、转换或翻译一个有边界的 source scope 时使用。

适合触发的场景：

- 需要 code-to-human learning notes。
- 需要严格的一对一 source file 和 source-tree coverage。
- 需要 explicit subset 或 fuzzy subset learning。
- 需要 code-to-code transformation、API/schema/runtime/tool conversion、SDK generation 或 adapter generation。
- 需要 human-language documentation translation。
- 需要 `source_manifest.tsv`、route policy、coverage contract 和 master-only acceptance。

示例 prompt：

```text
Use learn-cron-builder to understand this package into one-to-one learning notes.
Use learn-cron-builder in transform mode for this API schema migration.
Use learn-cron-builder to translate these docs with source coverage validation.
```

边界：这不是普通 feature implementation 的默认 skill。它主要产出经过验证的 learning、transform 或 translation artifacts。这些 artifacts 可以作为后续 blueprint 的输入，但不会自动等同于已接受的产品代码。

### `optimization-cron-builder`

当用户已经给出 design philosophy，并希望做结构化 architecture refinement，而不是直接写产品代码时使用。

适合触发的场景：

- 需要生成有边界的 `Stage_*_AR_Blueprint.md`。
- 需要不超过 100 个 architecture refinement checklist items。
- 需要在 `Docs/researches/Stage_*_AR/` 下生成逐项 research docs。
- 需要按 blueprint section 分配 parallel worker ownership。
- 需要把 repo-specific optimization plan 过滤到一个明确 design philosophy 之下。

示例 prompt：

```text
Use optimization-cron-builder with this design philosophy: reduce cognitive load and simplify extension points.
Use optimization-cron-builder to derive an AR blueprint for this stage.
Use optimization-cron-builder to research each architecture refinement item before implementation.
```

边界：这个 skill 默认不直接实现产品代码。它创建 optimization research 和 AR blueprint，之后可以交给 `execution-cron-builder` 执行。

### `looper-cron-builder`

当工作需要在明确资源、reward 和 side-effect 控制下反复尝试时使用。

适合触发的场景：

- 需要围绕 DAG nodes、bridge surfaces、bridge metrics、product validation goals、benchmark lanes 或 monitoring signals 做 bounded attempts。
- 需要 resource leases、budgets、compact evidence ledgers、reward signals、ROI tracking 和 no-reward pause rules。
- 需要为 risky writes、publishing、deletion、spend 或 external calls 建 side-effect gates。
- 需要 operator-controlled feedback loops，以及 paused loop 的 re-funded resume。
- 需要 nested b3ehive skill attempts，并保留 attribution 和 master acceptance。

示例 prompt：

```text
Use looper-cron-builder to control repeated validation attempts around this benchmark lane.
Use looper-cron-builder to add ROI tracking and no-reward pause rules to this workflow.
Use looper-cron-builder around these bridge surfaces and side-effect gates.
```

边界：looper 是 feedback overlay，不是 cyclic dependency graph。它应该把 loops 附着在 DAG nodes 或 bridge surfaces 旁边，最终完成仍由 master lane 在验证通过后接受。

## 常见工作流

### 新功能但路线不确定

```text
compete-cron-builder -> execution-cron-builder
```

先用 `compete-cron-builder` 生成并比较 proposals，再把选中的 blueprint 交给 `execution-cron-builder` 实现。

### 现有代码库还没理解清楚

```text
learn-cron-builder -> compete-cron-builder -> execution-cron-builder
```

先用 `learn-cron-builder` 固定 source coverage，产出 validated notes 或 transforms。只有在后续仍有多条实现路线时，才接 `compete-cron-builder`。

### 架构优化

```text
optimization-cron-builder -> execution-cron-builder
```

先用 `optimization-cron-builder` 生成 AR blueprint 和 research docs。只有当 AR blueprint 被接受为 authoritative implementation source 后，才交给 `execution-cron-builder`。

### 长期任务，有反馈或预算风险

```text
execution-cron-builder + looper-cron-builder
```

用 `execution-cron-builder` 管 DAG implementation path，用 `looper-cron-builder` 管 repeated attempts、metric movement、reward/ROI accounting、side-effect gates 和 pause/resume control。

## 共享概念

`DAG` 是 `Directed Acyclic Graph`，即有向无环图。在 b3ehive 中，它表示任务依赖顺序。下游任务不应该在上游依赖被接受前完成或被接受。

五个 skill 共享 dual-cursor checklist protocol：

- `[ ]` 表示未完成。
- `[_]` 表示 worker 已自测，等待 master acceptance。
- `[x]` 表示 master 验证后接受。

worker 只能把 `[ ]` 推进到 `[_]`。只有 master lane 可以把 `[_]` 推进到 `[x]`。

## 安装

从 repository root 安装：

```bash
codex plugin marketplace add .
codex plugin add b3ehive@b3ehive
```

从 GitHub 安装：

```bash
codex plugin marketplace add weiyangzen/b3ehive
codex plugin add b3ehive@b3ehive
```

安装后启动新的 Codex thread，让 Codex 加载 bundled skills。

## Source Of Truth

root skill directories 是 source of truth：

```text
compete-cron-builder/
execution-cron-builder/
learn-cron-builder/
optimization-cron-builder/
looper-cron-builder/
```

`plugins/b3ehive/skills/` 是 packaged copy。发布前，从 repository root 运行同步命令：

```bash
scripts/sync_codex_plugin.sh
```

完整安装、维护、验证和 release contract 见 [docs/codex-plugin.zh-CN.md](../../docs/codex-plugin.zh-CN.md)。
