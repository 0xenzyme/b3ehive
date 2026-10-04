# b3ehive Codex Plugin

[English](README.md)

五个蜂群 skill，共守一律（`core.md`），共用一环（`loop.md`）。

| Skill | 用于 |
|---|---|
| `compete-cron-builder` | 难抉择、修复搜索、审计、覆盖；oracle 优先择选 |
| `execution-cron-builder` | 一份 blueprint 化 DAG；worker 隔离；master 验收 |
| `learn-cron-builder` | 理解、转换、翻译、建 canon |
| `optimization-cron-builder` | 测量式性能循环或设计研究 |
| `looper-cron-builder` | 共享 loop 与预算治理 |

```bash
codex plugin marketplace add weiyangzen/b3ehive
codex plugin add b3ehive@b3ehive
```

安装后新开 Codex 线程。`skills/` 下为生成副本；改根目录 skill 后运行 `scripts/sync_codex_plugin.sh`。完整说明见仓库 [README](../../README.zh-CN.md)。
