# 门·证·环·剃：skill 的 deletion test

> ⚠️ **本文是本仓方法论**（`AGENTS.md` / `METHODOLOGY.md` 的门·证·环·剃），
> **不是 Anthropic 官方规范**。官方最接近的代偿是 eval-driven development——
> 「skill 应解决真问题，而非记录臆想的问题」。用它时明确这是本仓取向。

## 剃（Razor）：核心问题

一个 skill 只在「**删掉它会让一个现代 agent 可度量地变差**」时才该存在。
动笔写任何新 skill 前先答这一问；答不上来 → 不建。

## deletion test 判据

| 该建（yes） | 别建（no） |
|---|---|
| 有稳定重复的流程，值得固化成骨架/脚本 | 一次性任务，做完即弃 |
| 领域专有知识，模型裸答会错或缺 | 只是把通用常识抄成文档 |
| 确定性脚本能消除每次重造轮子 | 模型裸答已够好（**先跑无 skill 基线验证！**） |
| 触发 + 约束能显著提质，且证据可测 | 与现有 skill 重叠（先扩现有那个） |

## 建 skill 时逐条过四支柱

- **门（Doors）**：这是不是一个清晰入口？写清了它 NOT for 什么、邻居是谁吗？
  每个 skill 都要声明自己不做什么并指向邻居。
- **证（Evidence）**：价值有 eval 证据吗？先建 ≥3 场景 + 无 skill 基线，用 benchmark
  delta 说话，别凭感觉。
- **环（Loop）**：要不要接 knowledge preflight（nmem + KB）？关键结论要不要写回 nmem
  让下次自动捞出？飞轮两端都要有。
- **剃（Razor）**：见下方预算检查。

## Codex 2% 上下文预算检查

每个 active skill 的 `name` + `description` 常驻系统提示，占固定预算。装了 N 个 skill，
预算就被摊薄 N 份。新增一个前问：

> 它的**触发收益** > 它占的**常驻预算**吗？

边际不明显就别急着进 `skills/`——留在 `candidates/` 观察，攒够证据再晋级。

## 过不了剃刀怎么办

把 deletion test 的结论讲给用户：为什么不该建、或该并进哪个现有 skill、或先留
candidates 观察。**然后停手。**

挡住一个不该存在的 skill，比多造一个更有价值——这本身就是 skill-forge 的合格产出，
不是失败。别为了产出而产出。
