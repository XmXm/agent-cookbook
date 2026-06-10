---
name: lark-architecture
description: |
  把架构图画进飞书画板（lark 画板 / whiteboard）——分层架构、微服务、前后端、云/网络拓扑、安全边界，
  产出的是画板里**可编辑的原生节点**，不是截图。**默认浅色**（适配飞书浅色文档，深色图嵌进文档会显得太重），
  也支持暗色。复用 architecture-diagram 的设计系统（语义配色、圆角组件盒、图例规则），但把 SVG 改造到画板能
  解析的子集（去掉 pattern/filter/渐变，箭头用 polygon，连线用正交折线）。
  Use when the user says 画架构图到飞书/飞书画板架构图/把架构图放进画板/lark 架构图/feishu architecture whiteboard,
  或给了飞书文档/画板 URL 并要在里面画系统架构、拓扑、分层图。
  不处理纯本地 HTML 架构图（那是 architecture-diagram），也不处理思维导图/时序图/流程图（那走 lark-whiteboard 的 mermaid 路由）。
compatibility: |
  Requires: lark-cli (>=1.0.x), Node.js (`npx -y @larksuite/whiteboard-cli@^0.2.11`).
  Auth: `lark-cli auth login`（user 模式）需在写入飞书前完成。
  画板与文档操作沿用 lark-doc / lark-whiteboard 的约定（v2 API、相对 @file 路径）。
metadata:
  requires:
    bins: ["lark-cli"]
---

# lark-architecture

把架构图画成**飞书画板里的原生可编辑节点**。心法一句话：
**用 [architecture-diagram](../architecture-diagram/architecture-diagram/SKILL.md) 的设计系统，走 `lark-whiteboard` 的 SVG 路由，按 [lark-doc](../lark-doc/SKILL.md) 的资源块规则写进飞书。** 默认浅色配色（飞书文档是浅底，深色图嵌进去太重）；用户明确要暗色再切暗色。

为什么需要单独一个 skill：`architecture-diagram` 产出的是自包含 HTML（内嵌 `<pattern>` 网格、`<filter>` 辉光、html2canvas 导出工具栏），这些**画板的 svg-parser 完全不支持**，直接塞进画板会渲染崩坏。本 skill 把那套设计语言**改造**到画板能吃下的 SVG 子集，并把配色调成**适配飞书浅色文档**，同时让节点保持可编辑。

---

## 不变量（违反任何一条就停下重做）

1. **画板 SVG 禁用装饰特性**：`<pattern>` / `<filter>` / `<radialGradient>` / `<linearGradient>` / `<clipPath>` / `<mask>` 一律不用。用了会导致画板渲染问题（不是降级成图片，是直接坏）。
2. **文字只用 `<text>` / `<tspan>`**，不要用 `<path>` 描字。画板硬编码 Noto Sans SC，`font-family` 写了也没用——**靠 `font-size` / `font-weight` 建立层级**，不要依赖字体。
3. **箭头用 `<polygon>` 小三角**，不要用 `<marker>`（不在可识别元素里）。**连线用正交折线 `<polyline>`**（带水平/垂直折点），不要斜线。
4. **变换**只用 `translate` / `rotate` / `scale`；`skewX` / `skewY` / `matrix(...)` 会被降级，别用。
5. **SVG 必须完整自包含**：有 `<svg>` 根节点和 `viewBox`，不引用外部图片/字体/脚本/远程资源。
6. **写飞书全程 v2**：`docs +create/+update/+fetch` 必带 `--api-version v2`；`--content @file` 的 `@file` 必须是**相对当前目录**的路径（先 `cd` 过去）。
7. **不留空白占位画板**：只有 `<whiteboard type="blank">` 而没把内容写进去，视为任务未完成。
8. **交付前必须本地渲染过 `--check` + 看过 PNG**，不要把没渲染过的 SVG 直接写进飞书。

---

## 设计系统：architecture-diagram → 画板 的改造对照

完整配色/排版/间距规则见 [architecture-diagram](../architecture-diagram/architecture-diagram/SKILL.md)。**保留**语义配色、圆角组件盒（标题+副标签）、消息总线橙色连接件、虚线安全组/区域边界、图例放在所有边界之外、垂直层间至少 40px 间隙这些规则。**改造**部分如下：

| architecture-diagram（HTML+SVG） | lark-architecture（画板 SVG） |
|---|---|
| `<pattern>` 网格背景 | 去掉，只铺一张纯色 `<rect>` 打底（默认浅色 `#ffffff`，暗色用 `#020617`） |
| `<marker>` 箭头 | 在连线末端画 `<polygon>` 小三角 |
| `<filter>` 辉光 / 阴影 | 去掉，靠 stroke 颜色和对比建立重点 |
| `<radialGradient>` / `<linearGradient>` | 去掉，改用纯色或 `rgba(...)` 半透明填充 |
| 不透明 rect 打底 + 半透明 rect 盖住穿过的箭头 | 不需要——连线走层间空隙即可；底色本身不透明 |
| html2canvas / jsPDF 导出工具栏 | 去掉，导出走 whiteboard-cli / lark-cli |
| JetBrains Mono（Google Fonts） | 去掉 font-family，画板只有 Noto Sans SC，用字号/字重分级 |
| `<foreignObject>` | 去掉，文字一律 `<text>` |
| 斜直线连接 | 正交折线 `<polyline>`（水平/垂直折点） |

**语义配色表 · 浅色（默认）** —— 飞书文档是浅色背景，深色图嵌进去像一块黑砖，所以默认走浅色：白底、浅色块、彩色描边、深色文字。

| 组件类型 | 填充 | 描边 | 文字 |
|---|---|---|---|
| Frontend 前端 | `#ecfeff` | `#0891b2` | 标题 `#0f172a` / 副标签 `#64748b` |
| Backend 后端 | `#ecfdf5` | `#059669` | 同上 |
| Database 存储 | `#f5f3ff` | `#7c3aed` | 同上 |
| Gateway 网关/通用 | `#f1f5f9` | `#64748b` | 同上 |
| Security 安全组 | `#fef2f4`（虚线边框） | `#e11d48` | 标签 `#e11d48` |
| Message Bus 消息总线 | `#fff7ed` | `#ea580c` | `#c2410c` |

标题/层标签用 `#0f172a`（深色，浅底上对比足），副标签用 `#64748b`；连线箭头用 `#94a3b8`。直接抄 [resources/template.svg](resources/template.svg)。

**语义配色表 · 暗色（可选）** —— 仅当用户明确要暗色，或图要放进深色场景时用。底色 `#020617`，半透明色块 + 亮色描边。

| 组件类型 | 填充（rgba） | 描边 |
|---|---|---|
| Frontend 前端 | `rgba(8,51,68,0.55)` | `#22d3ee` |
| Backend 后端 | `rgba(6,78,59,0.55)` | `#34d399` |
| Database 存储 | `rgba(76,29,149,0.55)` | `#a78bfa` |
| Cloud 云 | `rgba(120,53,15,0.4)` | `#fbbf24` |
| Security 安全组 | `none`（虚线边框） | `#fb7185` |
| Message Bus 消息总线 | `rgba(251,146,60,0.3)` | `#fb923c` |
| External 通用 | `rgba(30,41,59,0.6)` | `#94a3b8` |

> **对比度（实测）**：暗色图在飞书渲染器里，偏暗的近白色（如 `#e2e8f0`）会发灰、对比不足。暗色方案的**主标题/重点文字一律用 `#ffffff`**，`#94a3b8`/`#64748b` 只留给副标签。暗色起手模板见 [resources/template-dark.svg](resources/template-dark.svg)。

组件盒骨架（圆角 `rx=6`、标题 `font-size=14 font-weight=600`、副标签 `font-size=11`）和正交连线 + 三角箭头的写法，两套模板通用，只是配色不同。

---

## 构图经验（信息流/搜索原理/产品视角图）

除分层架构外，画板也常用于**产品向的流程/原理图**（如搜索原理、数据流向、功能架构概览）。这类图的要点：

### 尺寸与紧凑度

- viewBox 宽度 680–780，高度尽量 ≤ 350。画板在飞书文档中按比例撑满宽度，过大的高度会让页面显得空洞。
- 元素之间垂直间距 16–24px 即可，不需要架构图的 40px 层间距。
- 每个框的高度严格匹配内容行数，**不留空白行**——同一排框内容行数不一致时，高度对齐到最多行的框，其余框补内容而非留白。

### 文字排版

- 产品图字号比架构图稍大：标题 12–13px，正文 10.5–11px。
- **不用 `|` 竖线分隔**——渲染后辨识度低、视觉噪音大。改用中文顿号、逗号或分行。
- 框内文字左起点 = 框 x + 14px，确保不贴边。行间距 17–18px。
- 描述文字分两层色彩：首行 `#1F2329`（标题级），后续行 `#646A73`（辅助级）。

### 起始节点

- 产品图不需要抽象标题（如"知识库搜索原理"）——直接用**动作化表达**作为入口，如搜索框 `搜索"鲁班七号二技能没伤害"`。
- 搜索框样式：大圆角 `rx≥18`、蓝色描边、蓝色加粗文字，一眼读懂是用户输入。

### 多列并排框

- 三列框间距 12–16px，宽度可以不等（内容多的框宽一些）但同排高度必须相同。
- 框头用浅色填充条（`opacity=0.06`）承载分类标题，视觉分层不靠加线。
- 三列之间的汇聚/扇出箭头用斜线（非正交折线），产品图追求简洁而非工程精确。

### 底部输出

- 最终输出框用主色（蓝色）浅底 + 描边 + 加粗文字，与顶部搜索框呼应形成闭环。
- 高度紧贴文字（24–36px），不要和中间的知识框一样高。

---

## Workflow

### Step 0 — Sanity check

```bash
lark-cli --version
npx -y @larksuite/whiteboard-cli@^0.2.11 -v
lark-cli auth status >/dev/null   # 写飞书前必须已 lark-cli auth login（user 模式）
```

### Step 1 — 设计并写 SVG

- 先想清楚信息结构：有明确上下层级 → 分层条带；多模块平级网状 → 岛屿式。
- 拷 [resources/template.svg](resources/template.svg)（浅色，默认）起手，按语义配色和组件盒骨架替换内容；用户要暗色就拷 [resources/template-dark.svg](resources/template-dark.svg)。**严格遵守不变量 1–5。**
- 产物目录：`./diagrams/YYYY-MM-DDTHHMMSS/`，文件名固定 `diagram.svg`（与 `lark-whiteboard` 的产物规范一致）。

### Step 2 — 本地渲染审查（不可跳过）

```bash
DIR=./diagrams/$(date +%Y-%m-%dT%H%M%S); mkdir -p "$DIR"   # 把 diagram.svg 放进去
npx -y @larksuite/whiteboard-cli@^0.2.11 -i "$DIR/diagram.svg" -f svg --check       # 几何自检
npx -y @larksuite/whiteboard-cli@^0.2.11 -i "$DIR/diagram.svg" -o "$DIR/diagram.png" -f svg   # 出图，肉眼看
```

`--check` 读法：
- **`text-overflow` error → 必须修**（容器太窄/字太多）。
- **`node-overlap` warn**：区分两种——安全组/区域边界**故意包住**内部节点会报 100% 包含的 warn，这是**正常的**，忽略；若是两个本不该叠的盒子互相压住，要修。
- 然后**一定看 PNG**：文字溢出、元素错位、整体崩坏要回 Step 1 改。

> **硬兜底**：渲染命令直接语法级报错，或两轮改写仍消不掉 `text-overflow` error，或 PNG 目测严重崩坏 → **别逐行修 SVG**，丢掉改走 DSL：读 `lark-whiteboard` 的 `routes/dsl.md` + `scenes/architecture.md` 用 DSL 从零重画（DSL 有自动布局引擎，结构稳）。

### Step 3 — 写进飞书（按场景二选一）

**场景 A：作为新画板块插入文档**（用户给了文档 URL，或要新建文档）

把 SVG 包进 `<whiteboard type="svg">` 资源块，作为 XML 正文写入。**资源块的精确语法先读 [lark-doc 的 lark-doc-xml.md](../lark-doc/references/lark-doc-xml.md) 的「资源块」章节**；整体调度逻辑见 [lark-doc 的 lark-doc-whiteboard.md](../lark-doc/references/lark-doc-whiteboard.md)。

```bash
cd "$DIR"                       # @file 必须相对当前目录
# doc.xml 内容形如： <whiteboard type="svg"><svg ...>...完整 SVG...</svg></whiteboard>
# 追加到已有文档：
lark-cli docs +update --api-version v2 --doc "<doc-url-or-token>" \
  --command append --content @doc.xml --as user
# 或新建文档（XML 正文里再带 <title>/<p> 等）：
lark-cli docs +create --api-version v2 --content @doc.xml --as user
```

> 这里 `--content` 走 **XML（默认）**，不要传 `--doc-format markdown`。需要精确落点（插在某个 block 后）时改用 `--command block_insert_after --block-id <id>`，参数见 lark-doc。

**场景 B：写进一块已存在的画板**（已知 `board_token`，如 `wbcnXXX`）

导出 OpenAPI 节点再写入（沿用 `lark-whiteboard` 的渲染&写入流程）：

```bash
npx -y @larksuite/whiteboard-cli@^0.2.11 -i "$DIR/diagram.svg" -f svg --to openapi --format json \
  | lark-cli whiteboard +update \
      --whiteboard-token "<board_token>" \
      --source - --input_format raw \
      --idempotent-token "$(date +%s)-arch-1" \
      --as user \
      --overwrite
```

> `--overwrite` 是**整体覆盖**该画板。画板已有内容时，不带 `--overwrite` 是增量叠加，可能和旧内容重叠——整图重绘就带上它。`--idempotent-token` ≥10 字符，避免重试重复写入。
> board_token 从哪来：用户直接给 / `docs +fetch --api-version v2` 从文档里取 `<whiteboard token="...">` / 先 `docs +update --command append --content '<whiteboard type="blank"></whiteboard>'` 建空白块再从响应 `new_blocks` 取——细节见 `lark-whiteboard` SKILL.md。

### Step 4 — 验证（汇报前最后一关）

- **场景 A**：`lark-cli docs +fetch --api-version v2 --doc "<doc>" --as user` 确认正文里有 `<whiteboard ...>` 块、数量对得上。
- **场景 B**：导出画板预览图肉眼复核：
  ```bash
  lark-cli whiteboard +query --whiteboard-token "<board_token>" --output_as image --output "$DIR/verify.png" --as user
  ```
- 不满意 → 改 SVG 回 Step 2，再覆盖写入（场景 B 用 `--overwrite`；场景 A 删旧块重插或切 `lark-whiteboard` 编辑）。

### Step 5 — 汇总输出

向用户报告：文档/画板 URL、画板数量、本地产物路径（`$DIR/diagram.svg` + `diagram.png`）、若降级到 DSL 要显式说明。

---

## 触发场景速查

| 用户说 | 怎么走 |
|---|---|
| "把这个系统架构画进飞书画板" | 全流程，场景 A |
| 给了飞书文档 URL + "在里面画个架构图" | Step 0→1→2→3A→4 |
| "这块画板（wbcnXXX）重画成架构图" | Step 0→1→2→3B（带 `--overwrite`）→4 |
| "架构图先在本地看看效果" | Step 0→1→2，交付 PNG，不写飞书 |
| 要思维导图/时序图/流程图/类图/饼图/甘特图 | 不归本 skill，走 `lark-whiteboard` 的 `routes/mermaid.md` |
| 只要本地暗色 HTML 架构图，不进飞书 | 不归本 skill，用 [architecture-diagram](../architecture-diagram/architecture-diagram/SKILL.md) |

## 不在本 skill 范围

- **本地 HTML 架构图**（带导出工具栏、网格、辉光）：用 [architecture-diagram](../architecture-diagram/architecture-diagram/SKILL.md)。
- **mermaid 类图表**（思维导图/时序图/类图/饼图/甘特图）：走 `lark-whiteboard` 的 mermaid 路由。
- **整篇 markdown（含 mermaid）导入飞书并建画板**：用 `markdown-to-lark-doc`。
- **复杂自动布局**：SVG 两轮搞不定就转 `lark-whiteboard` 的 DSL 路由（`routes/dsl.md` + `scenes/architecture.md`）。

## 参考

- [architecture-diagram](../architecture-diagram/architecture-diagram/SKILL.md) — 设计系统的源头（配色、排版、间距、图例规则）
- [lark-doc 的 lark-doc-whiteboard.md](../lark-doc/references/lark-doc-whiteboard.md) — 文档里插画板的调度与 SVG 设计指南
- [lark-doc 的 lark-doc-xml.md](../lark-doc/references/lark-doc-xml.md) — `<whiteboard type="svg">` 资源块精确语法
- `lark-whiteboard` skill — SVG/DSL/Mermaid 路由、`--check` 渲染审查、`whiteboard +update` 写入、DSL 兜底
- [resources/template.svg](resources/template.svg) — 画板安全的架构图起手模板（浅色，默认）
- [resources/template-dark.svg](resources/template-dark.svg) — 暗色变体起手模板
