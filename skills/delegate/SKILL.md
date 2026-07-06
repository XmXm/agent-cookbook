---
name: delegate
description: >-
  多 coding agent 委派门：Claude 只做方案、路由与验收，编码实施委派给外部
  coding agent（Codex 主力 / kimi 最快 / pi 按模型分档 / copilot 特批档）。
  内置 ROI 门（复杂度 × token 成本 × 时间成本）决定自己做还是委派、派给谁、
  是否拆分并发多实例。仅当用户显式调用 /delegate 时使用；绝不主动触发，
  绝不因为"任务看起来像开发任务"而自动进入此模式。
  Multi-agent delegation: Claude plans, routes and accepts; external agents
  implement. User-invoked only, never trigger proactively.
argument-hint: "<要实现的任务描述> [直接干 = 跳过方案确认]"
disable-model-invocation: true
---

# Delegate: Claude 方案路由 + 外部 agent 编码 + Claude 验收

省 token 的分工契约：「思考密集」留给 Claude（方案、路由、验收判断），「产码密集」
交给外部 coding agent（写代码、跑自验）。本 skill 生命周期内 **Claude 不写实现
代码**——Claude 一动手写码就等于没省钱。唯一例外见 Phase 3 的验收手改 ROI 条款。

## 流程总览

```text
用户 /delegate <任务>
  → Phase 0 ROI 门（劝退 / 单派 / 拆分并发）+ 路由（能力矩阵选 agent）
  → Phase 1 方案（Claude，plan 门标准；并发时按子任务拆分）
  → 用户确认方案（调用时已说"直接干"则跳过）
  → Phase 2 派发（单实例或并发多实例；codex 走 Agent 工具，其余走 CLI）
  → Phase 3 验收（Claude 本会话实证核对；并发时逐子任务 + 整体集成）
      ├─ PASS → 收尾
      └─ FAIL → delta 回派同 session（≤2 轮）→ 升梯队重派（限 1 次）→ 交用户
```

## Phase 0 — ROI 门与路由

委派有固定往返成本：组 prompt、agent 拉起与自验、Claude 验收，单轮往返分钟级。
ROI 按三要素判断：

- **复杂度**：改动面（文件数/行数）、设计决策是否已定死、是否需要强推理。
- **token 成本**：Claude 自写全部实现要产出的 tokens，对比方案+验收 tokens——
  差值才是委派省下的钱；差值小于往返开销就不值得派。
- **时间成本**：串行单任务时 Claude 自己做往往更快；子任务可并行时委派赢——
  多实例同时跑，墙上时间取最慢者而非求和。

判定输出三选一：

1. **劝退**：琐碎任务（约 20 行以内、单文件、意图无歧义、typo/纯配置）——
   提醒用户往返开销高于收益，问是否仍派。用户坚持则照走，选免费或最快档。
2. **单派**：一个 agent 一次派发，按下方路由表选。
3. **拆分并发**：任务能拆成 ≥2 个**文件集不相交**的独立子任务时，逐个子任务
   路由（可同 agent 多实例，也可多 agent 混编），并发派发。

## 能力矩阵

评级维度：质量、速度、成本。评级是初始估计，**用验收结果校准**——某 agent 在
某类任务上连续返工就降档，证据在收尾时写回 nmem，并更新本表。新增 agent =
本表加一行 + Phase 2 补一条派发契约。

| Agent | 调用方式 | 质量 | 速度 | 成本 | 定位 |
|---|---|---|---|---|---|
| codex | Agent 工具 → `codex:codex-rescue` | ★★★★★ | ★★★ | 订阅 | 主力：复杂实现、跨文件重构、需强推理 |
| kimi | `kimi -p "<prompt>"` | ★★★★ | ★★★★★ | 订阅 | 二梯队首选：中等复杂度、要快 |
| pi · glm-5.2 | `pi --model litellm/glm-5.2 -p` | ★★★★ | ★★★ | 中低 | 准一梯队替补：省 codex 额度 |
| pi · deepseek-v4-pro | `pi --model deepseek/deepseek-v4-pro -p` | ★★★ | ★★★★ | 低 | 小而明确的任务 |
| pi · MiniMax-M3 | `pi --model minimax-cn/MiniMax-M3 -p` | ★★ | ★★★ | 免费 | 琐碎/批量/试探，失败零成本 |
| copilot · fable-5 | `copilot --model claude-fable-5 -p` | ★★★★★ | ★★ | 额度紧 | 特批档，见下方红线 |

**copilot 红线**：订阅额度有限，默认永不路由到 copilot。仅当 (a) 用户点名要用，
或 (b) codex 不可用且任务确需一梯队质量时，**先询问用户同意**再派。

路由表（复杂度 → 默认 agent）：

| 任务画像 | 派给 |
|---|---|
| 复杂、大改动、设计敏感、需强推理 | codex |
| 中等复杂度、要快 | kimi |
| 中等复杂度、不急、想省 codex 额度 | pi · glm-5.2 |
| 小而明确 | pi · deepseek-v4-pro（要快则 kimi） |
| 琐碎但用户坚持委派、大批量同构任务 | pi · MiniMax-M3 |
| 需一梯队质量但 codex 不可用 | 询问用户 → copilot · fable-5 |

可用性替补：所选 agent 缺失或未认证时（codex → `/codex:setup`；kimi →
`kimi login`；pi → 对应 provider API key；copilot → `copilot login`），报告
并按矩阵选同档或降半档替补（copilot 仍需询问）；全部不可用则**停**——不降级为
Claude 自己实施，也不伪造结果。

## Phase 1 — 方案（Claude）

按 plan 门（`skills/plan/SKILL.md`）的 decision-complete 标准出方案，目标是
agent 拿到后**不需要再做任何设计决策**。小任务（对应 plan 门 Lightweight 画像：
问题已定义、只剩"怎么改"）压缩成**目标 + 选定做法 + 验收标准**三段即可，
其余小节一句话带过或写"无"；中大型任务五小节全开：

- **目标**：一句话说清改什么、为什么。
- **改动清单**：预期要动的文件/模块，以及明确 out-of-scope 的部分。
- **方案与取舍**：选定做法 + 一句话说明为何不选替代方案。所有设计决策在此定死。
- **兼容边界**：列出本次必须保留的真实契约（public API、持久化数据、对外协议、
  用户明确要求的兼容项）；没有就写"无"。未列入的老代码一律视为可直接修改、可删除
  ——内部调用方、旧命名、现有代码形状、"diff 会大"不构成兼容理由。这一条是
  Phase 2 重构策略块的直接输入，缺了它 agent 会自己脑补兼容需求。
- **验收标准**：3-7 条可客观验证的条目（命令、行为、输出），Phase 3 逐条核对用。
  写不出可验证的验收标准 = 方案还没想清楚，回炉。
- **持久化判据只看改动本身，不看委派流程**：Phase 0-3 的派发/验收往返不算
  "多阶段"，agent 在外部执行不算"跨会话"——方案经 Phase 2 的 prompt 骨架
  传递、验收在本会话完成，`.plans/` 在这条链路里不承担任何交接职能。仅当
  改动本身满足 plan 门持久化判据（改动多阶段、3+ 实施步骤、执行真正跨
  Claude 会话）或用户点名要文档时才写 `.plans/`；单派的中小任务方案留在
  对话里直接派发。

**并发拆分附加要求**——每个子任务单独具备：

- **文件集**：互不相交是硬性前提；文件集相交的子任务必须合并成一个派发或串行。
- **独立验收标准**：不依赖其他子任务完成即可核对。
- **接口约定**：子任务之间若有调用/数据契约，在方案里定死签名，双方照抄。

方案呈给用户确认后再派发；用户调用时已说"直接干/不用确认"则跳过确认。

## Phase 2 — 派发

### Prompt 骨架（所有 agent 共用）

六个块缺一不可。codex 按 gpt-5-4-prompting 契约用 XML 标签组装；CLI agent
用相同内容的 markdown 小节：

```text
<task>
[目标 + 必要的仓库上下文 + 改动文件清单 + 已定死的设计决策]
</task>
<completeness_contract>
完成定义 = 以下验收标准全部满足：[逐条列出本子任务的验收标准]
</completeness_contract>
<verification_loop>
返回前自行构建并运行相关验证；报告实际执行的验证命令与结果。
</verification_loop>
<action_safety>
只改 <task> 列出的范围；不做无关重构、不动无关文件。
[并发时追加：以下文件属于其他并行任务，禁止触碰：<其他子任务的文件集>]
</action_safety>
<refactor_policy>
范围收窄不等于改法保守。范围内的老代码该改就直接改，该删就删除（不是注释掉、
不是标记 deprecated）。本次真实兼容约束仅限：[抄录方案的兼容边界；没有则写"无"]。
内部调用方、旧命名、现有代码形状、"改动会大"都不是保留老实现的理由。
禁止：新旧双路径并存；用转发/适配/包装层裹住老实现来回避修改它；只加不删；
方案未要求的防御性判空、try-catch、降级分支；"以防万一"的开关、配置项或保留字段。
</refactor_policy>
<compact_output_contract>
返回：改动文件清单、每条验收标准的自验结果、遗留风险。
</compact_output_contract>
```

`<refactor_policy>` 必填的原因：coding agent 的默认风格普遍偏保守——不敢动老
代码、层层加保护、过度兼容。`<action_safety>` 管"改哪里"（范围要窄），
`<refactor_policy>` 管"怎么改"（范围内要果断），两者不冲突。

### 各 agent 派发契约（已实测）

- **codex**：Agent 工具，`subagent_type: "codex:codex-rescue"`。小而有界前台等；
  长任务加 `--background`。不指定 `--model`/`--effort`，除非用户明确要求。
- **kimi**：`kimi -p "<prompt>"`。prompt 模式自动批准工具，**不能**加 `--yolo`
  （互斥报错）。输出末尾有 `To resume this session: kimi -r <session-id>`，
  捕获它供返工回派：`kimi -r <session-id> -p "<delta>"`。
- **pi**：`pi --session-id $(uuidgen) --model <provider/model> -p "<prompt>"`。
  派发前预分配 session id 并记下，返工用同一 `--session-id` 回派。
- **copilot**：`copilot --session-id $(uuidgen) --model claude-fable-5
  -p "<prompt>" --allow-all-tools -s`。非交互必须 `--allow-all-tools`；
  返工 `copilot --resume <session-id> -p "<delta>" --allow-all-tools -s`。

### 派发规则

- 一次派发只做一件事；不相关的诉求拆成多次派发。
- CLI agent 在仓库根目录起进程（cwd 决定它看到的项目）。
- 并发时每实例独立 `run_in_background` Bash 任务跑，结束后从输出提取改动摘要
  与 session id；codex 多实例 = 同一消息里多个并行 Agent 调用。
- 并发上限 3-4 实例，再多验收吞不下、机器也扛不住。
- agent 干活期间 Claude 不并行改同一批文件，也不预写"备用实现"。

## Phase 3 — 验收（Claude）

agent 返回后实证核对。结论必须来自本会话实跑的证据，agent 的自验报告只作参考，
不作为通过依据：

1. `git diff --stat` 核对改动范围 vs 方案改动清单——超范围改动一律列为问题。
2. 逐条核对验收标准：能实跑的命令在本会话跑一遍。
3. 读关键 diff：正确性、边界条件、与既有代码风格的一致性（MLBB C# 对照
   `cs-coding` 的规范）。
4. 保守味检查：有没有方案未要求的兼容层、新旧双路径、防御性保护、注释掉或
   deprecated 的死代码、"以防万一"的配置开关。有 → 一律列为 FAIL 项，返工
   delta 指令里明确指名"直接修改/删除 XXX，不要包一层"。

**并发场景加两步**：先逐子任务按各自验收标准核对，再做整体集成核对——全量
diff 里查子任务边界有没有互相踩踏、接口约定双方签名是否一致、整体验证命令
（构建/测试）实跑一遍。

结论二选一：

- **PASS**：报告验收结果（逐条标准 + 证据），进收尾。
- **FAIL**：把问题清单写成 delta 指令（只说差量，不重述全方案），按各 agent
  的 resume 方式回派**同一 session**。最多 2 轮返工。仍不过 → 允许**一次**
  升梯队重派（如 MiniMax→kimi、kimi→codex），新 prompt 里写清失败历史与已试
  路径，避免重蹈；升梯队仍不过则停下，把现状与问题清单交用户裁决。
  Claude 接手实施必须由用户明说。

例外（验收手改 ROI 条款）：FAIL 项回派还是手改，按 Phase 0 同款 ROI 判断，
不设行数门槛——当修正**不涉及新的设计决策**、不需要重新推敲 agent 的实现思路，
且 Claude 直接改的成本明显低于一轮回派往返（组 delta prompt + agent 拉起自验 +
再验收）时，Claude 可直接改，并在验收报告中逐项注明"此项为 Claude 手改"。
两条护栏：涉及设计决策的修正一律回派；手改若成为主要修复手段（多数 FAIL 项
都在手改），说明本次委派质量不达标，应走回派/升梯队而非 Claude 逐项代修。

## 收尾

- 更新 `.plans/` 任务状态（若 Phase 1 有持久化）。
- 重大设计决策按 `nmem-save` 约定写回 nmem；能力矩阵的校准证据（某 agent 在
  某类任务上的实际表现）一并写回，并同步更新本文件的矩阵评级。
- 不自动 commit/push；由用户另行发起（可用 `git-sync`）。

## 边界（Not for）

- 纯排查 bug → `hunt`；纯 review → `check`；纯文档 → `write-document`。
- 用户直接说 `/codex:rescue ...` → 走 codex 插件原生命令，不套本流程。
- 所有 agent 不可用时本 skill 不降级为 Claude 实施——报告并停。
- 不因"任务像开发任务"自动进入——仅显式 `/delegate`。
