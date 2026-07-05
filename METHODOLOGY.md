# 工程方法论：门 · 证 · 环 · 剃

个人 AI 工程体系的单一事实源。本文是地图，不是领土：原则和结构在这里，
可执行细节活在各 skill 正文、shared/ 契约和脚本里（见文末指针索引）。

体系服务于一个目标：把资深工程师的隐性判断显性化为可路由、可验证、
可演进的技能系统，让每一次排查、设计、评审的产出都回流成下一次的起点。

## 体系全景：五层能力矩阵

| 层 | 载体 | 核心资产 | 治理机制 |
|---|---|---|---|
| 哲学层 | 人 + nmem | 边界导向、长期主义、系统化思维 | nmem 决策记忆持续沉淀 |
| 方法论层 | agent-cookbook（随人走，个人 GitHub） | 四门 + shared/ 公约 + knowledge preflight | RESOLVER 路由表 + verify-skills.sh 合同 + legacy 停车场 |
| 项目绑定层 | mt-skills（公司 git，submodule） | cs-coding + kb-search 等 MT skill + project-routing.md | 依赖方向单向：MT 可引用通用，通用永不点名 MT |
| 领域作战层 | mlbattle 四仓（随仓走） | bdt CLI → mlbattle-kb 知识服务 → battle-debug 引擎 → eval/case/pattern 治理 | 安全红线、evidence_strength 分级、process_log 契约、`bdt kb submit` 单写者 |
| 协作层 | lark-* 全家桶 | 飞书作为工作 IO：单据进、交付出 | lark-cli `_notice` 自引导 |
| 思想供给层 | refs/ 只读子模块 | Waza、ponytail、hai-stack、mattpocock、lark-skills | 三层复用纪律（见"剃"） |

两级 skills 的咬合：用户级是方法论与工具箱，项目级是作战流水线，
通过同名特化 override（kb-search）、双向负边界声明（cs-coding ↔ check ↔
battle-debug ↔ p4-review）、上下游数据（lark-proj 读单是 bug corpus 上游）
三种机制对接。

## 四支柱

### 门（Doors）：按任务生命周期切分入口，负边界成对咬合

- 写码前 `plan`（立场先行：Lightweight 快速立场 / Design / Evaluate /
  Refactor / Grill / Review），写码时 `cs-coding`，写码后 `check`，
  坏了 `hunt`，沉淀 `write-document`。
- 每门声明 "Not for X" 并指名邻居；门间交接是显式握手
  （"可以干 / 按计划实施" 在 plan handoff 与 check Mode Picker 对称出现）。
- 技能化的是约束与阶段，不是动作本身（泛名 code 门被 deletion test 否决）。

### 证（Evidence）：结论必须可对账，证据有强度等级

- evidence_strength 分级 + cap 机制（lint 层强制）；表现层/sync 结论上限 medium。
- 双源诚信核验：process_log 自述 vs transcript 行为铁证交叉。
- 探针取证闭环：probe-first 注入、仅限日志类调用、用完还原。
- 反证标准：规避假设根因后异常消失才升 confirmed。
- "证" 同样作用于自我审计：ground truth 直证 + 对抗式复核，纠错公开认账。

### 环（Loop）：取之前查、产之后写、定期评估反哺

- 前端强制取：knowledge preflight 是四门的硬节点（起草前/review 前/
  假设前/动笔前），非阻塞降级。
- 后端契约写：KB Inputs Used 必填、Knowledge Gap 强制暴露、
  本回合不 submit 不结束。
- Case-first 链路：bug → case → pattern → knowledge → 索引 → 下次召回；
  pattern 与工作流解耦，知识独立演进。
- 盲测评估闭环：只读盲排 → 对照 → 规则缺口 → 回补 → 重测；
  原理性知识优先于条件规则补丁。

### 剃（Razor）：能力收敛不堆积

- 存在性判据只有一条：删掉它会不会让一个现代 Agent 明显变差。
- 三层复用谱系：直接软链（跟上游）→ fork 剥离（注明出处、剥掉特化）→
  纯思想蒸馏（不引入依赖）。
- 分层原则：需要判断 → skill；确定性 → script/CLI。
- 硬约束倒逼收敛：Codex 2% skills context budget，新增 skill 前体积评估。
- 防膨胀进产物层：progress.md 滚动摘要、findings.md 上限约 400 行。

## 五条工作回路

| 回路 | 链路 | 成熟度 |
|---|---|---|
| Bug 排查 | 飞书单 → hunt → battle-debug（双模式）→ 取证 → 修复（cs-coding）→ p4-review → 收口 → case → pattern → KB | 最成熟，全链自动化 |
| 需求实现 | story → plan（altitude 判断，非平凡落 .plans/）→ check Plan Execution → cs-coding → check review → p4-dev → closeout → 周报 | 成熟 |
| 知识 | 个人决策 → nmem；领域事实 → KB；preflight 强制读，产物契约强制写 | 贯穿所有回路 |
| 评估 | blind-env → eval / eval-concurrent → eval-stats → goal-iterate → 缺口回补 | battle-debug 域专属 |
| 技能演进 | 观察摩擦 → 剃刀评估 → 选复用层级 → verify 合同 → RESOLVER → legacy 停车 | 元回路 |

## 治理规则

- **触发原则 v2**：副作用决定显式/自动。方法论 skill 自动触发
  （误触发最坏代价是多读一页规范）；碰版本库/外部状态的操作 skill 显式调用。
- **shared/ 准入**：至少 2 个消费者才进 shared；禁止跨技能引用
  references（跨技能共享一律走 shared）。
- **持久化契约**：.plans/ 三件套按 `shared/plan-artifacts.md`；
  plan 创建、check Plan Execution 滚动更新 progress、plan Review 验收。
- **提交纪律**：mt-skills 先 commit/push，父仓再更新 submodule 指针；
  不被要求不提交。
- **refs/ 只读**：只经脚本移指针，不为上游瑕疵买单。

## 观测与演进

路由可靠性是本体系当前最脆假设，观测先于优化。

基线（2026-07-03，30 天窗口）：527 个 session 中 52 个触发过 skill
（约 10%），8 个进过前门（约 1.5%）；think 调用 8 次高于 plan 的 6 次
（think 已退役、能力并入 plan Lightweight）；write-document 与 cs-coding
零调用，是下一步路由验证重点。

节奏：每月跑一次 `/skill-usage-report`（agent-cookbook own skill，内含
观测脚本与月报模板）对比基线；路由 hit/miss/misfire 的判定需要判断而非
计数，配合人工或 agent 辅助抽查。

已知缺口（工作机侧执行债，随 working memory 滚动）：bdt `--pipeline`
分发同步、HeroTest headless 完整链路入 CI、mt-skills dev 分支推送节奏。

## 指针索引

| 主题 | 位置 |
|---|---|
| 门的正文与模式 | `skills/{plan,check,hunt,write-document,cs-coding}/SKILL.md` |
| 跨门公约 | agent-cookbook `shared/`（common-core、languages、knowledge-preflight、agent-constraints、plan-artifacts）；MT 绑定在 mt-skills `shared/`（project-routing、workspace-facts） |
| 路由表与合同 | agent-cookbook `skills/RESOLVER.md` + `scripts/verify-skills.sh` |
| 用量观测 | agent-cookbook `skills/skill-usage-report/`（月度流程 + 观测脚本） |
| 演化史 | agent-cookbook `legacy/`（含 rules 退役映射）与 `.plans/001-mt-skills-five-doors/` |
| 领域作战面 | mlbattle-debug 及其子仓 `.claude/skills`（battle-debug、eval 家族、p4 家族） |
| 上游思想 | agent-cookbook `refs/`（Waza、ponytail、hai-stack、mattpocock-skills、lark-skills） |
