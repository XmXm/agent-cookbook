---
name: skill-usage-report
description: "月度 skill 用量观测与 nmem 月报写回：跑 transcript 统计、环比上月、抽查漏触发/误触发、按模板把结论写回 nmem。Use whenever the user asks to 跑月度 skill stats、用量月报、skill 用量观测、前门渗透率、看看 skill 触发情况、monthly skill usage report, or mentions checking how often skills or front doors actually trigger. Not for skill contract checking (verify-skills.sh), and not for battle-debug eval scoring."
---

# Skill Usage Report: 月度用量观测与月报写回

为「泛名路由可靠性」这一体系最脆假设建立持续观测。脚本只建观测面
（确定性部分），漏触发/误触发的判定才是本 skill 的核心工作（判断部分），
结论按模板环比写回 nmem，让下个月的 knowledge preflight 自动捞出对照。

## 流程（四步，约 10 分钟）

### 1. 取对照

`nmem --json m search "skill 用量月报"`，取最近一份月报。首月对照基线
（2026-07-03）：527 sessions / 52 触发 skill / 8 进前门，write-document
与 cs-coding 零调用。

### 2. 跑观测

```bash
python3 scripts/skill-usage-stats.py --days 30
```

脚本在本 skill 的 scripts/ 下：stdlib、只读，扫描 `~/.claude/projects/`
全部 Claude Code transcript，输出各 skill 调用量、前门覆盖的原始计数
（渗透率 = 进前门 sessions / 总 sessions，写月报时自算）、按项目分布。

### 3. 抽查判定（核心判断步）

从数字里找可疑面，挑 2-3 个 session 读 transcript，判定要引 session
文件路径和具体证据，不凭印象：

- **漏触发**：该触发没触发。重点盯上月零调用或长期低频的门，找一个明显
  该进门的 session，看模型当时为什么裸答（description 缺触发词？ask 太短
  不值得进门？被邻近 skill 截胡？）。
- **误触发**：不该触发却触发。看进门的 session 里 skill 是否真的贡献了
  约束或结构，还是只是加载了一页没人用的规范。

### 4. 写回 nmem

标题带一句话结论；正文五段缺一不可，行动项没有动作也要显式写"无行动"：

```bash
nmem m add "skill 用量月报 YYYY-MM（skill-usage-stats.py --days 30）：
总量：N sessions / M 触发（x%）/ K 进前门（y%），环比上月 ±…。
前门明细：plan a、check b、hunt c、write-document d、cs-coding e。
解读：<零调用项、异常波动、新改造 skill 的首月表现>。
抽查：<session 级漏触发/误触发判定与证据>。
行动项：<改 description 触发词 / 合并 / 降级 / 明确无行动>。" \
  -t "skill 用量月报 YYYY-MM：<一句话结论>" -i 0.7
```

常规月报 importance 0.7；重大发现（某门连续两月零调用、渗透率腰斩）调到
0.85 以上。

## 约束

- **行动项强制收尾**。观测不产生行动就是仪式；行动项通常是改某个 skill
  的 description 触发词、合并入口或降级，落实后下月验证效果。
- **deletion test 适用于本流程自身**：连续 2-3 个月产不出有效结论，
  砍掉本 skill。
- **先手动后自动**：想挂定时任务前，先手动验证两三个月的价值（lazy 阶梯）。
- **未覆盖面照实报**：Codex sessions 不在统计内；路由质量判定是抽查
  不是全量，报告里不得把抽查结论写成总体结论。

## 边界

- skill 合同校验（frontmatter、RESOLVER 覆盖、链接完整性）走仓根的
  verify-skills.sh，不归本 skill。
- battle-debug 排查能力的评分走 `/battle-debug-eval` 家族，不归本 skill。
