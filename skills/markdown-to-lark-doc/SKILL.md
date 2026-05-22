---
name: markdown-to-lark-doc
description: |
  整篇本地 .md 文件导入飞书云文档（图文并茂），自动把 ```mermaid 围栏块转成飞书画板。
  Use when the user says "md 推到飞书"、"导入 lark-doc"、"markdown 转飞书文档"、
  "把这个 md 同步成飞书"、"mermaid 转画板"、"markdown-to-lark-doc"、"sync md to feishu"，
  或刚写完一篇含 mermaid 的 markdown 并提到飞书 / 云文档 / 知识库 / wiki。
  覆盖新建文档、向已有 doc 追加、全文替换已有 doc 三种模式，全程使用 lark-cli docs v2 API。
compatibility: |
  Requires: lark-cli (v2 skill installed; run `lark-cli update` if you see v1 deprecation warnings),
  Node.js (`npx -y @larksuite/whiteboard-cli@^0.2.11`), Python 3.8+ for the bundled scripts.
  Auth: `lark-cli auth login` (user mode) before first run.
---

# markdown-to-lark-doc

把一篇本地 `.md` 文件**整篇**推到飞书云文档（Docx），其中 ` ```mermaid ` 围栏代码块自动**转成飞书画板**，其余 markdown 元素（标题、列表、表格、`![](https://...)` 网络图片）按 lark-cli v2 的 Markdown 渲染直接生效。

> **不变量**（贯穿全流程，违反任何一条都停下）
> 1. 所有 `docs +*` 命令必须带 `--api-version v2`；缺了就会撞 v1 deprecation。
> 2. 目标 doc token 必须匹配 `^docx[A-Za-z0-9]{15,}$`；URL 形式自动剥 `/docx/<TOKEN>` 段。
> 3. 已写过内容的画板二次写入前必须 `--overwrite --dry-run` 探测一次，看到 `XX whiteboard nodes will be deleted` 必须先向用户确认。
> 4. `--idempotent-token` ≥10 字符，格式 `<unix>-<basename>-<idx>`，避免重试导致重复写入。
> 5. **本 skill 不处理本地图片自动上传** —— `![](./local.png)` 这种死链会留在文档中。需要本地图片时请提示用户用 `docs +media-insert` 手工补，或预先把图传到图床改成 https URL。

---

## Workflow（6 步）

### Step 0 — Sanity check

```bash
lark-cli --version              # 期望 ≥ 1.0.32
npx -y @larksuite/whiteboard-cli@^0.2.11 -v
```

确认两个都能跑。`lark-cli` 提示 "lark-doc skill is not v2" 时先 `lark-cli update` 再继续。

### Step 1 — 抽出 mermaid，生成占位 md

```bash
python3 scripts/extract_mermaid.py <file.md>
# → 产出 <file>.processed.md  + <file>.mermaid_blocks.json
```

脚本会把每段 ` ```mermaid ... ``` ` 围栏替换为单行：

```html
<whiteboard type="blank" data-mmd-id="N"></whiteboard>
```

其余 markdown 内容原样保留（标题、列表、表格、`![](https://...)`、行内代码等）。

> `<whiteboard>` 是 lark-doc-xml.md 第 18 行确认的合法 block 类型，在 `--doc-format markdown` 模式下也会被解析为画板占位（不会按字面量输出）。

### Step 2 — 决定新建 vs 追加 vs 全文替换

| 用户意图 | 命令 | 说明 |
|---|---|---|
| 用 md 新建文档 | `docs +create` | 默认放入个人 wiki |
| 把 md 追加到已有文档末尾 | `docs +update --mode append` | 保留原文，尾部追加 |
| 用 md **全文替换**已有文档 | `docs +update --mode replace_all` | 清空原文，整篇覆盖 |

**默认创建位置**：新建时一律加 `--wiki-space my_library`，文档创建在个人知识库（wiki/）下。仅当用户明确说"放云盘"、"放我的空间"、"不要放 wiki" 时才省略此参数（此时文档落入云空间根目录）。如果用户指定了 `--wiki-node` 或 `--folder-token`，以用户指定为准。

**全文替换注意事项**：
- `--mode replace_all` 会**删除**目标文档的全部现有内容（包括画板），再写入新内容。
- 执行前必须向用户确认："将清空文档 `<token>` 的全部内容并重新写入，是否继续？"
- 全文替换后，文档 URL 不变，历史版本可在飞书版本记录中找回。

**Step 1 标题处理**：`docs +create --markdown @file` 会从首行 `# Title` 自动提取标题。如果 md 没有 H1，用文件名（去扩展名）作为标题；标题不要在 `--content` 中重复出现。

### Step 3 — 写入文档

```bash
# 新建（默认放入个人 wiki）
lark-cli docs +create \
  --api-version v2 \
  --wiki-space my_library \
  --markdown @<file>.processed.md \
  --as user \
  > create_resp.json

# 追加到已有 doc
lark-cli docs +update \
  --api-version v2 \
  --doc <docx-token-or-url> \
  --mode append \
  --markdown @<file>.processed.md \
  --as user \
  > update_resp.json

# 全文替换已有 doc（用户确认后执行）
lark-cli docs +update \
  --api-version v2 \
  --doc <docx-token-or-url> \
  --mode replace_all \
  --markdown @<file>.processed.md \
  --as user \
  > update_resp.json
```

> 用 `@<path>` 文件传参，避免 shell 转义；不要把 md 内容直接拼进命令行。

从响应里提取 `data.document.url` 报告给用户（即使后续画板填充失败，至少文档已建好）。

### Step 4 — 对齐 placeholder ↔ board_token

```bash
python3 scripts/stitch_boards.py \
  --blocks <file>.mermaid_blocks.json \
  --response create_resp.json \
  > stitched.json
```

脚本：
- 从响应里过滤出 `data.document.new_blocks[]` 中 `block_type == "whiteboard"` 的项；
- **按顺序**与 `mermaid_blocks.json` 的 placeholder 对齐（v2 服务端保证 new_blocks 顺序与 markdown 中出现顺序一致）；
- 数量不一致直接退码 != 0，stderr 报错，让 agent 中止并报告用户。

输出 `stitched.json` 是数组：

```json
[
  {"mmd_id": 0, "code": "sequenceDiagram\n...", "board_token": "wbcn...", "idempotent_token": "1747600000-demo-0"},
  ...
]
```

### Step 5 — 逐个写入画板

对 `stitched.json` 的每一条：

```bash
# 5a. 先把代码写本地临时文件
echo "$CODE" > /tmp/mmd-$N.mmd

# 5b. 渲染预览（可选但推荐，做语法门）
npx -y @larksuite/whiteboard-cli@^0.2.11 -i /tmp/mmd-$N.mmd -o /tmp/mmd-$N.png

# 5c. 转 OpenAPI 并 pipe 给 lark-cli
npx -y @larksuite/whiteboard-cli@^0.2.11 -i /tmp/mmd-$N.mmd --to openapi --format json \
  | lark-cli whiteboard +update \
      --whiteboard-token $TOKEN \
      --source - --input_format raw \
      --idempotent-token $IDEMPOTENT \
      --as user
```

**如果 board 是空白新建的占位（本流水线的正常情况）**：不需要 `--overwrite`，直接写入即可。
**如果用户指定的是已经有内容的画板**：必须先加 `--overwrite --dry-run` 探测；看到 "`XX whiteboard nodes will be deleted`" 时必须先问用户确认，再去掉 `--dry-run`。

### Step 6 — 渲染失败时的 fallback

按 `references/mermaid-fallback.md` 三档兜底：

1. **`whiteboard-cli --check` 报错或渲染崩溃** → 用 `docs +update --command block_replace --block-id <bid> --content '<code language="mermaid">…</code>'` 把占位换回 mermaid 代码块（飞书可识别 mermaid 代码块）；
2. **mermaid 类型不在适用集**（思维导图/时序图/类图/饼图/甘特图，引自 `lark-whiteboard/routes/mermaid.md`）→ 同 1；
3. **以上都失败** → `whiteboard-cli -i x.mmd -o x.png` 转 PNG，再 `docs +media-insert --file x.png` 补回，并在汇报里**显式标注"已降级到 PNG"**。

### Step 7 — 汇总输出

向用户报告：

```
✓ Doc: https://<host>.feishu.cn/docx/<token>
✓ Boards: N / M 成功（M 是总数）
  - mmd_id=0  wbcn...  sequenceDiagram   ✓
  - mmd_id=1  wbcn...  mindmap            ✓ (fallback: code-block)
  ...
```

---

## 触发场景速查

| 用户说 | 直接进 |
|---|---|
| "把 docs/notes.md 推到飞书" | Step 0 → 1 → 2 (create, wiki) |
| "用这个 md 新建一篇飞书文档" | 同上 |
| "把这个 md 追加到 https://xxx.feishu.cn/docx/doxabc..." | Step 0 → 1 → 2 (update append) |
| "用这个 md 覆盖/替换 https://xxx.feishu.cn/docx/doxabc..." | Step 0 → 1 → 2 (update replace_all)，需确认 |
| "同步 md 到飞书（已有文档链接）" | 等同全文替换，需确认后执行 |
| "我的 markdown 里有 mermaid，导入飞书时画板也要建好" | 全流程 |
| "放到云盘 / 我的空间，不要 wiki" | create 时省略 `--wiki-space` |
| 单纯 "把 mermaid 写到画板里" | 跳到 Step 5（用户给 board_token + 代码即可，不走 docs） |

## 不在本 skill 范围

- **本地图片自动上传**（`![](./local.png)`）：lark-doc 不会自动找本地文件。如有需要请提示用户：(a) 把图上传图床改成 https，或 (b) 让用户单独跑 `docs +media-insert --file <path>`。
- **PlantUML / 复杂 DSL 画板**：需要走 `lark-whiteboard` skill 的 svg / dsl 路由，本 skill 仅覆盖 mermaid。
- **文档内嵌 sheet / bitable**：超出 markdown 表达力，由 `lark-doc` skill 主流程处理。

## 参考

- `references/lark-doc-recap.md` — lark-cli v2 Markdown 写入要点（转义、`@file` 传参、whiteboard 占位）
- `references/mermaid-fallback.md` — 渲染失败三档兜底
- `references/examples.md` — 一篇含 sequence + mindmap 的完整命令链示例
- `checklists.md` — 收尾自检
- 上游：[`lark-cli/skills/lark-doc/SKILL.md`](https://github.com/larksuite/cli) / [`lark-cli/skills/lark-whiteboard/routes/mermaid.md`](https://github.com/larksuite/cli)
