# RSI 样例提示词

[English](rsi-prompt.md)

这是一份 b3ehive 的 **RSI（recursive self-improvement，递归自我改进）样例提示词**。它同时跑两个循环：

- **对象循环**：在冻结的 oracle 下改进一个目标（仓库、kernel、研究结论）。
- **仪器循环**：改进"做改进的工具"本身，即 b3ehive 自己的 skill、校验器与脚本。每个被接受的仪器改动，都会让后续的对象循环做得更好。

这里的"递归"指工程循环（提出、测试、评审、留存）作用于它自身的机制，而不是宣称模型能自主变强：每个改动都由 master 接受，oracle 始终冻结，所有仪器改动都可回滚。

## 提示词

替换尖括号字段后，粘贴到装有 b3ehive 的 agent 会话中。

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

## 与 b3ehive 模块的对应

| 步骤 | 模块 |
|---|---|
| canon、经验 | learn `canon` 模式；`scripts/find_lesson.py` |
| blueprint、oracle 先行 | execution；core 第 2 律 |
| 多假设并行 | compete；loop 形状 `lanes`；方向与机制距离 |
| 测量与 ratchet | optimization `measured` 模式；`B3_STATS`；loop v2 ratchet |
| 独立评审 | loop 形状 `review`；compete 盲审 |
| 留存 | 经验库；master 验收 |
| 结果路由、重规划义务、暂停 | loop v2 结果词汇；looper 治理 |
| 仪器循环 | core 第 7 律；compete 影子模式；`evals/` 消融 |

## 变体

- **kernel 优化**：`<TARGET>` 是一个 kernel；canon 纳入硬件厂商的文档 MCP 与论文；仪器包括 `ncu`、`nsys`；oracle 合同按 `optimization-cron-builder/references/measured-mode.md`。
- **研究**：oracle 用 dev 集迭代、holdout 集验收；结论只有在独立评审批准同一个证据摘要后才算确认。
- **仓库维护**：execution 用 `persistent_pool`；事故写入经验库，每次修复前先检索。
