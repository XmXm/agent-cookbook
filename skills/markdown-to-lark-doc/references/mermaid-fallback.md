# Mermaid 渲染失败的兜底

`whiteboard-cli` 的 mermaid 解析器只覆盖一部分类型（引自上游 `lark-cli/skills/lark-whiteboard/routes/mermaid.md`）：

> 适用于：思维导图、时序图、类图、饼图、甘特图。

落到 mermaid 关键字大致是：`mindmap` / `sequenceDiagram` / `classDiagram` / `pie` / `gantt`。其它（`flowchart` / `graph` / `stateDiagram` / `journey` / `erDiagram` / `quadrantChart` / `sankey` / `gitGraph` / `timeline` / `xychart-beta` 等）能不能渲染要看 whiteboard-cli 当前版本，**不要假定**。

## 兜底优先级

### 档 1 — 留作 mermaid 代码块（首选）

最稳的兜底：让飞书原生渲染 mermaid 代码块。用 v2 的 `block_replace` 把空白画板换成 fenced code block：

```bash
lark-cli docs +update \
  --api-version v2 \
  --doc <doc-url-or-token> \
  --command block_replace \
  --block-id <empty whiteboard 的 block_id> \
  --content '<code language="mermaid">graph TD
A --> B
</code>' \
  --as user
```

注意：
- `--content` 这里用 **XML**，**不要**传 `--doc-format markdown`（默认 `xml` 正合适）。
- 内嵌 `<` 不需要再转义；外层用单引号包死字面量。
- 代码内换行直接写，shell 单引号会保留。
- `<block-id>` 来自 `stitched.json` 的 `block_id` 字段（stitch 脚本已经从 `new_blocks[]` 取过）。

### 档 2 — PNG 降级（最后手段）

代码块都渲染不出来时：

```bash
# 1) 渲染 PNG
npx -y @larksuite/whiteboard-cli@^0.2.11 -i /tmp/mmd-N.mmd -o /tmp/mmd-N.png

# 2) 在原位附近插入图片（选一段失败 placeholder 周围的唯一文本片段做锚点）
lark-cli docs +media-insert \
  --doc <doc-url-or-token> \
  --file /tmp/mmd-N.png \
  --caption "mermaid block #N (rendered as image)" \
  --selection-with-ellipsis '<占位前后的唯一文本，可用 start...end 形式>' \
  --as user

# 3) 删掉空白占位
lark-cli docs +update \
  --api-version v2 \
  --doc <doc-url-or-token> \
  --command block_delete \
  --block-id <placeholder block_id> \
  --as user
```

> `--selection-with-ellipsis` 支持 `'start...end'` 两段拼接做唯一定位；如果锚点不唯一，先 `+fetch` 看一眼实际文本再决定。

## 何时跳过 fallback

如果用户明确说"画板转不了就报错给我"，就不要悄悄走 fallback，直接停下、把失败的 mmd_id 和原代码一起返回给用户决定。

## 自检

无论走哪一档，最后向用户汇总时必须**显式标注每个 mmd_id 的最终归宿**：

```
- mmd_id=0  ✓ board=B0ysw...
- mmd_id=1  ⚠ fallback=code-block (render check failed: node-overlap)
- mmd_id=2  ⚠ fallback=png  (placeholder deleted, image inserted at <anchor>)
```
