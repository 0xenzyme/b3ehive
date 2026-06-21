# b3ehive

[English](README.md)

[![Codex Skill](https://img.shields.io/badge/Codex-Skill-blue)](https://github.com/openai/codex)
[![Claude Code Skill](https://img.shields.io/badge/Claude%20Code-Skill-orange)](https://docs.anthropic.com/en/docs/claude-code)
[![opencode Skill](https://img.shields.io/badge/opencode-Skill-green)](https://opencode.ai)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://openclaw.ai)
[![Hermes Skill](https://img.shields.io/badge/Hermes-Skill-purple)](https://hermes-agent.nousresearch.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **"Fake it until make it"** — The Feynman Way

## b3ehive 是什么

b3ehive 是一组面向 agent 工作的五个 swarm algorithms。它不是单纯的代码生成提示词，而是把工作组织成可检查、可验证、可继续的流程：先观察真实上下文，选择合适组织形态，运行有边界的 worker 循环，通过 validation gate 后再 checkpoint。

## 五个 Skills

| Skill | 作用 |
|---|---|
| `compete-cron-builder` | 多方案竞争：`n` workers、`m` proposals、`choose k`、coverage union、repair queue、blueprint synthesis。 |
| `execution-cron-builder` | 把一个已确认 blueprint 变成可执行 cron：daily todo、DAG、worker/master 双通道、validation gate、checkpoint、cleanup。 |
| `learn-cron-builder` | 把 source scope 学成可验证 artifacts：code-to-human notes、subset learning、code-to-code transform、human-language translation。 |
| `optimization-cron-builder` | 根据 design philosophy 生成 `Stage_*_AR_Blueprint.md`，并为每个 architecture refinement item 产出 research doc。 |
| `looper-cron-builder` | 给长期或反复尝试加 resource-aware bridge controller：lease、side-effect gate、evidence、reward、ROI、pause/resume。 |

## Dual-Cursor Checklist Protocol

执行和学习类 workflows 使用同一个进度语法：

- `[ ]` 表示未完成，仍可被 worker claim。
- `[_]` 表示 worker 已自测，等待 master integration 或 curation。
- `[x]` 表示 master 已验证、集成并接受。

worker 只能把 `[ ]` 推进到 `[_]`。只有 master lane 可以把 `[_]` 推进到 `[x]`。cleanup 要求没有 `[ ]` 和 `[_]`。

## 安装

Clone 仓库：

```bash
git clone https://github.com/weiyangzen/b3ehive.git
```

### Codex Plugin

b3ehive 作为 Codex plugin package 位于 [`plugins/b3ehive`](plugins/b3ehive/README.zh-CN.md)。仓库也提供 marketplace catalog： [`.agents/plugins/marketplace.json`](.agents/plugins/marketplace.json)。

从当前 checkout 安装：

```bash
codex plugin marketplace add .
codex plugin add b3ehive@b3ehive
```

从 GitHub 安装：

```bash
codex plugin marketplace add weiyangzen/b3ehive
codex plugin add b3ehive@b3ehive
```

安装后启动新的 Codex thread，让五个 bundled skills 被加载。

### Portable Skill Install

为 Codex、Claude Code、opencode、OpenClaw 和 Hermes 安装全部五个 skills：

```bash
cd b3ehive
scripts/install_skills.sh --target all --scope user
```

只安装某个平台：

```bash
scripts/install_skills.sh --target codex --scope user
scripts/install_skills.sh --target claude --scope user
scripts/install_skills.sh --target opencode --scope user
scripts/install_skills.sh --target openclaw --scope user
scripts/install_skills.sh --target hermes --scope user
```

## 快速使用

```text
Use compete-cron-builder to compare local proposals, synthesize a blueprint, or run coverage union.
Use execution-cron-builder for this repo and this blueprint.
Use learn-cron-builder to learn a codebase, transform source artifacts, or translate docs.
Use optimization-cron-builder with this design philosophy.
Use looper-cron-builder to add resource-aware bridge controllers around these bridge surfaces and metrics.
```

## 文档

- [docs/README.zh-CN.md](docs/README.zh-CN.md) — 文档索引和多语言规则
- [docs/concepts.zh-CN.md](docs/concepts.zh-CN.md) — 核心概念
- [docs/blueprint.zh-CN.md](docs/blueprint.zh-CN.md) — Blueprint 详解
- [docs/codex-plugin.zh-CN.md](docs/codex-plugin.zh-CN.md) — Codex plugin 安装、使用和发布
- [docs/agent-platforms.zh-CN.md](docs/agent-platforms.zh-CN.md) — Codex / Claude Code / opencode / OpenClaw / Hermes 兼容性

## Repository Map

- [compete-cron-builder](compete-cron-builder/SKILL.md)
- [execution-cron-builder](execution-cron-builder/SKILL.md)
- [learn-cron-builder](learn-cron-builder/SKILL.md)
- [optimization-cron-builder](optimization-cron-builder/SKILL.md)
- [looper-cron-builder](looper-cron-builder/SKILL.md)
- [plugins/b3ehive](plugins/b3ehive/README.zh-CN.md)
- [SKILL.md](SKILL.md)

## License

MIT © Weiyang ([@weiyangzen](https://github.com/weiyangzen))
