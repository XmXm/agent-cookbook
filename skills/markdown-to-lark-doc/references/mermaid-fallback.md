# Mermaid 渲染失败的三档兜底

`whiteboard-cli` 的 mermaid 解析器只覆盖一部分类型（引自上游 `lark-cli/skills/lark-whiteboard/routes/mermaid.md`）：

> 适用于：思维导图、时序图、类图、饼图、甘特图。

落到 mermaid 关键字大致是：`mindmap` / `sequenceDiagram` / `classDiagram` / `pie` / `gantt`。其它（`flowchart` / `graph` / `stateDiagram` / `journey` / `erDiagram` / `quadrantChart` / `sankey` / `gitGraph` / `timeline` / `xychart-beta` 等）能不能渲染要看 whiteboard-cli 当前版本，**不要假定**。

## 兜底优先级

### 档 1 — 留作 mermaid 代码块

最稳的兜底：让飞书自己渲染。把占位 block 替换成 fenced code with `language=mermaid`：

```bash
lark-cli docs +update \
  --api-version v2 \
  --doc <doc_id> \
  --command block_replace \
  --block-id <block_id of the empty whiteboard> \
  --content '<code language="mermaid">graph TD
A --> B
</code>' \
  --as user
```

注意：
- `--content` 用 **XML** 而不是 markdown（v2 局部精修要求；`--doc-format xml` 是默认值）
- 内嵌 `<` 不需要再转义；外层用单引号包死字面量
- 代码内换行直接写，shell 单引号会保留

### 档 2 — 同档 1，但触发条件不同

mermaid 语法在 whiteboard-cli 的覆盖集里，但 `--check` 报 `text-overflow` / `node-overlap` 两轮修不掉时也走档 1。不要花太多时间手工调 mermaid 布局，飞书内置渲染通常更可控。

### 档 3 — PNG 降级

实在不行（whiteboard-cli 直接崩、飞书 mermaid 渲染也不行）：

```bash
# 转 PNG
npx -y @larksuite/whiteboard-cli@^0.2.11 -i /tmp/mmd-N.mmd -o /tmp/mmd-N.png

# 上传为图片 block 到文档末尾（注意是文档末尾，不是占位位置）
lark-cli docs +media-insert \
  --doc <doc_id> \
  --file /tmp/mmd-N.png \
  --caption "mermaid block #N (rendered as image)" \
  --as user

# 然后用 block_delete 把原占位干掉
lark-cli docs +update \
  --api-version v2 \
  --doc <doc_id> \
  --command block_delete \
  --block-id <placeholder-block-id> \
  --as user
```

> 档 3 的缺陷：图片落在文档末尾而不是原位置。如果文章有 ≥2 个失败 mermaid，结尾顺序就乱了。**优先用档 1**。

## 何时跳过 fallback

如果用户明确说"画板转不了就报错给我"，就不要悄悄走 fallback，直接停下、把失败的 mmd_id 和原代码一起返回给用户决定。

## 自检

无论走哪一档，最后向用户汇总时必须**显式标注每个 mmd_id 的最终归宿**：

```
- mmd_id=0  ✓ board=wbcn...
- mmd_id=1  ⚠ fallback=code-block (render check failed: node-overlap)
- mmd_id=2  ⚠ fallback=png  (placeholder deleted, image appended at end)
```
