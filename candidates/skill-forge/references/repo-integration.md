# 本仓晋级流：candidates → skills

## 为什么先落 candidates/

起草期的 skill 不该激活：不进 RESOLVER、不占常驻预算、不受 verify 约束、不被 agent
误触发。`candidates/` 是「待评估候选区」，区别于 `legacy/`（退休停放）。
verify-skills.sh 只扫 `skills/`，所以 `candidates/` 天然隔离，随便改。

## 晋级检查单（四条全绿才移）

1. **剃刀过关**：`references/razor.md` 的 deletion test 有明确 yes。
2. **评测达标**：≥ 3 场景，with-skill 对 no-skill 有可见增益（benchmark delta 为正）。
3. **用户点头**。
4. **frontmatter 合规**：对照 `references/frontmatter-spec.md`。

## 晋级动作

```bash
# 1. 移入 skills/（own skill 直接 git mv；共享 skill 见下）
git mv candidates/skill-forge skills/skill-forge

# 2. 登记 RESOLVER：在 skills/RESOLVER.md 加一行路由，指向 skills/skill-forge/SKILL.md

# 3. 校验到绿
bash scripts/verify-skills.sh
```

- **own skill**：真实目录，直接进 `skills/`。
- **要跨项目复用的共享 skill**：先放 `mt-skills/`，再在 `skills/` 下建符号链接
  `skills/<name> -> ../../mt-skills/skills/<name>`；改动先在 mt-skills 提交推送，
  再更新父仓指针（见 AGENTS.md 的 Submodules）。
- 漏登记 RESOLVER 报 RESOLVER GAP；name ≠ 目录名报 NAME MISMATCH。

## 官方 skill-creator 脚本定位（复用，不复制）

本机路径（marketplaces 版本号可能变，find 一下最稳）：

```bash
find ~/.claude/plugins -type d -name skill-creator
# 常见：~/.claude/plugins/marketplaces/anthropic-agent-skills/skills/skill-creator/
```

可直接跑的（从 skill-creator 目录内以模块方式运行）：

- `scripts.aggregate_benchmark` — 聚合 with/without 基准（mean ± stddev + delta）
- `scripts.run_loop` — description 触发优化环（≤ 5 轮，按 held-out test 分选最优）
- `scripts.package_skill` — 打成 `.skill` zip
- `eval-viewer/generate_review.py` — 评审 UI（headless 用 `--static` 出静态 HTML）
- `agents/grader.md` — grader 子 agent 评分规范
- `references/schemas.md` — evals.json / grading.json / benchmark.json 的完整 schema

> 不把这套脚本复制进本仓——复制 = 维护双份，违背剃。指向官方即可。

## 纯人评降级回路（官方脚本不可用时）

无 subagent / 无浏览器时：逐个读候选 skill 的 SKILL.md，自己跑测试 prompt，在对话里
直接展示 prompt + 输出，问用户「这样对吗、想改啥」。跳过定量基准，只做定性反馈——
够用作 sanity check，人评步骤本身能补上严谨性。

## 打包分发（可选）

跨机分发才需要：从 skill-creator 目录跑 `python -m scripts.package_skill <候选 skill 目录>`
→ 得到 `<name>.skill`，把路径给用户安装。
