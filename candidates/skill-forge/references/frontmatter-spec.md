# frontmatter 硬约束速查

> 官方规范 + 本仓 verify-skills.sh 契约。起草与晋级前对照。

## 两个必填字段

只有 `name` 和 `description` 必填。其余（`allowed-tools`、`license`、`metadata`）
可选、罕用。SKILL.md 必须以 `---` 开头、有闭合 `---`。

## name

- ≤ 64 字符
- 只能小写字母、数字、连字符 `-`
- 禁 XML 标签
- 禁保留词 `anthropic`、`claude`
- **必须等于目录名**（verify 强校验，不符报 NAME MISMATCH）

## description

- 非空
- ≤ 1024 字符
- 禁 XML 标签
- 是唯一触发杠杆：第三人称、what + when、具体触发词、刻意 pushy 对抗欠触发
- 中文优先 skill 要中英触发词都覆盖（见 `references/zh-authoring.md` 判据四）

## 本仓额外契约（verify-skills.sh 会挂的点）

- name == 目录名；无重复 name；符号链接不能断。
- 每个 active skill 必须在 `RESOLVER.md` 里有一行 `skills/<name>/SKILL.md`（漏则 RESOLVER GAP）。
- 正文里 `references/…`、`agents/…`、`scripts/…` 的相对提及必须指向真实文件（否则 BROKEN REFERENCE）。
- 相对 Markdown 链接（方括号文字 + 圆括号相对路径）的目标必须真实存在；本仓惯例是
  直接用反引号包路径，避免触发这条链接校验（本文正是这么做的）。
- 表格行不能有未转义的 `|`——cell 内的 `|` 用反引号包起来或转义。

## 值预算（soft，别当硬数字）

- Level 2 的 SKILL.md：`< 500 行` / `< 5k token`。官方自己给了多种说法（行/token/词），
  当软指导。逼近上限 → 拆到 `references/` 并留清晰指针。
- 大 reference（> 300 行）加个目录（TOC）。

## 一个本仓特有陷阱

SKILL.md 里引用**官方**脚本时，别写裸 `scripts/xxx`——verify 的正则会把它当成
**本 skill 的本地文件**去校验，报 BROKEN REFERENCE。规避：

- 引用官方脚本：用点号模块形式 `scripts.run_loop`，或加前缀 `skill-creator/scripts/run_loop.py`。
- 引用仓根脚本：写不带 `scripts/` 前缀的文件名，如「仓根 `verify-skills.sh`」。
- 只有**本 skill 自己真实存在**的文件才写裸 `references/xxx.md`。
