# b3ehive 核心概念

> 本文档整理自社区讨论，用于帮助新用户快速理解 b3ehive 的设计哲学和关键抽象。

---

## 一、项目理念：为什么是蜂群？

### 1.1 费曼技巧的启发

b3ehive 的灵感来自物理学家理查德·费曼的**费曼技巧**（Feynman Technique）：

> **"What I cannot create, I do not understand."**
>
> 如果你不能用简单的语言把它教给别人，说明你还没有真正理解它。

b3ehive 把这个思想搬到了 AI Agent 的工作中：让 Agent 把问题拆分、执行、验证，留下一条**可检查、可重复、可改进**的路径。最终产出的不只是代码，更是一份"教给人类"的完整证据链。

### 1.2 一个 Agent 是声音，一群 Agent 是编排

| 传统 AI 助手 | b3ehive |
|---|---|
| 一个助手，一种形态 | **五种蜂群组织形态** |
| Prompt In → Answer Out | **Checklist → Worker → Validator → Cleanup** |
| 隐藏状态 | **可检查的 Spec、Todo、Log、Artifact** |
| "看起来完成了" | **通过验证门，才能 Checkpoint** |

不同的工作，需要不同的组织方式：

- **难以决策** → 需要**辩论**（debating）
- **长期实现** → 需要**执行**（execution）
- **未知代码库** → 需要**研究**（research）
- **成熟系统** → 需要**优化**（optimization）
- **跨语言/跨工具迁移** → 需要**迁移**（migration）

b3ehive 不是代码生成器，而是**按科学方法组织的集体工作**：观察地面 → 选择组织形态 → 运行有边界的循环 → 诚实验证 → 留下证据。

---

## 二、Blueprint（蓝图）

### 2.1 Blueprint 是什么

在 b3ehive 中，**Blueprint 是唯一权威的需求源**。它是整个蜂群工作流的"心脏"和"燃料"。

核心特征：

| 特征 | 说明 |
|---|---|
| **唯一性** | 每个 Skill 有且只有一个 blueprint 文件，禁止多个需求来源互相冲突 |
| **自带 Checklist** | Blueprint 内包含 `- [ ]` / `- [x]` 标记的执行清单，本身就是进度表 |
| **自带依赖 DAG** | Checklist 项之间可以定义依赖关系，生成每日 todo 时变成拓扑排序的 DAG |
| **动态更新** | 每完成一批工作，guard 会把 `[ ]` 改为 `[x]` 写回 blueprint，它是活的 |
| **分层结构** | 可定义"层"（layer），强制执行"底层未完成前上层不能关闭" |

### 2.2 Blueprint vs. 传统 Spec

| 传统 Spec | b3ehive Blueprint |
|---|---|
| 静态文档，写给人看 | 动态文档，给机器执行 |
| 需求描述 + 验收标准 | 需求描述 + **执行清单** + **实时进度** + **依赖关系** |
| 开发完成后归档 | 开发过程中不断被修改（打勾、拆分、更新） |
| 可能有多个子文档 | **有且只有一个权威源** |
| 完成状态在 Jira/Trello 里 | 完成状态就在 blueprint 文件本身里 |

> **Blueprint = Spec（需求规格）+ Task Board（任务板）+ State Store（状态存储），三合一。**

### 2.3 不同 Skill 中的 Blueprint 形态

| Skill | Blueprint 的具体形态 |
|---|---|
| `execution-cron-builder` | 一个 Markdown 文件，里面有散文式需求描述 + checklist 段落。cron 按 checklist 逐项实现代码。 |
| `research-cron-builder` | 生成的 `blueprint_checklist.md`，从仓库树扫描而来，每个源码文件对应一个研究任务。 |
| `optimization-cron-builder` | `Stage_*_AR_Blueprint.md`，从设计理念推导出的架构优化清单，每项对应一篇研究文档。 |
| `debating-cron-builder` | **没有 blueprint**。输入是 `task_description` + `constraints`，3 个 agent 直接竞争实现。 |
| `migration-cron-builder` | 核心文档是 `MIGRATION_SPEC.md`，属于 blueprint 的"迁移泛化"：用 source→target contract 替代 blueprint。 |

### 2.4 Blueprint 的生命周期

```
Bootstrap:   初始化 checklist，所有项标记为 [ ]
    ↓
Daily Todo:  从 blueprint 的未完成项生成当日 todo（含 DAG 依赖）
    ↓
Worker 执行: 按 DAG 顺序 claim 任务，产出代码/文档
    ↓
Validation:  运行验证门（编译、测试、lint 等）
    ↓
Checkpoint:  通过后，将 [ ] 改为 [x]，写回 blueprint
    ↓
Cleanup:     当 blueprint 中所有项都变为 [x]，cron 自动停止并清理自身
```

---

## 三、五大 Skill 速查

| Skill | 核心能力 | 输入 | 输出 |
|---|---|---|---|
| `debating-cron-builder` | 多 Agent 辩论选优 | 一个任务描述 | 最优实现 + 对比报告 + 决策理由 |
| `execution-cron-builder` | 按蓝图持续执行代码 | 一个 Blueprint | 逐项实现的代码 + checkpoint 提交 |
| `research-cron-builder` | 代码库研究 | 一个代码仓库 | 每份源码对应的研究文档 |
| `optimization-cron-builder` | 架构优化研究 | 设计理念 + 阶段蓝图 | 每项优化的研究文档 |
| `migration-cron-builder` | 产物契约迁移 | Source Contract + Target Contract | 迁移后的目标产物 |

---

## 四、命名由来

- **b3** = **B**lueprint, **B**atch, **B**ehavior
- **hive** = Swarm intelligence（蜂群智能）

> Choose the right swarm, run bounded work, and leave proof.
> So called b3ehive.
