# 中文优先撰写规约

> skill-forge 的核心增量。起草任何 SKILL.md 前先读本文。
> 一句话原则：**默认简体中文；当英文更准、更短、更无歧义时保留英文；绝不硬翻译。**

## 判据一：何时保留英文（原文不译）

| 类别 | 处理 | 例子 |
|---|---|---|
| 代码标识符：字段/命令/文件/函数/路径 | 一律原文 | `name`、`description`、`SKILL.md`、`--max-iterations`、`python -m scripts.run_loop` |
| 产品/项目/工具专名 | 原文 | Claude Code、skill-creator、RESOLVER、nmem、lark-cli |
| 已成行业术语，中文译名混乱或降精度 | 首次「中文（English）」对照，后文择一 | progressive disclosure、frontmatter、token、prompt、eval、baseline、subagent、schema |
| description 里的触发词 | 中英并列（见判据四） | dashboard / 仪表盘、review / 审查 |

## 判据二：何时用中文

- 解释性正文、讲「为什么」、流程叙述、约束/边界说明——中文更亲切精准。
- 面向用户的沟通话术——中文。
- 结构性指令（祈使句）——中文，动词用中文（「先读」「跑」「回填」「拆到」）。

## 判据三：反硬翻译清单（别这么干）

- 别每次都写全称对照。`progressive disclosure` 首次对照一次即可，后文用其一，
  不要每处都写「渐进式披露（progressive disclosure）」。
- 别硬译成生僻中文词。trigger 动词用「触发」，别造「触发器」当动词；
  overfit 直接用英文或「过拟合」，别写「过度拟合化」。
- 别翻译代码/命令里的英文。`--verbose`、`baseline` 作字段名时不译。
- 别中英间距忽有忽无。本仓惯例：中英文之间留一个半角空格，中文段落用全角标点，
  行内 `code` 与代码块内保持原样。

## 判据四：description 的中英触发词覆盖（关键）

description 是唯一触发杠杆，且跨语言匹配（中文 query 命中英文 description）机制
未文档化、不可靠。所以**中英触发词都要显式写进 description**。结构模板：

```
"<中文一句 what+when>。<English what if clearer>。Use whenever the user wants
<中文触发短语列表>、<English trigger phrases>。Not for <中文边界>（走 <邻居 skill>）。"
```

- what + when 同时给；第三人称；pushy——附显式场景词对抗欠触发。
- eval 触发查询也要中英混采，别只测一种语言。

**before → after 示例**（承官方 dashboard 例，中文化）：

- ❌ 弱：`"构建一个展示内部数据的快速仪表盘。"`
- ✅ 强：`"构建展示内部数据的快速仪表盘（fast dashboard）。Use whenever the user
  mentions 仪表盘/数据可视化/内部指标/dashboard/data viz/internal metrics，
  even if they don't literally say 'dashboard'。"`

## 判据五：正文风格（承官方 skill-creator）

- imperative 祈使语气写指令；讲清**为什么**优先于堆全大写 MUST/ALWAYS。
  若发现自己在写死板的 ALWAYS/NEVER，是黄旗——改成解释缘由，让模型理解而非背诵。
- 先写草稿，隔一会用新眼睛重读再改。
- theory of mind：写通用而非绑死具体例子的指令。

## 自检

- [ ] 代码/命令/字段/专名全部原文，没被翻译掉？
- [ ] 术语首次对照、后文不啰嗦？
- [ ] description 中英触发词都覆盖、第三人称、pushy？
- [ ] 中英文间距、标点一致（半角空格 + 中文全角）？
- [ ] 没有为了「显得中文」而硬译降低精度的地方？
