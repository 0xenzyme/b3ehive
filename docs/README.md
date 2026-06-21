# b3ehive Docs

[中文](README.zh-CN.md)

This directory uses paired Markdown files for multilingual documentation:

- `*.md` is the default English canonical page.
- `*.zh-CN.md` is the Simplified Chinese page.
- Each pair links to the other at the top.
- Keep technical names in English: `blueprint`, `DAG`, `skill`, `worker`,
  `master lane`, `validation gate`, `LooperLog`, and command names.

## Documents

| English | 中文 |
|---|---|
| [Core Concepts](concepts.md) | [核心概念](concepts.zh-CN.md) |
| [Blueprint](blueprint.md) | [Blueprint 蓝图](blueprint.zh-CN.md) |
| [Codex Plugin](codex-plugin.md) | [Codex Plugin](codex-plugin.zh-CN.md) |
| [Agent Platform Compatibility](agent-platforms.md) | [Agent 平台兼容性](agent-platforms.zh-CN.md) |

## Maintenance Rules

- Add new docs as language pairs when the topic is public-facing.
- Link to the same-language page when possible.
- If only one language exists temporarily, add the paired file before release.
- Do not mix full English and Chinese bodies in one document; use language
  links instead.
