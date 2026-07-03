# mt-skills 四门 + 编码规范层落地计划（plan / check / hunt / write-document + cs-coding）

> 状态：**P1–P6 已完成，P7 取消（不再需要）**。实施期间提交由用户触发（commitall）。
> 本计划由 /plan 产出，调研证据：agent-cookbook 全仓、refs/Waza（MIT）、refs/ponytail、refs/hai-stack、refs/mattpocock-skills、mlbattle-debug（docs/skills + dotnet-runtime skills + mlbattle-kb KB + bdt v1.15.x 命令面）。
> 2026-07-02 修订 v2：吸收 nmem 工作记忆（Codex symlink/加载行为、explicit-only 触发治理先例、planning 文档膨胀教训、Skill vs KB 划界原则、周报写作规范），并新增 shared/ 共用基座层（Key Decision 3）。
> 2026-07-02 修订 v3：**取消泛用 code 门**（deletion test 不过；Waza 亦无 code 技能）。cs-coding-style 改名 **cs-coding** 扩权为 C# 编码门；计划执行归 check 的 Plan Execution；lazy 保留不退役；净减技能数口径校正为 -10。计划目录名 001-mt-skills-five-doors 保留不改。
> 2026-07-02 修订 v3.1：KD8 触发口径定案——用户更新总原则为「默认自动触发，仅设计上需要主动调用的才显式」，nmem 旧 explicit-only 原则已 supersede。
> 2026-07-02 修订 v3.2：Phases 按**改动半径**显式分层——仓库之外的动作集中标记：P1 矩阵首测标【仓外·只读】，P6 的 `rm ~/.claude/rules` 标【仓外】（本计划唯一的本机状态变更），**工作机部署与跨 runtime `cp -RL` 物化从 P6 拆出独立成 P7（纯仓外阶段）**；Rollback 按仓内/仓外分列回滚方式。
> **上下文自足**：本目录 `findings.md` = 调研证据与仓库现状快照（软链拓扑、Waza fork 素材清单、部署机制、nmem 记忆锚点），`progress.md` = 阶段状态。全新会话凭这三个文件 + 仓内实况即可执行，无需本次会话历史。

## Goal

在 mt-skills（工作专用、跨项目、自包含的 git 子模块）内建成"四门 + 编码规范层"：
**plan（方案）· check（审查 + 计划执行）· hunt（排查）· write-document（文档）**，
写码不设泛用门——由 **cs-coding**（cs-coding-style 改名扩权）等语言编码规范直接承接，
使 agent 在写代码、做方案、审查、排查、写文档时跟随固定规范，并在固定节点挂接项目知识
（bdt / 战斗 KB / lark 链路 / nmem），同时退役 `rules/` 目录
（部分 coding agent runtime 不加载 rules，规范必须由 skill 承载）。

## Building

一套三层分工下的工作技能中枢：agent-cookbook 继续做个人全局聚合（skills/ 软链到
~/.claude/skills 与 ~/.agents/skills）；mt-skills 承载四门 + cs-coding（改名自
cs-coding-style）+ 既有 3 技能（kb-search、lark-proj、lark-story-closeout），自包含、
可单独 clone 到工作机；mlbattle-debug 项目技能保持现状，各门只**路由**到它们，不复制
业务细节。四门统一采用 Waza 骨架（Outcome Contract / Mode Picker / Hard Rules / Gotchas /
Output+Sign-off / references 分层），cs-coding 保持现有 authoring 结构，均在固定位置
内嵌三类项目挂钩（见 Key Decision 2）。

## Not Building

- **不重建 planning-in 的重机械**：PreToolUse/Stop hooks、`_index.json` 索引、状态面板、
  `session-catchup.py`、planning-review 的多智能体评审编排。plan 的 Persist（task_plan /
  findings / progress 三件套）+ Grill/Review 模式覆盖 80% 需求；若跨 session 恢复之痛复发，
  再单独立项把索引脚本请回来（明确的止损点，不预建）。
- **不建泛用 `code` 门**：写码是 agent 的默认能力，需要技能化的是约束与阶段（Waza 亦无
  code 技能）。对 C# 主场景它只是 cs-coding 的透传壳（deletion test 不过）；计划执行由
  check 的 Plan Execution 模式承接。
- **不给 mt-skills 建独立校验脚本**：沿用 agent-cookbook 的 `verify-skills.sh`（经软链生效）。
- **不动 lark 分层**：refs/lark-skills 软链 + mt-skills 自写补充（lark-proj、lark-story-closeout）维持现状。
- **不动 design（Waza）**：UI 场景无替代，保留软链。
- **不做门间自动串联**：沿 Waza 约定，每门做完即停，由用户或明确授权语推进（"按计划实施"除外）。
- **不复制项目业务细节进 mt-skills**：路由只点名目标技能 + 一句判据；表结构、枚举、范式正文留在 KB 与项目技能里。
- **shared 基座只放规范与方法论，不放事实性知识**（用户既定 Skill vs KB 划界原则：历史案例、
  危险区域清单、开关等价关系等 descriptive 知识归 KB，走 kb-search）。
- **不因共用层引入构建/生成步骤**：shared 靠目录内相对软链复用（内核级解析），拒绝 build-time 拼装。
- **不引入新语言/运行时/依赖**。

## Approach

**fork-and-own Waza（MIT，保留 attribution），落 mt-skills 真实目录，agent-cookbook 以软链接入。**
check/hunt 直接 fork 改造，plan 迁移现有草稿收尾，write-document 新写（按 Waza 骨架），
cs-coding 由 cs-coding-style 改名扩权。
每个技能剥离 Waza 专属机件（check-update.sh 调用、rules/durable-context.md 链接、GitHub
维护者特化），换成本工作流的等价物（nmem 记忆预检、bdt kb 知识预检、飞书/P4 路由）。

**已否决的近选项**：薄包装（各门只写挂钩与路由，方法论仍引用 refs/Waza 软链）。
否决理由：mt-skills 必须自包含（工作机不保证装 Waza）；且各门的价值恰在于把方法论与项目
知识焊在同一文本里，薄包装做不到。代价（接受）：上游 Waza 演进不再自动同步，需要
`scripts/update-submodules.sh` 后手动 diff 回灌，频率预计每季度一次以内。

## Key Decisions

1. **四门 + cs-coding 落 `mt-skills/skills/<name>`，双端接入**。个人机：agent-cookbook
   `skills/<name>` 软链。工作机：clone mt-skills，按 mlbattle-debug 既有"docs/skills 每技能
   软链"模式接入（同 bdt / dotnet 技能的再导出方式），进 P4 worktree 用 update-skills-deploy
   推送。任何**复制式部署必须解引用软链（`cp -RL`）**，否则 shared 基座（决策 3）断链。
   **泛用 `code` 门取消，职责拆解**：计划执行 → check 的 Plan Execution 模式（Waza 原生分工）；
   C# 写码门 → cs-coding-style **改名 `cs-coding`** 并扩权（引 shared 基座 + 写后出口；范围
   早已超出 style，趁引用少改名最便宜）；Python/Go 规范 → `shared/languages.md`（check 审查
   面引用兜底，某语言规范变重时再立 `py-coding` 类对称技能，YAGNI）；写码期"别过度设计"
   反射 → **lazy 保留不退役**。
2. **三类挂钩，固定位置，带降级语义**（"关联项目知识、有指导方向、不含业务细节"的实现方式）：
   - *知识预检*：nmem search（个人决策/先例）+ 战斗 KB（经 kb-search）。节点：plan
     Design/Refactor 动笔前、hunt 立假设前、check 开审前、cs-coding 碰高危符号前。**检索细节
     （hybrid 模式、facet、--obs/--expand）统一由 kb-search 承载，各门只写节点与检索意图**
     （nmem 实证：短技术词纯向量召回不可靠、优先 hybrid——这类经验只沉淀在 kb-search 一处）。
     bdt 不存在或 KB 不可达 → 显式说明并跳过，不阻塞。预检契约写成 shared 基座一页，各门引用。
   - *路由*：命中项目场景即转项目技能（hunt→battle-debug/desync-analysis/regression-forensics/
     line-origin-forensics；check→p4-review/p4-patch；cs-coding→build-compat/`bdt cs`；
     write-document→battle-debug-write-knowledge/markdown-to-lark-doc/project-requirement）。
     只点名 + 一句判据，**判据看动作不看业务词**（p4-dev 路由边界先例）。**explicit-only 技能
     （p4-review、p4-dev 等已设 disable-model-invocation 的 P4 操作技能）只提示用户显式调用，
     不代触发**——沿用 2026-05-13 误触发治理确立的约定。
   - *规范内嵌*：rules 内容折叠进 shared 基座 + 技能 references（先例：csharp rule → cs-coding-style）。
3. **共用基座层 `mt-skills/shared/`（去 rule 化的 base 文档层，Waza `rules/` 的自包含版）**。
   跨技能共用的通用规范不再各门复制，落 shared 单一来源：
   - `shared/common-core.md`：编码风格倾向（不可变更新、小文件）+ 安全底线 + 风险分级测试
     （≤70 行）。消费者：check（审查基线，主）；plan / cs-coding 可选引。
   - `shared/languages.md`：Python / Go 速查（uv、ruff、gosec 等，≤50 行）。消费者：check
     （非 C# 审查兜底，主）；未来 py-coding 类语言门。
   - `shared/knowledge-preflight.md`：知识预检契约（nmem + kb-search 的节点、意图、降级语义，
     ≤30 行）。消费者：plan / check / hunt / write-document 四门全部；cs-coding 自带等效预检
     （高危符号 → kb-search），不为对齐而改引。
   - `shared/agent-constraints.md`：Agent 自我约束通用版（不写变更叙述注释、不越界重构、
     不自动加 fallback、未授权不自动写测试，≤20 行；自 cs-coding-style 提炼，C# 特化留原处）。
     消费者：cs-coding（主）；check 的 drift/scope 检查语义等效（Waza 原生自带），不重复引。
   - `shared/workspace-facts.md`：工作环境稳定接口一页（bdt=机器接口、KB 入口、lark 链路、
     nmem，≤30 行）。消费者：四门与 cs-coding 的路由段按需查阅，不设强制节点。
   进 shared 的门槛：**≥2 个消费者**（markdown-mermaid 单消费者就留在 write-document 正文）。
   **引用机制**：每个门/编码规范技能目录内建相对软链 `shared -> ../../shared`，SKILL.md 一律用
   **向下路径** `shared/xxx.md` 引用——内核按物理位置逐段解析软链，穿透 `~/.claude/skills`
   等任意入口；而向上 `../../shared` 的字符串引用在软链拓扑下会解析错位，禁止使用。
   命名用 `shared` 而非 `rules`，避免与正在退役的 runtime rules 机制混淆。
   verify-skills.sh 的链接检查跟随软链，天然覆盖。
4. **rules 退役的承接映射**：common-coding-style / common-security / common-testing →
   `shared/common-core.md`；python-\*/go-\* → `shared/languages.md`；markdown-mermaid →
   `write-document` 正文（单消费者不进 shared）；README 审计结论存档。全部折叠完成后（P6）：
   删除 `~/.claude/rules` 软链，`rules/` 移入 `legacy/rules/`。**代价（接受）**：rules 的
   always-on 与 `paths:` 条件加载消失，改由"进门必经 + 门内强制引用 shared"近似——实质任务
   从四门或 cs-coding 进，由其把基座装进上下文；非 C# 写码的缝隙见 Premise Collapse。
5. **write（Waza）保留，write-document 新增，职责互斥**：write-document = 结构化文档创作
   （README/设计文档/postmortem/周报/KB 知识/飞书交付）；write = 润色/去AI味/发布文案。
   两边 description 都写 Not-for 互斥行；write-document 的"深度润色"一律路由 write。
6. **净减技能数 + description 撰写规范**：退役 12 项（think、grilling、handoff、
   codebase-design、domain-modeling、improve-codebase-architecture、planning-in×6；**lazy
   保留**，承接写码期"别过度设计"触发面），新增 2 行 active 条目（plan、write-document），
   check/hunt 原地替换、cs-coding 改名不变数，净 **-10**（口径：RESOLVER active 条目数），
   缓解 Codex skills 上下文预算（已超 2% 告警；超限时 description 被截断，触发面必须写在
   句首）。description 遵循既定原则：**只说"做什么 + 何时触发"，不写"怎么做"**；触发词用
   用户意图语言、带"推力"；Not-for 行做互斥。
7. **plan 的对标审计结论**（吸收已完成度）：think 骨架 ✅、lazy/ponytail 7 级阶梯 ✅
   （lazy-ladder.md）、hai-stack 格局/苟 ✅（frame-vs-ground.md）、planning-in 持久化 ✅
   （Persist 段）；**缺口三处**：improve-codebase-architecture 的"深化扫描"入口
   （P1 补 references/refactor-scan.md：Explore 走查 + deletion test + 候选清单，砍 HTML 报告）、
   知识预检段（P1 补，引 shared）、**计划文件防膨胀纪律**（P1 补：吸收 planning-archive 教训——
   历史上 task_plan 曾膨胀到 3365 行 / 60k tokens 拖垮 session 恢复；规则=progress 滚动摘要、
   完成 phase 折叠成一行结论、findings 超 ~400 行先收缩再追加）。另：handoff 的执行侧从
   「code 按 phase 执行」改为 **check 的 Plan Execution 模式**承接（Waza 原生分工），
   plan/references/handoff.md 相应指向 check。
8. **触发口径（已定案，2026-07-02 用户更新总原则）**：skill 默认允许模型自动触发；仅
   **设计上就需要主动调用**的技能设 explicit-only。判据是副作用与流程重量，不是技能类别：
   会碰版本库/外部状态的操作类（p4-dev、p4-review、commitall、update-skills-deploy 等）与
   重流程编排类保持显式调用；约束/方法论/authoring 型（四门、cs-coding、kb-search 等）
   自动触发——误触发最坏代价只是多加载一页规范，无副作用。旧"全部 skill explicit-only"
   原则已在 nmem 废止（supersede →「Skill 触发总原则 v2：默认自动触发，操作类才显式」）。

## Premise Collapse

**本计划假设：在 ~50 个活跃技能中，描述驱动的自动路由能可靠地把意图分发到四门与 cs-coding**
（邻接风险点：check/p4-review、write-document/write/lark-doc、hunt/battle-debug）。
若该假设失败，表现为写 C# 时不加载 cs-coding、或审查时误载错门——门就退化成没人走的正门。
v3 取消泛名 `code` 门后，路由面上最模糊的一环已被移除；cs-coding 的触发面（战斗 C# 关键词 +
主动加载先例）是现存最强的。显式接受的缝隙：**非 C# 写码没有专属门**，由 lazy（过度设计
反射，保留）、check（审查期引 shared/languages.md 兜底）、全局 CLAUDE.md（uv 约定）三处
覆盖；某语言写码规范变重时再立 `py-coding` 类对称技能。
这不是假想风险：p4-review / p4-dev 在 2026-05-13 真实发生过误触发，最终靠
disable-model-invocation + description 触发词收敛治理——说明触发面冲突会发生，也说明治理
手段有效。计划已内嵌的抵抗：description 全部带 Not-for 互斥行 + 中文触发词表；退役 12 个
重叠技能减少竞争；RESOLVER 分区 + 分歧注记。若仍失效：退路是养成显式
`/plan /check /hunt /cs-coding` 调用习惯，并考虑复活 planning-in 的 hook 思路做强制注入
（注意该退路**仅 Claude Code 可用**——Codex hooks 目前只有 SessionStart/Stop，没有
PreToolUse；Codex 侧只能靠显式调用）。

次级脆弱点一：mt-skills 自包含性依赖"工作机 bdt 全局可用 + 项目技能可缺席降级"。降级语义
在每个挂钩点显式写出（Key Decision 2），实施时逐条验收。

次级脆弱点二：**软链在各 runtime 的加载行为不一致**（nmem 记忆存在冲突证据：一条说 Codex
忽略 symlink 目录，另一条说官方支持 `.agents/skills` 软链；本机 `~/.codex/skills` 目前为空，
Codex 实际经由项目级 `.agents/skills` 或插件加载）。对策：P1 就做 runtime 兼容矩阵实测
（Verification 第 5 条），软链失效的 runtime 一律走 `cp -RL` 物化 + update-skills-deploy
同步模式，不赌行为（物化动作集中在 P7 统一执行）。

## External Dependencies

无新增。bdt（全局已装，v1.15.x）、lark-cli（已装）、nmem（已装）、Waza fork 依据 MIT。

## Verification Plan（每阶段必跑）

1. `bash scripts/verify-skills.sh` 全绿（frontmatter/RESOLVER/软链/链接/表格）。
2. 软链解析：`ls -la ~/.claude/skills/<name>` 指向 mt-skills 且 SKILL.md 可读；
   `cat ~/.claude/skills/<name>/shared/common-core.md` 穿透两层软链可读（shared 基座解析验证）。
3. 触发冒烟（人工，新开 session）：每门 ≥2 条触发语句命中本门、≥1 条邻接语句不误触
   （冒烟表见各阶段）。
4. mt-skills 子仓先 commit，agent-cookbook 后更新指针（commitall 已支持子模块顺序）。
5. **runtime 兼容矩阵**（P1 建立，P7 复测）：Claude Code（个人机软链入口）✅ 预期直通；
   Codex 项目级 `.agents/skills`（官方声明支持软链）实测一次；Codex 用户级 `~/.codex/skills`
   实测 symlink 目录是否被忽略（nmem 两条记忆互相矛盾，以实测为准）——被忽略则该入口改
   `cp -RL` 物化。每格记录：入口路径 / 软链是否直通 / shared 是否可读 / description 是否被
   2% 预算截断。

## Rollback

全部动作可逆，按改动半径分两类：

- **仓内（无标记步骤，P1–P6 主体）**：软链替换可原样换回（refs/Waza、mattpocock 目标不动）；
  退役 = mv 进 legacy/（不删除）；rules/ 移 legacy 前不改内容；两仓均为 git，按阶段 revert。
- **仓外（【仓外】标记步骤 + P7 整阶段）**：不受 git 回滚覆盖，逐项手工可逆——
  `~/.claude/rules` 软链删除后可一条 `ln -s` 重建（rules/ 内容在 legacy/ 原样保留）；
  工作机部署与 `cp -RL` 物化副本删除即整体回滚，不影响两仓；P1 矩阵首测为只读，无需回滚。

---

## Phases

> **改动半径标记**：无标记步骤全部落在两仓之内（mt-skills / agent-cookbook），git 按阶段 revert
> 可回滚；标 **【仓外】** 的步骤触碰仓库之外的状态（家目录软链、其他 runtime 入口、工作机），
> 回滚方式见 Rollback。仓外动作全部集中在三处：**P1 第 7 步**（矩阵首测，只读）、
> **P6 第 2 步**（`rm ~/.claude/rules`，本计划唯一的本机状态变更）、**P7 整阶段**
> （工作机部署 + 跨 runtime 物化，纯仓外，不改两仓内容）。

### P1 — shared 基座 + plan 迁入 mt-skills + 第一批退役 + RESOLVER 重写

1. 新建 `mt-skills/shared/`（Key Decision 3 的五个文件**一次建齐**，rules 折叠在此完成：
   common-\* → common-core.md、python-\*/go-\* → languages.md）。
2. `mv skills/plan mt-skills/skills/plan`（当前未跟踪，直接移）+ `ln -s ../mt-skills/skills/plan
   skills/plan` + 技能目录内建 `shared -> ../../shared` 软链。
3. plan 补三个缺口：
   - SKILL.md 增「知识预检」小节（引 `shared/knowledge-preflight.md`，≤8 行）；
   - 新增 `references/refactor-scan.md`（≤50 行）：改造前扫描 = Explore 走查 → deletion test →
     候选清单（Files/Problem/Solution/强度分级），输出 markdown 而非 HTML；Refactor 模式开头引用。
   - Persist the Plan 增防膨胀纪律（≤6 行）：progress 滚动摘要、完成 phase 折叠成一行结论、
     findings 超 ~400 行先收缩再追加（吸收 planning-archive 的 60k tokens 教训）。
   - Hard Rules 中 `.claude/rules/` 措辞改为「AGENTS.md / CLAUDE.md 等项目硬规则」。
4. 退役：删软链 think、grilling、handoff、codebase-design、domain-modeling、
   improve-codebase-architecture；`mv skills/planning-in* skills/planning-organize
   skills/planning-review skills/planning-split legacy/`（6 个 planning；**lazy 保留**，
   承接写码期"别过度设计"触发面）。
5. RESOLVER.md 重写：新增「Front Doors」分区（本阶段先 plan 一行）与「Coding Guides」分区
   （现名 cs-coding-style，P2 改名后更新），删除退役行，Legacy 表补映射（planning-\* → plan；
   grilling → plan Grill 模式；handoff → plan references/handoff.md；codebase-design/
   domain-modeling → plan references/deep-modules.md；improve-codebase-architecture →
   plan references/refactor-scan.md）。
6. 新建 `mt-skills/README.md`：技能清单、shared 基座说明、自包含声明、个人机/工作机两种接入
   方式（agent-cookbook 软链 / docs/skills 软链 + update-skills-deploy，复制式部署必须 `cp -RL`）、
   **kb-search 双事实源声明**（跨项目规范源=mt-skills，mlbattle-debug 内副本以之为准）。
7. 【仓外·只读】建立 runtime 兼容矩阵（Verification 第 5 条首测：Claude Code 软链 + Codex 两个
   入口 + shared 穿透）。只实测并记录结论，不改任何仓外状态；若某入口软链失效，`cp -RL` 物化
   推迟到 P7 统一执行。
8. 验收：Verification Plan 1-5 + 冒烟（命中：「出个方案」「帮我拷问这个计划」「验收一下」；
   不误触：「排查这个报错」应走 hunt/battle-debug）。

### P2 — cs-coding-style 改名 cs-coding + 扩权为 C# 编码门

1. `git mv mt-skills/skills/cs-coding-style mt-skills/skills/cs-coding`，frontmatter `name`
   同步改；agent-cookbook 软链改名重建；RESOLVER「Coding Guides」行更新。趁引用还少
   （技能 7/1 才建）改名成本最低；"-style" 名不副实——技能早已覆盖写前决策/帧同步/生命周期，
   不只是风格。
2. 扩权（增量 ≤15 行，心法/机械规范/写前决策/自检全部不动）：
   - 目录内建 `shared -> ../../shared` 软链；
   - 「Agent 自我约束」节改为引 `shared/agent-constraints.md` 通用版 + 保留 C# 特有条目；
   - 两处 `.claude/rules` 措辞改「AGENTS.md/CLAUDE.md」（rules 退役前先解耦，原 P6 项提前）；
   - 增写后出口一行（verify / check）。
3. description 同步 name 改动，保持既有触发面（战斗 C# 关键词、主动加载语义）与 Not-for
   （review→check/p4-review、排查→battle-debug、Lua/纯配置不触发）。
4. 验收：标准 5 项 + 冒烟（命中：「帮我写个战斗字段」「按我的规范写 C#」→ cs-coding；
   「按计划实施」→ check Plan Execution（P3 前由 Waza check 暂接）；「review 一下」不误触）。

### P3 — check fork（审查门）

1. `cp -r refs/Waza/skills/check mt-skills/skills/check`（含 references/persona-catalog.md、
   project-context.md、agents/reviewer-security.md、reviewer-architecture.md、
   scripts/audit_signals.py；**不带** public-reply.md），文件头注明 fork 自 Waza vX + MIT。
2. 剥离：check-update.sh 调用、durable-context 链接（换 nmem 预检）、Triage 模式的 GitHub
   队列流、release reactions/appcast 细节；**保留** Worktree Safety、Hard Stops、Finding
   Quality Gate、Autofix 分级、Plan Execution（**承接 plan handoff 的执行入口**——取消 code
   门后「按计划实施」由此进）、精简版 Ship（release gate 矩阵 + 生成物核对）、
   Project Audit（含 audit_signals.py）。目标 ≤300 行。
3. 新增工作挂钩：开审前知识预检（引 `shared/knowledge-preflight.md`，经 kb-search 拉该子系统
   已知反范式做 checklist，检索细节不进本门）；审查基线引 `shared/common-core.md` +
   `shared/languages.md`（非 C# 语言规范的兜底消费点）；diff 来源分流表（git diff → 本门；P4
   CL/shelf/opened/飞书单 → **提示用户显式调用 `/p4-review`**、patch registry → `/p4-patch`——
   两者是 explicit-only 技能，本门不代触发）；C# 战斗维度（引用 cs-coding 写后自检 + KB
   `reference/coding_style.md`/`code_conventions.md` 的「现象→检查点」映射，按名路由不复制正文）。
4. 替换软链：`skills/check` 改指 `../mt-skills/skills/check`；RESOLVER 更新。
5. 验收：标准 5 项 + 冒烟（命中：「看看这个 diff」「合并前检查」「按计划实施」；
   「review 这个 CL」应提示 /p4-review；「项目体检」仍命中本门 Audit 模式）。

### P4 — hunt fork（排查门）

1. `cp -r refs/Waza/skills/hunt mt-skills/skills/hunt`（references 只带 failure-patterns.md、
   logging-techniques.md；ime-unicode/rendering-debug 不带，需要时回 refs 查），MIT 注记同上。
2. 保留全套根因纪律：一句话根因 file:line、三假设硬停 + Handoff 模板、Bisect（worktree 保护）、
   Scope Blast（举一反三）、Runtime Evidence Ladder、靶向日志；Native Freeze 模式精简为一小节。
   目标 ≤220 行。
3. 新增工作挂钩：立假设前症状预检（引 `shared/knowledge-preflight.md`，经 kb-search 搜症状
   范式 + cases 同型历史 + bug-history，检索细节不进本门）；路由表（战斗逻辑 bug/replay →
   battle-debug、desync 日志 → desync-analysis、「哪个提交引入」→ regression-forensics、
   行级溯源 → line-origin-forensics/svn-diff、编译不过 → build-compat）；修后回写提示
   （值得沉淀的根因 → nmem / battle-debug-write-knowledge，提示不强制）。
4. 替换软链 + RESOLVER。
5. 验收：标准 5 项 + 冒烟（命中：「这个报错查一下」「以前是好的」；「战斗里技能没伤害」
   应路由 battle-debug；「review 代码」不误触）。

### P5 — write-document 新建（文档门）

1. 新建 `mt-skills/skills/write-document/`：SKILL.md ≤150 行（交付路由内嵌正文，暂不设
   references；膨胀再拆）。
2. 内容：文档类型路由（README/设计文档/postmortem/周报/KB 知识文档/飞书文档，各给骨架要点；
   **周报直接内嵌已沉淀的飞书周进展结构**——概述→画板(可选)→主要进展→后续安排、动词开头写
   "做了什么"、不搞一二三分节，出处为 nmem 的 mlbattle 周进展写作规范 procedure）；写前知识
   预检（引 `shared/knowledge-preflight.md`，文档规范类先例优先查 nmem；参考已有飞书文档用
   webforage / lark-doc 读取——WebFetch 无飞书登录态，已实证不可用）；markdown 规范（含 mermaid
   节点换行用 `<br/>` 这一条 rules 遗产）；结构纪律（借 Waza write Longform 思路：跨节重复收敛、
   表格不复读、删段先确认信息量）；交付链路由（本地 md → 飞书 → markdown-to-lark-doc / lark-doc；
   KB 知识 → battle-debug-write-knowledge（按其 frontmatter 契约）；Notion → notion-md-sync；
   项目主文档 → project-requirement/project-sync）；深度润色/去AI味 → 路由 write（保留的 Waza
   门），工作机缺席时给 3 条内嵌底线（禁 em-dash、中英文空格、只交成稿）。
3. description 互斥：Not-for 润色/文案/推文（write）、纯代码注释与 commit message。
4. agent-cookbook 软链 + RESOLVER Front Doors 收齐四门。
5. 验收：标准 5 项 + 冒烟（命中：「写篇设计文档」「把这个整理成周报」；「润色这段」应走 write；
   「md 推到飞书」应走 markdown-to-lark-doc）。

### P6 — rules 退役收尾 + 文档同步（仓外动作仅第 2 步删软链一处）

1. 前置核对：P2/P5 已合并（承接内容在位）。
2. 【仓外】`rm ~/.claude/rules`（软链——本计划唯一的本机状态变更；先删再做下一步，避免
   悬空软链窗口）；随后仓内 `git mv rules legacy/rules`；`legacy/rules/README.md` 顶部
   加退役声明 + 去向映射表（Key Decision 3）。
3. 复核 cs-coding（P2 已完成 rules 措辞解耦与 shared 接入）：全仓 grep `.claude/rules`
   确认无残留引用。
4. AGENTS.md 更新：Layout 图（rules → legacy、新增 mt-skills/shared）、Rules 章节改为退役说明、
   新增「Front Doors」一节描述四门 + cs-coding + shared 基座 + mt-skills 双端接入；RESOLVER 终检。
5. 验收：标准 1-4 项 + `~/.claude/rules` 不存在且新 session 无 rules 注入 + RESOLVER active
   条目净变化 ≤ -10 核对（runtime 矩阵复测与工作机部署移至 P7）。

### P7 —【仓外】工作机部署 + 跨 runtime 物化（纯仓库外阶段）

> 本阶段不改两仓内容（仅回写本计划目录的 findings/progress 记录）；全部实质动作发生在
> 工作机与本机其他 runtime 入口，回滚 = 删除部署产物（见 Rollback）。

1. 工作机：clone mt-skills + 按 mlbattle-debug 既有模式 docs/skills 每技能软链接入，进 P4
   worktree 跑 update-skills-deploy 推送（复制式部署验证 `cp -RL` 解引用后 shared 内容在
   副本内可读）。
2. 本机：对 P1 矩阵判定软链失效的 runtime 入口执行 `cp -RL` 物化，改走 update-skills-deploy
   同步模式。
3. runtime 兼容矩阵复测（Verification 第 5 条全格重跑，含 description 2% 预算截断检查），
   结论回写本目录 findings.md。
4. 工作机冒烟：四门与 cs-coding 各 1 条 + 降级语义 1 条（KB 不可达时 plan 仍可用）。
5. 验收：矩阵全格成档 + 冒烟通过。

---

## 冒烟触发语句总表（验收用）

| 门 | 应命中 | 不应误触 |
|---|---|---|
| plan | 出个方案 / 值不值得做 / 拷问这个计划 / 验收一下 | 排查报错（hunt）、看看 diff（check） |
| cs-coding | 帮我写个战斗字段 / 按我的规范写 C# / 改 ISHOW | review（check/p4-review）、排查（battle-debug）、Lua/纯配置 |
| check | 看看代码 / 合并前 / 按计划实施 / 项目体检 | review 这个 CL（p4-review）、润色文档（write） |
| hunt | 查一下报错 / 以前是好的 / 反复修不好 | 战斗技能 bug 直达 battle-debug、出方案（plan） |
| write-document | 写设计文档 / 整理成周报 / 写 KB 知识 | 润色去AI味（write）、md 推飞书（markdown-to-lark-doc） |
