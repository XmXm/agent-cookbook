---
name: markdown-to-lark-doc
description: |
  整篇本地 .md 文件导入飞书云文档（图文并茂），自动把 ```mermaid 围栏块转成飞书画板。
  Use when the user says "md 推到飞书"、"导入 lark-doc"、"markdown 转飞书文档"、
  "把这个 md 同步成飞书"、"mermaid 转画板"、"markdown-to-lark-doc"、"sync md to feishu"，
  或刚写完一篇含 mermaid 的 markdown 并提到飞书 / 云文档 / 知识库 / wiki。
  覆盖新建文档、向已有 doc 追加、全文替换已有 doc 三种模式，全程使用 lark-cli docs v2 API。
compatibility: |
  Requires: lark-cli (latest), Node.js (`npx -y @larksuite/whiteboard-cli@^0.2.11`),
  Python 3.8+ for the bundled scripts. Auth: `lark-cli auth login` (user mode) before first run.
---

# markdown-to-lark-doc

把一篇本地 `.md` 文件**整篇**推到飞书云文档（Docx），其中 ` ```mermaid ` 围栏代码块自动**转成飞书画板**，其余 markdown 元素（标题、列表、表格、`![](https://...)` 网络图片）按 lark-cli v2 的 Markdown 渲染直接生效。

> **不变量**（贯穿全流程，违反任何一条都停下）
> 1. 所有 `docs +*` 命令必须带 `--api-version v2`。不传会落到 v1 deprecated 路径，且 v1 的 `+update` **不返回 `new_blocks`**，画板对齐直接没戏。
> 2. v2 写 markdown 的**唯一正确组合**是 `--content @<file> --doc-format markdown`：
>    - **必须显式传 `--doc-format markdown`** —— 默认是 `xml`，传 markdown 进去会被 XML 解析器吃掉，正文全丢只剩 `<whiteboard>` 标签。这是本 skill 历史踩过的头号坑。
>    - `--markdown @file` 不是 v2 的旗子（那是 v1 的），别用。
> 3. `@<file>` 路径**必须相对当前目录**。绝对路径 lark-cli 会拒：`--file must be a relative path within the current directory`。`cd` 到 md 所在目录再调用。
> 4. v2 的 `+update` 模式用 `--command overwrite|append|str_replace|block_replace|...`（不是 `--mode`，那是 v1）。全文替换 = `--command overwrite`，追加 = `--command append`。
> 5. v2 没有 `--new-title` / `--title` 旗子。文档标题从 markdown 首行 `# H1` 自动提取，想改标题就改 md 的 H1。
> 6. 目标 doc 可传完整 URL（`/docx/<TOKEN>` 或 `/wiki/<TOKEN>`）或裸 token，**直接当 `--doc` 参数传给 `docs +update` 即可**。v2 服务端会自行把 wiki token 解到底层 docx，不需要预先解析。
>    - **禁区**：不要去调 `lark-cli wiki +node-get` / `wiki nodes get_node` 拿 `obj_token`，那需要 `wiki:node:retrieve` scope，本流程现有的 `docx:document:write_only` 就够；切到 wiki skill 会触发 OAuth re-login，浪费一整轮。
>    - **唯一兜底**：极少数情况 `docs +update --doc <wiki-url>` 报 "doc not found" 时，才 `lark-cli docs +fetch --api-version v2 --doc <wiki-url>` 取 `data.document.document_id`（不是 `obj_token`，v2 fetch 经常返回 null），再用 document_id 重试 `+update`。**不要预防性 fetch**，遇到错才用。
> 7. 已写过内容的画板二次写入前必须 `--overwrite --dry-run` 探测，看到 `XX whiteboard nodes will be deleted` 先向用户确认。
> 8. `--idempotent-token` ≥10 字符，格式 `<unix>-<basename>-<idx>`，避免重试导致重复写入。
> 9. **本 skill 不处理本地图片自动上传** —— `!\[图注\]\(./local.png\)` 这种死链会留在文档中。需要本地图片时请提示用户用 `docs +media-insert` 手工补，或预先把图传到图床改成 https URL。

---

## 禁区：不要走的弯路（看到就停下）

| 错误路径 | 为什么是弯路 | 正确做法 |
|---|---|---|
| `lark-cli wiki +node-get --node-token <wiki-token>` 想拿 obj_token | 触发 `wiki:node:retrieve` scope 缺失，引发整轮 OAuth re-login；本流程根本不需要 | 直接 `docs +update --doc <wiki-url>`，v2 服务端自己解 |
| 看到 wiki URL 就觉得"得先解析" | 多此一举；浪费 1~2 个 tool call | 上一行 |
| 切到 `lark-wiki` skill | 那个 skill 是管知识库节点/成员的，不是写文档内容的；走它就跑偏了 | 全程留在 `markdown-to-lark-doc`，只用 `docs +create` / `docs +update` / `docs +fetch` |
| 用户说"覆盖写入"还跑去问要不要确认第二轮 | 用户表态等同确认 | 直接执行 overwrite |
| `lark-cli auth login --scope "..."` 加新 scope | 现有 token 的 `docx:document:write_only` + `docx:document:create` 就够本流程；缺 scope 是因为你走错了 verb | 退回上一步看看是不是误用了 wiki/drive verb |
| `docs +update` 不带 `--api-version v2` 还能跑 → 默认走 v1 deprecated 路径 | v1 响应里没有 `new_blocks`，画板对齐脚本会失败 | 永远带 `--api-version v2` |

**心法**：本 skill 全部 IO 只走 `lark-cli docs +*`。看到自己想 `lark-cli wiki +*` / `lark-cli drive +*` / `lark-cli api ...` 就立刻停下，回到 Step 2 的命令骨架表对照。

---

## Workflow

### Step 0 — Sanity check

```bash
lark-cli --version
npx -y @larksuite/whiteboard-cli@^0.2.11 -v
lark-cli auth status >/dev/null   # 必须已 `lark-cli auth login`
```

### Step 1 — 抽出 mermaid，生成占位 md

```bash
cd <md 所在目录>          # 见不变量 #3，后续所有 @file 都得是相对路径
python3 <skill-dir>/scripts/extract_mermaid.py <file.md>
# → 产出 <file>.processed.md  + <file>.mermaid_blocks.json
```

脚本会把每段 ` ```mermaid ... ``` ` 围栏替换为单行：

```html
<whiteboard type="blank" data-mmd-id="N"></whiteboard>
```

其余 markdown 内容原样保留（标题、列表、表格、`![](https://...)`、行内代码等）。

> `<whiteboard>` 是 lark-doc-xml.md 第 18 行确认的合法 block 类型；v2 的 markdown 解析器会把它当作真实 block 不按字面输出。

### Step 2 — 决定新建 vs 追加 vs 全文替换

**默认规则**：
- 用户只给了一个 md 文件、没给目标 doc → **新建文档**（放进个人 wiki）。
- 用户给了 md + 一个 doc URL/token，**没明说**"追加 / append / 加到末尾" → **默认全文替换**（必须先向用户确认一句"将清空 doc 全部内容并重新写入，是否继续？"）。
- 用户明说"追加 / append / 加到末尾" → 才走 append。

| 用户意图 | 命令骨架 |
|---|---|
| 用 md 新建文档 | `docs +create --api-version v2 --content @file --doc-format markdown --parent-position my_library` |
| 用 md **全文替换**已有文档（默认） | `docs +update --api-version v2 --doc <doc> --command overwrite --content @file --doc-format markdown` |
| 把 md 追加到已有文档末尾（需用户明说） | `docs +update --api-version v2 --doc <doc> --command append --content @file --doc-format markdown` |

**默认创建位置**：新建时加 `--parent-position my_library`，文档放进个人知识库。用户明确说"放云盘 / 我的空间 / 不要放 wiki" 时省略此参数。要指定父节点用 `--parent-token <token>`（既支持 folder token 也支持 wiki-node token）。

**全文替换注意事项**：
- `--command overwrite` 会**删除**目标文档的全部现有内容（包括画板），再写入新内容。stderr 会给警告：`the document contains N whiteboard blocks that cannot be reconstructed from Markdown; overwrite will permanently delete them`。
- 执行前必须向用户确认："将清空文档 `<token>` 的全部内容并重新写入，是否继续？"
- 全文替换后，文档 URL 不变，历史版本可在飞书版本记录中找回。

**标题**：从 markdown 首行 `# Title` 自动提取（v2 没有显式 title 旗子）。要改标题就改 md 第一行 H1。

### Step 3 — 写入文档

```bash
# 新建（默认放入个人 wiki）
lark-cli docs +create \
  --api-version v2 \
  --parent-position my_library \
  --content @<file>.processed.md \
  --doc-format markdown \
  --as user \
  > create_resp.json

# 追加到已有 doc
lark-cli docs +update \
  --api-version v2 \
  --doc <docx-url | document_id | wiki-url> \
  --command append \
  --content @<file>.processed.md \
  --doc-format markdown \
  --as user \
  > update_resp.json

# 全文替换已有 doc（用户确认后执行）
lark-cli docs +update \
  --api-version v2 \
  --doc <docx-url | document_id | wiki-url> \
  --command overwrite \
  --content @<file>.processed.md \
  --doc-format markdown \
  --as user \
  > update_resp.json
```

> - `@<file>` 必须**相对当前目录**，先 `cd` 到 md 所在目录。
> - **必须**带 `--doc-format markdown`，否则按 XML 解析正文全丢（见不变量 #2）。
> - 如果 wiki URL 直传报错：`lark-cli docs +fetch --api-version v2 --doc <wiki-url> --as user --jq .data.document.document_id` 取 `document_id`（不是 `obj_token`），再重试。

从响应里提取 `data.document.url` 报告给用户（即使后续画板填充失败，至少文档已建好）。

### Step 4 — 对齐 placeholder ↔ board_token

```bash
python3 <skill-dir>/scripts/stitch_boards.py \
  --blocks <file>.mermaid_blocks.json \
  --response create_resp.json \
  --basename <短标签> \
  > stitched.json
```

脚本：
- 从响应里过滤出 `data.document.new_blocks[]` 中 `block_type == "whiteboard"` 的项；
- **按顺序**与 `mermaid_blocks.json` 的 placeholder 对齐（v2 服务端保证 new_blocks 顺序与 markdown 中出现顺序一致）；
- 数量不一致直接退码 != 0，stderr 报错，让 agent 中止并报告用户。
- `board_token` 实际不一定以 `wb` 开头，stitch 脚本里的 warning 可忽略（不影响 pipeline）。

输出 `stitched.json` 是数组：

```json
[
  {"mmd_id": 0, "code": "sequenceDiagram\n...", "board_token": "B0ysw...", "idempotent_token": "1747600000-demo-0"},
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

按 `references/mermaid-fallback.md` 兜底：

1. **`whiteboard-cli` 渲染崩溃 / mermaid 类型不在适用集**（思维导图/时序图/类图/饼图/甘特图，引自 `lark-whiteboard/routes/mermaid.md`）→ 用 `docs +update --api-version v2 --command block_replace --block-id <bid> --content '<code language="mermaid">…</code>'` 把那个空白画板换回 mermaid 代码块（飞书原生可识别）。这里 `--content` 走的是 **XML**，不要传 `--doc-format markdown`。
2. **代码块也不行** → `whiteboard-cli -i x.mmd -o x.png` 转 PNG，再 `docs +media-insert --doc <doc> --file x.png --selection-with-ellipsis '<占位附近的唯一文本片段>'` 在原位插入图片，并 `+update --command block_delete --block-id <bid>` 删掉空白占位。汇报里**显式标注"已降级到 PNG"**。

### Step 7 — 验证文档完整性（必做，汇报前的最后一关）

不要相信 `+create/+update` 的 `ok:true` —— 把文档拉回来核对正文和画板数都对上：

```bash
lark-cli docs +fetch --api-version v2 --doc <doc-url-or-token> --as user 2>/dev/null \
  | python3 -c "
import json, re, sys
doc = json.load(sys.stdin)['data']['document']
content = doc.get('content', '')
wbs = len(re.findall(r'<whiteboard', content))
text = re.sub(r'<whiteboard[^>]*></whiteboard>|<title>.*?</title>', '', content).strip()
title = re.findall(r'<title>(.*?)</title>', content)
print(f'whiteboards={wbs}, text_chars={len(text)}, title={title}')
"
```

**红线**（任一触发立即停下并报告用户，**不要**当成功汇报）：
- `text_chars` 远小于源 md 字符数 → 正文被丢掉。最常见原因：忘了 `--doc-format markdown`（见不变量 #2）。
- `whiteboards` ≠ 源 md 中 mermaid 数 → placeholder 对齐错位。
- `title == 'Untitled'` 但源 md 有 H1 → 标题没提取出来，检查 md 首行是否被 `<whiteboard>` 占位之类东西挤掉。

红线触发后的处理：核对 Step 3 的命令，用正确的 v2 组合重写，再回到 Step 4 重对齐画板。

### Step 8 — 汇总输出

向用户报告：

```
✓ Doc: https://<host>.feishu.cn/docx/<token>
✓ Title: <标题>
✓ Body: <text_chars> chars
✓ Boards: N / M 成功（M 是总数）
  - mmd_id=0  <token>  sequenceDiagram   ✓
  - mmd_id=1  <token>  mindmap            ✓ (fallback: code-block)
  ...
```

---

## 触发场景速查

| 用户说 | 直接进 |
|---|---|
| "把 docs/notes.md 推到飞书"（只有 md，没给 doc） | Step 0 → 1 → 2 (**create**, wiki) |
| "用这个 md 新建一篇飞书文档" | 同上 |
| "把这个 md 同步到 https://xxx.feishu.cn/docx/doxabc..."（md + doc URL，没明说动词） | Step 0 → 1 → 2 (**overwrite** 默认)，先向用户确认 |
| "用这个 md 覆盖/替换 https://xxx..." | 同上，已表态等同确认 |
| "把这个 md 追加到 https://xxx..."（明说追加） | Step 0 → 1 → 2 (**append**) |
| "我的 markdown 里有 mermaid，导入飞书时画板也要建好" | 全流程 |
| "放到云盘 / 我的空间，不要 wiki" | create 时省略 `--parent-position` |
| 单纯 "把 mermaid 写到画板里" | 跳到 Step 5（用户给 board_token + 代码即可，不走 docs） |

## 不在本 skill 范围

- **本地图片自动上传**（`!\[alt\]\(./local.png\)`）：lark-doc 不会自动找本地文件。如有需要请提示用户：(a) 把图上传图床改成 https，或 (b) 让用户单独跑 `docs +media-insert --file <path>`。
- **PlantUML / 复杂 DSL 画板**：需要走 `lark-whiteboard` skill 的 svg / dsl 路由，本 skill 仅覆盖 mermaid。
- **文档内嵌 sheet / bitable**：超出 markdown 表达力，由 `lark-doc` skill 主流程处理。

## 参考

- `references/lark-doc-recap.md` — lark-cli v2 写入要点（`--content @file --doc-format markdown` 组合、whiteboard 占位、响应结构）
- `references/mermaid-fallback.md` — 渲染失败兜底（代码块 / PNG 两档）
- `references/examples.md` — 一篇含 sequence + mindmap 的完整命令链示例
- `checklists.md` — 收尾自检
- 上游：[`lark-cli/skills/lark-doc/SKILL.md`](https://github.com/larksuite/cli) / [`lark-cli/skills/lark-whiteboard/routes/mermaid.md`](https://github.com/larksuite/cli)
