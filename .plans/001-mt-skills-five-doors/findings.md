# findings.md — 调研证据与现状快照（2026-07-02）

供全新会话执行 task_plan.md 时恢复上下文，免于重复调研。事实以本文件记录时点为准，
执行前若仓库有变动，以 `git status` 实况覆盖本快照。

## 1. agent-cookbook 现状（个人机）

- 仓库根：`/Users/ansz/dev/agent-cookbook`。runtime 软链三条：
  `~/.claude/skills` 与 `~/.agents/skills` → `agent-cookbook/skills/`；
  `~/.claude/rules` → `agent-cookbook/rules/`（P6 退役对象）。
- `git status` 关键项（规划时点）：`skills/plan/` 与 `.plans/` 未跟踪；
  `.gitmodules`、`AGENTS.md` 已修改；`refs/mt-skills → mt-skills` 重命名已发生；
  四个 mt-skills 软链（cs-coding-style/kb-search/lark-proj/lark-story-closeout）为已暂存改动。
- `skills/` 拓扑分类：
  - Waza 软链：think、check、hunt、design、write（→ `refs/Waza/skills/*`）；
  - mattpocock 软链：codebase-design、domain-modeling、grilling、handoff、
    improve-codebase-architecture；
  - mt-skills 软链：cs-coding-style、kb-search、lark-proj、lark-story-closeout
    （→ `../mt-skills/skills/*`，五门照此模式）；
  - lark-skills 软链 ×20（lark-*）；
  - 自有真实目录：lazy(81 行，ponytail 蒸馏，**保留**)、planning-in(507 行+4 脚本)、
    planning-in-remove/-status、planning-organize、planning-review(487 行)、planning-split、
    webforage、commitall、markdown-to-lark-doc、notion-md-sync、pc-wsl-docker、
    finding-lark-chat-history、git-remote-sync、architecture-diagram、
    architecture-to-lark-whiteboard、**plan（未跟踪新目录，P1 迁移对象）**。
- `legacy/` 现有：brainstorming、cs-style-check、p4-ops、systematic-debugging。
  `scripts/verify-skills.sh`（210 行）在 L101-103 **硬编码检查** brainstorming 与
  systematic-debugging 的存在性；其余契约：frontmatter name=目录名、RESOLVER 全覆盖、
  软链不破、相对链接可解析（`test -e` 跟随软链）、表格竖线转义。
- `mt-skills/`：独立 git 仓（submodule）。`skills/` 下现有 4 个：cs-coding-style
  （SKILL.md 153 行 + 7 references；`.claude/rules` 引用在 **L70-71 与 L114**，P2 解耦）、
  kb-search、lark-proj、lark-story-closeout（均单 SKILL.md）。
- plan 草稿（`skills/plan/`）：SKILL.md 115 行 + references 6 个
  （frame-vs-ground / lazy-ladder / deep-modules / handoff / evaluation / review-gate）。
  已内化：think 骨架、ponytail 7 级阶梯、hai-stack geju/goudi、planning-in 持久化三件套。

## 2. Waza fork 素材（refs/Waza，MIT © 2026 Tw93，fork 需保留 attribution）

- 统一骨架：🥷 首行 → Outcome Contract（Outcome/Done when/Evidence/Output）→
  Durable Context Preflight → Modes（Mode Picker 分流）→ Hard Rules（check 叫 Hard Stops）→
  Gotchas 两列表 → Output/Sign-off。references=按需目录，scripts=确定性，agents=评审员 prompt。
- check（404 行）fork 清单：带 references/{persona-catalog.md, project-context.md} +
  agents/{reviewer-security.md, reviewer-architecture.md} + scripts/audit_signals.py；
  **不带** public-reply.md。砍：Triage GitHub 队列流、release reactions/appcast。
  保：Worktree Safety、Hard Stops、Finding Quality Gate、Autofix 分级、Plan Execution
  （承接 plan handoff 执行）、精简 Ship、Project Audit。
- hunt（232 行）fork 清单：带 references/{failure-patterns.md, logging-techniques.md}；
  **不带** ime-unicode.md、rendering-debug.md。保根因纪律全套（一句话根因/三假设硬停/
  Bisect/Scope Blast/证据阶梯/靶向日志/Handoff 模板）；Native Freeze 精简成一小节。
- 两个 fork 都要剥离：`bash ../../scripts/check-update.sh` 调用行、
  `../../rules/durable-context.md` 链接（换成 nmem + shared/knowledge-preflight.md）。
- write（209 行，润色/去AI味/文案）与 design（175 行，UI）**留在 Waza 软链不动**。
- Waza CLAUDE.md 设计规约要点：8 技能硬上限；"需要判断→skill、确定性→script/rule"；
  catalogs consolidate 不 accumulate；RESOLVER 与 description 同步。

## 3. mlbattle-debug 侧事实（工作机部署 + 接口面）

- 聚合层：`setup-skills-link.sh` 幂等把 `.agents/.claude/.codex/skills` 三入口软链到
  `docs/skills`；`docs/skills` 内 = 19 个真实目录（编排/评测/知识类）+ 每技能软链
  （→ `dotnet-runtime/mlbattle-dotnet/.claude/skills` 的 17 个 battle/p4 家族 + bdt 仓）。
  五门接入照抄该模式：mt-skills clone 后每技能软链进 docs/skills。
- P4 worktree 的 `.claude/skills/` 是**真实拷贝子集**（battle-debug、build-compat 等），
  由全局 update-skills-deploy 强制同步 → 复制时必须 `cp -RL` 解引用，否则 shared 断链。
- bdt v1.15.x 顶层命令族：kb / case / kb-check / bug-history / lark-proj / p4 / svn /
  cs / csv / xml / trace / replay / context / desync / codegen / session / dotnet / manifest
  （manifest = 机器可读命令契约 registry，JSON）。
- KB（`mlbattle-kb/data/mlbattle-debug-docs`）：knowledge/ 下 GUIDE + LOADING_PROTOCOL
  （L0 入口）、patterns ×100、reference ×53（+enum 120 / mechanisms 17 / tables 10 /
  flow 8 / decision_cards 6）、postmortem ×12、enum_detail ×733；schemas/ 有
  controlled_vocabulary（tag 命名空间 subsystem/* symptom/* category/*、conclusion_type、
  evidence_strength）。cases 已迁独立项目 mlbattle-debug-cases。
- 审查/排查侧补充知识（check/hunt 按名路由，不复制）：KB `reference/coding_style.md`、
  `code_conventions.md`（含「现象→检查点」映射表）、`architecture_axioms.md`。
- kb-search 双事实源现状：mt-skills 版与项目版并存 → P1 README 声明 mt-skills 为跨项目规范源。
- 盲测隔离：KB 有 blind 分支/profile（battle-debug-eval 切换）；hunt 的 KB 预检在盲测
  环境天然走 blind provider，无需特判。

## 4. nmem 记忆锚点（新会话 `nmem --json m search "<标题关键词>"` 可找回）

本计划决策链三条：
- 「mt-skills 五门技能体系落地决策」（v1）
- 「mt-skills 五门计划 v2 修订要点」（shared 基座 + 先例回灌）
- 「四门+cs-coding：code 门取消决策（v3）」

关键依据记忆（标题）：
- 「Codex skills context budget 2% 警告与降压方案」
- 「技能文件结构与加载规则详解」（称 Codex 忽略 symlink 目录）与
  「Codex 项目级技能支持机制」（称 `.agents/skills` 官方支持软链）——**两条矛盾，
  runtime 兼容矩阵以实测为准**
- 「p4-review / p4-dev skill 误触发修复（disable-model-invocation + description 清理）」
- 「Skill 触发总原则 v2：默认自动触发，操作类才显式」（2026-07-02，**现行原则**；已
  supersede 旧的「Claude Code Skill 显式触发策略与配置规范」与「Brian 偏好：Explicit-only
  skill 触发」两条；「p4-ops Invoke Policy 显式触发策略」在 v2 下仍有效——操作类保持显式）
- 「Skill description 优化原则：只说做什么+何时触发」
- 「Skill(规范/方法论) vs KB(知识) 划界原则」（用户口径）
- 「planning-archive Skill: 解决 planning-with-files 文档膨胀问题」（60k tokens 教训）
- 「mlbattle 周进展飞书文档写作规范」（write-document 周报类型直接内嵌）
- 「向量检索对高密度技术术语文档召回失败实证」（hybrid 优先，沉在 kb-search）
- 「webforage 可访问飞书文档，WebFetch 不行」
- 「Codex hooks 与 Claude Code 的能力差异对比」（仅 SessionStart/Stop）
- 「p4-dev skill 路由边界：动作导向而非业务词导向」

## 5. 执行注意

- 提交纪律：mt-skills 子仓先 commit，agent-cookbook 后更新指针；提交由用户触发
  （commitall skill 已支持子模块顺序），不要主动 commit/push。
- `rules/README.md` 已有 csharp rule → cs-coding-style 折叠先例的表述，P6 更新去向映射时
  保持口径一致。
- RESOLVER.md 当前分区：Planning And Design / Coding (C#) / Debug, Review, And Verification /
  Content And Web / Lark / Git And Ops + Legacy 表；重写时改为 Front Doors + Coding Guides
  起头，其余分区保留。
- 冒烟验收是人工步骤（新开 session 输入触发语句），不要试图脚本化。
