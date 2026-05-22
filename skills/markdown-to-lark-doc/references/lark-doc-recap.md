# lark-doc v2 Markdown 写入要点（速查）

本 skill 用到的 lark-cli v2 行为浓缩，不替代上游 `lark-cli/skills/lark-doc/references/lark-doc-md.md`。

## API version 是硬要求

所有 `docs +*` 命令必须带 `--api-version v2`：

```bash
lark-cli docs +create  --api-version v2 ...
lark-cli docs +fetch   --api-version v2 ...
lark-cli docs +update  --api-version v2 ...
```

缺了会进 v1 (MCP) 路径，stderr 输出 `[deprecated] docs +<verb> is using the v1 API. ... run \`lark-cli update\` to upgrade skills.` 同时 stdout 可能是 v1 envelope，结构不一样。

## 内容传参：用 `@file`

`--content` 支持三种来源：

| 写法 | 用途 |
|---|---|
| `'<literal>'` | 短内容，单引号包字面量 |
| `-` | 从 stdin 读 |
| `@/path/to/file.md` | 从文件读（推荐） |

本 skill 一律走 `@<file>.processed.md`，彻底绕开 shell 转义。

字面以 `@` 开头时用 `@@` 双写转义；`--pattern` 不支持 `@file`。

## Markdown 中的 whiteboard 占位

`lark-doc-xml.md` 第 18 行：

> `<whiteboard>` 嵌入画板 `type`: `blank` \| `mermaid` \| `plantuml` \| `svg`

即使 `--doc-format markdown`，文档解析器仍会把 `<whiteboard>` 当作真实 block，不会按字面输出。所以本 skill 的占位用：

```html
<whiteboard type="blank" data-mmd-id="N"></whiteboard>
```

`data-mmd-id` 是我们自加的属性，飞书侧会忽略，只为本地对账。

## 响应里取 board_token

`docs +create` / `docs +update` v2 响应：

```json
{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "document_id": "doxcn...",
      "url": "https://xxx.feishu.cn/docx/doxcn...",
      "new_blocks": [
        {"block_id": "...", "block_type": "whiteboard", "block_token": "wbcn..."},
        ...
      ]
    }
  }
}
```

- 文档 URL：`data.document.url`
- 画板 token：过滤 `data.document.new_blocks[]` 中 `block_type == "whiteboard"` 的 `block_token`
- v2 服务端**保证 new_blocks 顺序与 markdown 中出现顺序一致**——这是 `stitch_boards.py` 直接顺序对齐的依据。

## 网络图片：自动下载

```markdown
![alt](https://example.com/photo.png)
```

`--doc-format markdown` 模式下 lark-cli 会自动 HTTP 下载并插成图片 block。本 skill 不需要为这种图做任何处理。

> 本地路径 `![](./local.png)` **不会**被自动上传——会留作死链。本 skill 范围外。

## 转义要点

`docs +fetch --doc-format markdown` 导出的内容里 `\[ \] \| \\` 等已经是转义过的，**不要反转义**；自己构造内容写入时也按 markdown 规则转义（`\\` `\` `\*` `\[` `\]` 等）。详见上游 `lark-doc-md.md`。

本 skill 不动 markdown 主体，转义责任在用户写的 md 作者；脚本只动 fence。

## 创建 vs 追加 vs 局部精修

| 场景 | 命令 |
|---|---|
| 新建文档 | `docs +create --api-version v2 --doc-format markdown --content @file.md` |
| 文档末尾追加整段 | `docs +update ... --command append --doc-format markdown --content @file.md` |
| 改某个 block | `docs +update ... --command block_replace --block-id <bid> --content '<xml>...'`（**用 XML，不用 markdown**） |

本 skill 只覆盖前两种。第三种留给 fallback（mermaid 失败时把占位 block_replace 回 mermaid 代码块）。
