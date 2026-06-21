# b3ehive 文档

[English](README.md)

`docs/` 目录使用成对 Markdown 文件维护多语言文档：

- `*.md` 是默认英文 canonical 页面。
- `*.zh-CN.md` 是简体中文页面。
- 每组文件顶部互相链接。
- 技术名词保留英文原文，例如 `blueprint`、`DAG`、`skill`、`worker`、
  `master lane`、`validation gate`、`LooperLog` 和命令名。

## 文档列表

| English | 中文 |
|---|---|
| [Core Concepts](concepts.md) | [核心概念](concepts.zh-CN.md) |
| [Blueprint](blueprint.md) | [Blueprint 蓝图](blueprint.zh-CN.md) |
| [Codex Plugin](codex-plugin.md) | [Codex Plugin](codex-plugin.zh-CN.md) |
| [Agent Platform Compatibility](agent-platforms.md) | [Agent 平台兼容性](agent-platforms.zh-CN.md) |

## 维护规则

- 面向用户的新增文档默认成对添加。
- 链接尽量指向同语言页面。
- 如果某个主题临时只有一种语言，release 前补齐配对文件。
- 不在同一个文档正文里混排完整中英双语；通过语言链接切换。
