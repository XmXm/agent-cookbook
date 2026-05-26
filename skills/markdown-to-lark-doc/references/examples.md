# 端到端示例

一篇 `demo.md`：

```markdown
# 季度复盘

## 关键时序

下面是用户从下单到收货的关键路径：

​```mermaid
sequenceDiagram
  participant U as 用户
  participant S as 服务端
  participant W as 仓储
  U->>S: 下单
  S->>W: 占库存
  W-->>S: 已占
  S-->>U: 订单创建成功
​```

## 思维导图：本季度重点

​```mermaid
mindmap
  root((Q3))
    增长
      用户量
      留存
    效率
      自动化
      工具链
​```

![架构图](https://example.com/arch.png)

完。
```

> 注：上面的 ` ​``` ` 是为了在本 reference 中展示，实际 md 用普通三重反引号。

## 完整命令链（新建）

```bash
# Step 0 — 环境校验
lark-cli --version
npx -y @larksuite/whiteboard-cli@^0.2.11 -v

# Step 1 — 抽 mermaid（先 cd 到 md 所在目录，后续 @file 都是相对路径）
cd ~/docs
python3 ~/.agents/skills/markdown-to-lark-doc/scripts/extract_mermaid.py demo.md
# stdout: {"processed_md":"demo.processed.md","blocks_json":"demo.mermaid_blocks.json","block_count":2}

# Step 2 + 3 — 新建文档（默认放入个人 wiki）
lark-cli docs +create \
  --api-version v2 \
  --parent-position my_library \
  --content @demo.processed.md \
  --doc-format markdown \
  --as user \
  > demo.create_resp.json

# 检查响应
jq '.data.document.url' demo.create_resp.json
# → "https://xxx.feishu.cn/docx/Lcp2..."

jq '.data.document.new_blocks[] | select(.block_type=="whiteboard")' demo.create_resp.json
# → 两条 {block_id, block_type:"whiteboard", block_token:"..."}

# Step 4 — 对齐
python3 ~/.agents/skills/markdown-to-lark-doc/scripts/stitch_boards.py \
  --blocks demo.mermaid_blocks.json \
  --response demo.create_resp.json \
  --basename demo \
  > demo.stitched.json

cat demo.stitched.json
# [
#   {"mmd_id":0,"code":"sequenceDiagram\n...","board_token":"...","block_id":"...","idempotent_token":"1747600000-demo-0"},
#   {"mmd_id":1,"code":"mindmap\n...","board_token":"...","block_id":"...","idempotent_token":"1747600000-demo-1"}
# ]

# Step 5 — 逐个写画板
jq -c '.[]' demo.stitched.json | while read row; do
  TOKEN=$(echo "$row" | jq -r .board_token)
  IDEM=$(echo "$row"  | jq -r .idempotent_token)
  ID=$(echo "$row"    | jq -r .mmd_id)
  echo "$row" | jq -r .code > /tmp/mmd-$ID.mmd

  # 5b. 本地预览（可选）
  npx -y @larksuite/whiteboard-cli@^0.2.11 -i /tmp/mmd-$ID.mmd -o /tmp/mmd-$ID.png || {
    echo "render failed for mmd_id=$ID, see references/mermaid-fallback.md"; continue;
  }

  # 5c. 写画板
  npx -y @larksuite/whiteboard-cli@^0.2.11 -i /tmp/mmd-$ID.mmd --to openapi --format json \
    | lark-cli whiteboard +update \
        --whiteboard-token "$TOKEN" \
        --source - --input_format raw \
        --idempotent-token "$IDEM" \
        --as user
done

# Step 7 — 验证文档完整性
lark-cli docs +fetch --api-version v2 --doc "$(jq -r .data.document.document_id demo.create_resp.json)" --as user 2>/dev/null \
  | python3 -c "
import json, re, sys
doc = json.load(sys.stdin)['data']['document']
content = doc.get('content', '')
print(f'text_chars={len(re.sub(r\"<whiteboard[^>]*></whiteboard>|<title>.*?</title>\", \"\", content).strip())}, whiteboards={len(re.findall(r\"<whiteboard\", content))}, title={re.findall(r\"<title>(.*?)</title>\", content)}')
"

# Step 8 — 汇报
echo "Doc: $(jq -r .data.document.url demo.create_resp.json)"
```

## 追加模式（向已有文档）

把 Step 2+3 改成：

```bash
DOC="https://xxx.feishu.cn/docx/Lcp2..."   # docx URL / wiki URL / document_id 都行

lark-cli docs +update \
  --api-version v2 \
  --doc "$DOC" \
  --command append \
  --content @demo.processed.md \
  --doc-format markdown \
  --as user \
  > demo.update_resp.json
```

## 全文替换模式（清空原文档后整篇覆盖）

```bash
lark-cli docs +update \
  --api-version v2 \
  --doc "$DOC" \
  --command overwrite \
  --content @demo.processed.md \
  --doc-format markdown \
  --as user \
  > demo.update_resp.json
```

> stderr 会给警告：`the document contains N whiteboard blocks that cannot be reconstructed from Markdown; overwrite will permanently delete them`。如果之前文档里有手工画的画板，全文替换会全部清掉。
> 要改标题：直接改 demo.md 的首行 `# Title`，v2 没有显式 title 旗子。

后续 Step 4/5/7 不变；`stitch_boards.py` 同样从 `data.document.new_blocks[]` 里取新写入的画板（已有 block 不会被列入 new_blocks）。
