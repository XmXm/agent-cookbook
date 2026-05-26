# 收尾自检清单

每次跑完工作流，向用户汇报前逐条核对。任何一条不通过先修，再汇报。

## 环境

- [ ] `lark-cli --version` 可执行
- [ ] `lark-cli` 已登录用户身份（`lark-cli auth login` 至少跑过一次）
- [ ] `npx -y @larksuite/whiteboard-cli@^0.2.11 -v` 可执行

## 参数 / 命令

- [ ] 所有 `docs +*` 命令都带 `--api-version v2`（不传会落 v1，`+update` 不返回 `new_blocks`）
- [ ] 写入 markdown 用 `--content @<file>.processed.md --doc-format markdown` 两个旗子一起，**`--doc-format markdown` 不能漏**（漏了走 XML 解析，正文全丢只剩 `<whiteboard>`）
- [ ] `+update` 模式用 `--command overwrite|append|block_replace|block_delete|...`，不是 `--mode`（那是 v1 deprecated 旗子）
- [ ] `@<file>` 是**相对当前目录**的路径，已经 `cd` 到 md 所在目录
- [ ] 标题需求：源 md 首行 H1 = 期望标题（v2 没有 `--title/--new-title` 旗子，只看 md）
- [ ] doc 参数可以是 `/docx/<TOKEN>` URL、`/wiki/<TOKEN>` URL，或 `document_id`；wiki URL 报错时用 `+fetch` 取 `data.document.document_id` 兜底（不是 `obj_token`，v2 fetch 经常返回 null）
- [ ] 每个画板 `--idempotent-token` 长度 ≥ 10，按 `<unix>-<basename>-<idx>` 模板生成
- [ ] 已有内容画板 二次写入做过 `--overwrite --dry-run` 探测并征得用户确认

## 写入后验证（汇报前）

- [ ] `docs +fetch --api-version v2 --doc <doc>` 拉回文档
- [ ] `text_chars` 与源 md 同量级（不是只剩几百字节）
- [ ] `<whiteboard>` 数 = 源 md 中 ` ```mermaid ` 围栏数
- [ ] `<title>` = 源 md 首行 H1（除非源 md 没 H1，那时是 `Untitled` 也算合理）

## 数据对账

- [ ] `extract_mermaid.py` 输出的 `block_count` = 源 md 中 ` ```mermaid ` 围栏数
- [ ] `stitch_boards.py` 不报 count mismatch（placeholder 数 = `new_blocks[]` 中 `block_type=="whiteboard"` 的数量）
- [ ] 处理过的 `processed.md` 不再包含字面量 ` ```mermaid ` 字符串（除非用户自己在引述）

## 汇报内容

向用户至少输出：

- [ ] 文档 URL（`data.document.url`）
- [ ] 标题、正文字符数
- [ ] 画板写入成功数 / 总数
- [ ] 每个 mermaid block 的最终归宿（board_token / fallback=code-block / fallback=png）
- [ ] 任何失败的 mmd 原文片段，方便用户决策

## 不要做

- [ ] **不要切到 `lark-wiki` / `lark-drive` skill 去"解析" wiki URL**——wiki URL 直接当 `docs +update --doc <wiki-url>` 的参数就行，v2 服务端会自己解
- [ ] **不要调 `lark-cli wiki +node-get` 拿 obj_token**——会触发 `wiki:node:retrieve` scope 缺失，引发整轮 OAuth re-login，本流程根本不需要
- [ ] **不要 `lark-cli auth login --scope "..."`**——现有 token 的 docx scope 就够本 skill 全流程；缺 scope 说明走错了 verb，退回上一步
- [ ] 不要悄悄给本地图片 `![](./x.png)` 改路径或上传——超出 skill 范围，必须明确告知用户
- [ ] 不要在 mermaid fallback 时不汇报，全部失败/降级路径都要显式标注
- [ ] 不要重复跑同一 `--idempotent-token`，重试请换 epoch 或 idx
- [ ] 看到 `--mode` / `--markdown` / `--new-title` 这几个旗子立即停下——那是 v1 deprecated 路径，本 skill 不走
- [ ] 用户已明说"覆盖 / 直接覆盖 / overwrite" 就不要再追问一轮"是否确认"——已表态等同确认
