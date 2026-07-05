---
name: <目录名：小写字母/数字/连字符，≤64，禁 anthropic/claude，必须等于目录名>
description: "<中文一句 what+when>。<English what if clearer>。Use whenever the user wants <中文触发短语列表>、<English trigger phrases>。Not for <中文边界>（走 <邻居 skill>）。"
---

# <Skill 名>：<中文副标题>

<一段：这个 skill 让 agent 能做什么、增量在哪、骨架承自哪。默认简体中文，
术语/命令/专名保留英文，别硬翻。>

> **定位**：<这是 authoring / review / debug / 观测 中的哪一类？一句话>

## 这个 skill 不做什么（邻居）

| 意图 | 去哪 |
|---|---|
| <相邻意图 A> | `<邻居 skill A>` |
| <相邻意图 B> | `<邻居 skill B>` |

## 流程

### 1. <阶段名>

<祈使句指令。讲为什么，别堆全大写 MUST。>

### 2. <阶段名>

<...>

## 约束

- <硬约束，讲清缘由>
- <...>

## 边界

- <明确不越界的地方，指向对应的门>

## 参考文件

- `references/<xxx>.md` — <何时该读它>

<!--
起草提示（写完删掉本注释）：
- 正文 < 500 行；逼近就拆到 references/ 并留清晰指针。
- description 中英触发词都覆盖、第三人称、pushy（见 skill-forge/references/zh-authoring.md）。
- 引用官方脚本用 `scripts.xxx` 点号形式或 `skill-creator/scripts/xxx` 前缀，别写裸 `scripts/xxx`。
- 动笔前先过 skill-forge/references/razor.md 的 deletion test。
-->
