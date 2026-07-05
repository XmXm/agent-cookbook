---
name: skill-forge
description: "创建、起草、改进、评测、打包 Agent Skill 的中文优先 meta-skill。以 Anthropic 官方 skill-creator 为骨架（三级渐进式披露、两字段 frontmatter 硬约束、评测先行 eval-driven、description 触发优化、可选 .skill 打包），叠加三样官方没有的增量：中文优先撰写规约（英文更准处保留英文）、门·证·环·剃 deletion test 门槛、本仓 candidates→skills 晋级流。Use whenever the user wants 写个 skill、做个 skill、起草/新建 skill、改进或优化现有 skill、给 skill 写或调 description、跑 skill 评测、把 candidates 里的 skill 晋级进 skills、create a skill from scratch, author/improve/optimize a skill, tune a skill description for triggering, run skill evals。Not for 飞书 API 封装类 skill（走 lark-skill-maker）、skill 月度用量观测（走 skill-usage-report）、skill 合同校验（跑仓根 verify-skills.sh）。"
---

# Skill Forge：中文优先的 skill 创建工坊

以 Anthropic 官方 **skill-creator** 为骨架的 meta-skill。骨架、评测脚本、
description 优化环全部**复用官方**（不重造，见「剃」）；本 skill 的增量只有
三处官方给不了的东西：

1. **中文优先撰写规约** — SKILL.md 正文默认简体中文，术语/API 名/更精准处保留
   英文，绝不硬翻译（`references/zh-authoring.md`）。
2. **门·证·环·剃 deletion test 门槛** — 动笔前先过剃刀，挡住"不该存在的 skill"
   （`references/razor.md`）。
3. **本仓晋级流集成** — 新 skill 先落 `candidates/`，评测达标才晋级进
   `skills/` 并登记 RESOLVER、过 verify（`references/repo-integration.md`）。

> **定位**：这是 authoring（起草/改进）+ 集成入口，不是用量观测、不是合同校验。
> 官方 skill-creator 已装在本机（`~/.claude/plugins/.../skill-creator/`），
> 它的评测/优化/打包脚本能直接跑，本 skill 只在其上加中文皮肤与本仓纪律。

## 这个 skill 不做什么（邻居）

| 意图 | 去哪 |
|---|---|
| 把飞书 API 封装成 skill | `lark-skill-maker`（lark-cli 专用） |
| 看 skill 触发/渗透率、跑月度用量月报 | `skill-usage-report` |
| 校验 skill 合同（frontmatter、RESOLVER、链接、表格） | 仓根 `verify-skills.sh` |
| 纯官方流程、无需中文皮肤与本仓纪律 | 直接用官方 `skill-creator` 技能 |

## 先过剃刀（门槛，不可跳过）

动笔写任何新 skill 前，先答 `references/razor.md` 里的 **deletion test**：
删掉这个 skill 会让一个现代 agent「可度量地变差」吗？答不上来就别建。

- **该建**：有稳定重复流程、领域专有知识、确定性脚本能固化、或触发-约束能提质。
- **别建**：一次性任务、模型裸答已够好、只是把通用常识抄成文档、与现有 skill 重叠。
- Codex 2% 上下文预算检查：这个 skill 的元数据常驻系统提示，值这个位置吗？

过不了剃刀就停下，把结论告诉用户；别为了产出而产出。

## 骨架：完全复用官方 skill-creator

**目录解剖**（官方规范，唯一必需文件是 SKILL.md）：

```
skill-name/
├── SKILL.md         # 必需：YAML frontmatter（name+description）+ Markdown 正文
├── references/      # 按需加载进上下文的文档（Level 3）
├── scripts/         # 确定性可执行代码，经 bash 运行——代码本身不进上下文，只有输出耗 token
└── assets/          # 产出物用的文件（模板/图标/字体），不进推理
```

**三级渐进式披露**（核心设计原则，决定 token 预算）：

1. **Level 1 元数据**（name+description）— 常驻系统提示 ~100 token，**唯一触发杠杆**。
2. **Level 2 SKILL.md 正文** — 触发时加载，**<500 行为佳**；逼近就拆到 references/
   并留清晰指针。
3. **Level 3+ 资源** — 按需加载，实际无上限；脚本执行不把代码读进上下文。

**两字段 frontmatter 硬约束**速查见 `references/frontmatter-spec.md`。核心：`name`
≤64、小写字母/数字/连字符、禁 `anthropic`/`claude`、**必须等于目录名**；
`description` 非空 ≤1024、禁 XML 标签。

## 流程（六阶段，官方五阶段 + 本仓晋级）

判断用户在流程哪一步，跳进去接力，别每次从头。

### 1. 捕获意图（Capture Intent）

先从当前对话里榨取信息（"把这个流程做成 skill" → 提取用过的工具、步骤序列、
用户的纠正、输入输出格式），再补问缺口。四问定调：

1. 这个 skill 让 agent 能做什么？
2. **何时触发**？（用户会怎么说、什么上下文——决定 description）
3. 期望输出格式？
4. 要不要建 eval 测试用例？（可客观验证的输出值得建；主观输出如文风/审美不必强求）

### 2. 起草 SKILL.md（中文优先）

**先读 `references/zh-authoring.md`**，再动笔。要点：
- 正文简体中文，术语/命令/API/专有名保留英文，英文更精准处直接用英文，不硬翻。
- description 写成**第三人称 + what + when + 具体触发词**，且刻意"pushy"一点对抗
  欠触发——中英混排触发词都要覆盖（用户可能用中文也可能用英文说同一个意图）。
- 用 `assets/SKILL.template.md` 作为起草模板起手。
- imperative 祈使语气写指令；讲清**为什么**，少用全大写 MUST/ALWAYS 的硬约束。

### 3. 评测先行（eval-driven，复用官方脚本）

**在写大量文档前**先建 ≥3 个真实场景 + 无 skill 基线——这是官方最佳实践。
本 skill **不重造评测器**，直接跑官方 skill-creator 的脚本：

- 测试用例存 `evals/evals.json`（2-3 个真实 prompt）。
- with-skill 与 baseline(no-skill) 同一轮并行 spawn 子 agent。
- grader 子 agent 按官方 `skill-creator/agents/grader.md` 评分 → `scripts.aggregate_benchmark`
  聚合（mean±stddev + delta）→ `eval-viewer/generate_review.py` 出审阅 UI。

> 具体命令与 schema 直接看已装的官方 skill-creator 技能；本仓不复制这套脚本
> （复制 = 维护双份，违背剃）。若官方未装，`references/repo-integration.md`
> 有降级到纯人评的最小回路。

### 4. 迭代（Improve）

从少数样本**泛化**，别做 overfit 的 fiddly 修补；保持 prompt 精简，删不拉车的
内容；读 transcript 不只看最终输出——若多个测试用例都独立写了同一个 helper
脚本，那是"该把它 bundle 进 `scripts/`"的强信号。改完重跑测试，直到用户满意或
反馈全空或不再有实质进展。

### 5. description 触发优化（可选，复用官方 run_loop）

skill 定稿后，提议优化 description 触发准确率。生成 ~20 条 should-trigger /
should-not-trigger 查询（8-10 正 + 8-10 负，负例要"近似难辨"不要显然无关），
跑官方 `scripts.run_loop`（默认最多 5 轮，按 held-out 测试分选最优防过拟合），
把 `best_description` 回填 frontmatter，给用户看 before/after。

> **中文触发的额外注意**：跨语言匹配（中文 query 命中英文 description）机制未文档化，
> 不可靠。所以触发词**中英都要显式写进 description**，eval 查询也要中英混采。

### 6. 晋级 / 打包（本仓集成，官方没有）

新 skill 起草期一律在 `candidates/`，**不进 `skills/`**（不激活、不进 RESOLVER、
不受 verify 约束）。评测达标、用户点头后，按 `references/repo-integration.md`
晋级：移入 `skills/`、登记 `RESOLVER.md`、跑仓根 `verify-skills.sh` 到绿、
按需建符号链接。要跨机分发再用官方 `scripts.package_skill` 打成 `.skill`。

## 约束

- **剃刀前置且强制**。过不了 deletion test 就不建，把理由讲给用户，不为产出而产出。
- **骨架不魔改、脚本不重造**。骨架、评测器、优化环全用官方；本 skill 只加中文皮肤、
  剃刀、晋级流三样。想在 SKILL.md 里手写一套 eval 脚本时——停，那是官方已有的。
- **中文优先 ≠ 硬翻译**。英文更准处保留英文是纪律不是妥协；判据见 zh-authoring.md。
- **先手动后自动**（lazy 阶梯）：description 优化、打包这些自动环节，先手跑验证
  价值，再考虑固化。
- **不越界**：本 skill 不做用量观测、不做合同校验，各有其门（见邻居表）。

## 边界

- skill 合同校验（frontmatter/RESOLVER/链接/表格）走仓根 `verify-skills.sh`，
  不归本 skill；本 skill 只在晋级时**调用**它，不替代它。
- skill 月度用量与前门渗透率观测走 `skill-usage-report`，不归本 skill。
- 飞书 API 封装类 skill 走 `lark-skill-maker`（它懂 lark-cli 的原子/编排范式），
  不归本 skill。

## 参考文件

- `references/zh-authoring.md` — 中文优先撰写规约（何时中、何时留英、混排范式、
  description 中英触发词覆盖）。**起草前必读**。
- `references/razor.md` — 门·证·环·剃 deletion test 门槛（**注明：这是本仓方法论，
  非 Anthropic 官方规范**）。**动笔前必读**。
- `references/frontmatter-spec.md` — 两字段 frontmatter 硬约束 + 命名规则速查。
- `references/repo-integration.md` — candidates→skills 晋级流、RESOLVER 登记、
  verify 联动、符号链接约定、官方脚本定位与纯人评降级回路。
