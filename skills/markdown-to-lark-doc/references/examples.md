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

## 完整命令链

```bash
# Step 0 — 环境校验
lark-cli --version
npx -y @larksuite/whiteboard-cli@^0.2.11 -v

# Step 1 — 抽 mermaid
python3 scripts/extract_mermaid.py /tmp/demo.md
# stdout: {"processed_md":"/tmp/demo.processed.md","blocks_json":"/tmp/demo.mermaid_blocks.json","block_count":2}

# Step 2 + 3 — 新建文档
lark-cli docs +create \
  --api-version v2 \
  --doc-format markdown \
  --content @/tmp/demo.processed.md \
  --as user \
  > /tmp/demo.create_resp.json

# 检查响应
jq '.data.document.url' /tmp/demo.create_resp.json
# → "https://xxx.feishu.cn/docx/doxcnAbCdEf..."

jq '.data.document.new_blocks[] | select(.block_type=="whiteboard")' /tmp/demo.create_resp.json
# → 两条 {block_id, block_type:"whiteboard", block_token:"wbcn..."}

# Step 4 — 对齐
python3 scripts/stitch_boards.py \
  --blocks /tmp/demo.mermaid_blocks.json \
  --response /tmp/demo.create_resp.json \
  --basename demo \
  > /tmp/demo.stitched.json

cat /tmp/demo.stitched.json
# [
#   {"mmd_id":0,"code":"sequenceDiagram\n...","board_token":"wbcn...","block_id":"...","idempotent_token":"1747600000-demo-0"},
#   {"mmd_id":1,"code":"mindmap\n...","board_token":"wbcn...","block_id":"...","idempotent_token":"1747600000-demo-1"}
# ]

# Step 5 — 逐个写画板
jq -c '.[]' /tmp/demo.stitched.json | while read row; do
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

# Step 7 — 汇报
echo "Doc: $(jq -r .data.document.url /tmp/demo.create_resp.json)"
```

## 追加模式（向已有文档）

把 Step 2+3 改成：

```bash
DOC="https://xxx.feishu.cn/docx/doxcnExistingDoc"

lark-cli docs +update \
  --api-version v2 \
  --doc "$DOC" \
  --command append \
  --doc-format markdown \
  --content @/tmp/demo.processed.md \
  --as user \
  > /tmp/demo.update_resp.json
```

后续 Step 4/5/7 不变；`stitch_boards.py` 同样从 `data.document.new_blocks[]` 里取新追加的画板（已有 block 不会被列入 new_blocks）。
