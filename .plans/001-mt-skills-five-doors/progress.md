# progress.md — 阶段状态

> 防膨胀纪律：本文件滚动摘要；phase 完成后折叠成一行结论。

- 计划状态：**P1–P6 已完成**（2026-07-02）；P7 取消（不再需要，见下）。
- 计划版本：v3.2。
- Phase 进度：
  - P1 ✅ — shared 基座五文件建齐 + plan 迁入 mt-skills + 退役 12 项 + RESOLVER 重写 + mt-skills README + runtime 矩阵首测（Claude Code 全通过，Codex 用户级仅 chronicle，无项目级入口）。
  - P2 ✅ — cs-coding-style → cs-coding 改名 + shared 软链 + agent-constraints 引用 + `.claude/rules` 措辞解耦 + 写后出口。
  - P3 ✅ — check fork 自 Waza，剥离 GitHub 特化，新增知识预检 / diff 来源路由 / 审查基线引 shared，≈210 行。
  - P4 ✅ — hunt fork 自 Waza，剥离 update-check / durable-context / rendering-debug / ime-unicode，新增知识预检 / 项目路由 / 修后回写提示，≈190 行。
  - P5 ✅ — write-document 新建，6 种文档类型路由 + 周报结构内嵌 + mermaid `<br/>` 规范 + prose floor。
  - P6 ✅ — `~/.claude/rules` 已删；`rules/` 已移入 `legacy/rules/`（含退役声明 + 去向映射）；AGENTS.md 已更新（Layout 图、Front Doors 节、Rules 退役说明）；全仓无 `.claude/rules` 残留引用。
  - P7 ✖ 不再需要 — mt-skills 技能已通过 agent-cookbook/skills/ 软链全局生效，工作机用同一套 agent-cookbook 入口即可；`cp -RL` 物化是 update-skills-deploy 既有行为，不需要本计划额外动作；P1 矩阵首测已确认 Claude Code 全通。
- Active skills: 35（净 -11，计划完结时快照；2026-07-03 后续变更后为 38）。verify-skills.sh 全绿。
- 计划完结。下一步：用户触发 commitall。
