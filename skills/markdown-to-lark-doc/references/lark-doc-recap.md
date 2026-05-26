# lark-cli v2 写入要点（速查）

本 skill 用到的 lark-cli v2 行为浓缩，不替代上游 `lark-cli/skills/lark-doc/references/lark-doc-md.md`。

## API version 是硬要求

所有 `docs +*` 命令必须带 `--api-version v2`：

```bash
lark-cli docs +create  --api-version v2 ...
lark-cli docs +fetch   --api-version v2 ...
lark-cli docs +update  --api-version v2 ...
```

不传会落到 v1 deprecated 路径。v1 的 `+update` 用 `--mode/--markdown/--new-title` 也能写内容，但响应里**不返回 `new_blocks`**，本 skill 的画板对齐脚本会失败。

## 内容传参：`--content @file --doc-format markdown`

v2 写入 markdown **必须**两个旗子一起：

```bash
--content @docs/file.md --doc-format markdown
```

- `--content` 支持三种来源：`'<literal>'`、`-`（stdin）、`@/path/to/file`（推荐）。
- `--doc-format` 默认是 `xml`。**漏传 `markdown` 会被 XML 解析器吃掉正文，只剩 `<whiteboard>` 等合法 XML block 标签**。
- `@<file>` 路径必须**相对当前目录**：`--file must be a relative path within the current directory`。先 `cd` 到 md 所在目录。
- 字面以 `@` 开头时用 `@@` 双写转义。

`--markdown @file` 是 v1 的旗子（默认不带 `--api-version v2` 时才出现），别用。

## v2 +update 的操作动词：`--command`

| `--command` 值 | 用途 | 必备额外旗子 |
|---|---|---|
| `overwrite` | 全文替换（覆盖正文，删除现存画板） | `--content + --doc-format markdown` |
| `append` | 文档末尾追加整段 | `--content + --doc-format markdown` |
| `str_replace` | 文本替换 | `--pattern` |
| `block_replace` | 替换某个 block | `--block-id` + `--content '<xml>'`（不传 `--doc-format markdown`） |
| `block_delete` | 删某个 block | `--block-id` |
| `block_insert_after` | 在某 block 后插入 | `--block-id` + `--content` |
| `block_copy_insert_after` / `block_move_after` | 复制/移动 block | `--block-id` + `--src-block-ids` |

本 skill 主流程只用 `overwrite` 和 `append`，fallback 用 `block_replace` / `block_delete`。

## Markdown 中的 whiteboard 占位

`lark-doc-xml.md` 第 18 行：

> `<whiteboard>` 嵌入画板 `type`: `blank` \| `mermaid` \| `plantuml` \| `svg`

`--doc-format markdown` 模式下，文档解析器仍会把 `<whiteboard>` 当作真实 block，不按字面输出。本 skill 的占位用：

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
      "document_id": "Lcp2...",
      "url": "https://xxx.feishu.cn/docx/Lcp2...",
      "new_blocks": [
        {"block_id": "...", "block_type": "whiteboard", "block_token": "B0ysw..."},
        ...
      ]
    }
  }
}
```

- 文档 URL：`data.document.url`
- 画板 token：过滤 `data.document.new_blocks[]` 中 `block_type == "whiteboard"` 的 `block_token`
- **`block_token` 前缀不固定**（实测见过 `B`、`X`、`C`、`E`、`V`、`N`、`T`、`J`、`M` 起头）。stitch 脚本的格式 warning 可忽略。
- v2 服务端**保证 new_blocks 顺序与 markdown 中出现顺序一致**——这是 `stitch_boards.py` 直接顺序对齐的依据。

## Wiki URL 解析

```bash
lark-cli docs +fetch --api-version v2 --doc <wiki-url> --as user --jq '.data.document'
```

返回结构：
```json
{"document_id": "Lcp2...", "obj_token": null, "title_info": null, "url": null}
```

注意 v2 `+fetch` 经常返回 `obj_token = null`，**用 `document_id` 兜底**。把 `document_id` 当作 `--doc` 参数传 `+update` 就行。

## 标题

v2 没有 `--title` / `--new-title` 旗子。**标题从 markdown 首行 `# H1` 自动提取**，想改标题就改源 md 的第一行。

## 网络图片：自动下载

```markdown
![alt](https://example.com/photo.png)
```

`--doc-format markdown` 模式下 lark-cli 会自动 HTTP 下载并插成图片 block。本 skill 不需要为这种图做任何处理。

> 本地路径 `![](./local.png)` **不会**被自动上传——会留作死链。本 skill 范围外。

## 转义要点

`docs +fetch` 导出的内容里 `\[ \] \| \\` 等已经是转义过的，**不要反转义**；自己构造内容写入时也按 markdown 规则转义（`\\` `\` `\*` `\[` `\]` 等）。详见上游 `lark-doc-md.md`。

本 skill 不动 markdown 主体，转义责任在用户写的 md 作者；脚本只动 fence。

## 创建位置参数

`+create --api-version v2` 用：

| 旗子 | 用途 |
|---|---|
| `--parent-position my_library` | 放进个人知识库（wiki/） |
| `--parent-token <token>` | 放进指定 folder 或 wiki-node |

不传 `--parent-position` 也不传 `--parent-token` → 落入云空间根目录。
