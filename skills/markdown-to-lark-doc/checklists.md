# 收尾自检清单

每次跑完工作流，向用户汇报前逐条核对。任何一条不通过先修，再汇报。

## 环境

- [ ] `lark-cli --version` 输出 ≥ 1.0.32，且没有 "v1 deprecation" 警告
- [ ] `lark-cli` 已登录用户身份（`lark-cli auth login` 至少跑过一次）
- [ ] `npx -y @larksuite/whiteboard-cli@^0.2.11 -v` 可执行

## 参数 / 命令

- [ ] 所有 `docs +*` 命令都带 `--api-version v2`
- [ ] doc token 形如 `docxXXXXXXXXXXXXXXX`（≥19 字符总长，前缀 `docx`），URL 形式已自动剥成裸 token 或直接传 URL 都行
- [ ] `--content` 走 `@<file>.processed.md` 而不是直接拼字符串
- [ ] 每个画板 `--idempotent-token` 长度 ≥ 10，按 `<unix>-<basename>-<idx>` 模板生成
- [ ] 已有内容画板 二次写入做过 `--overwrite --dry-run` 探测并征得用户确认

## 数据对账

- [ ] `extract_mermaid.py` 输出的 `block_count` = 源 md 中 ` ```mermaid ` 围栏数
- [ ] `stitch_boards.py` 不报 count mismatch（placeholder 数 = `new_blocks[]` 中 `block_type=="whiteboard"` 的数量）
- [ ] 处理过的 `processed.md` 不再包含字面量 ` ```mermaid ` 字符串（除非用户自己在引述）

## 汇报内容

向用户至少输出：

- [ ] 文档 URL（`data.document.url`）
- [ ] 画板写入成功数 / 总数
- [ ] 每个 mermaid block 的最终归宿（board_token / fallback=code-block / fallback=png）
- [ ] 任何失败的 mmd 原文片段，方便用户决策

## 不要做

- [ ] 不要悄悄给本地图片 `![](./x.png)` 改路径或上传——超出 skill 范围，必须明确告知用户
- [ ] 不要在 mermaid fallback 时不汇报，全部失败/降级路径都要显式标注
- [ ] 不要重复跑同一 `--idempotent-token`，重试请换 epoch 或 idx
