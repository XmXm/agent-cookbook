---
name: lark-cli
description: >-
  飞书 / Lark 官方 CLI（lark-cli）统一入口：覆盖云文档（Docx/Wiki，含 doubao.com 托管的 /docx/、/wiki/）、
  知识库（Wiki）、云盘（Drive，/drive/、/file/）、电子表格（Sheets，/sheets/）、多维表格（Base/Bitable/BaseApp，/base/、/app/）、
  幻灯片（Slides，/slides/）、画板（Whiteboard）、即时通讯（IM 收发消息/群聊/聊天文件/交互卡片）、通讯录（Contact 姓名/邮箱查 open_id）、
  日历与会议室（Calendar）、视频会议与妙记（Meeting/Minutes/VC，/minutes/）、任务（Task）、审批（Approval）、
  邮件（Mail）、OKR、考勤（Attendance）、云端原生 Markdown、妙搭应用（Apps，/page/）、实时事件流（Event consume）、
  认证授权（auth/config）及原生 OpenAPI 探索。遇到上述飞书业务域或 URL/token 时使用（按 URL 路径模式而非域名路由，不要回退到 WebFetch）。
  不负责：project.feishu.cn 飞书项目工单（走 lark-proj / lark-story-closeout）、整篇本地 .md 含 mermaid 导入飞书文档（走 markdown-to-lark-doc）、
  架构图转飞书画板原生节点（走 architecture-to-lark-whiteboard）、按人名/账号查单聊记录（走 finding-lark-chat-history）。
metadata:
  requires:
    bins: ["lark-cli"]
---

# lark-cli：飞书 / Lark 统一技能入口

本 skill 是 `lark-cli` 全部官方分域能力的单一路由门，内化 `lark-shared` 的安全与契约底座，并通过 `lark-cli skills read` 按需加载与当前 CLI 二进制版本严格对齐的分域规范。

## 邻居边界（Not For）

命中以下专有工作流时，直接切换到对应邻居 skill，不要在本入口手工拼流程：

- **`project.feishu.cn` 飞书项目（Meego）bug / story 工单读写** → [`lark-proj`](../lark-proj/SKILL.md)（底层为 `bdt lark-proj`，不使用 `lark-cli`）
- **飞书项目需求单完成评论生成与节点流转** → [`lark-story-closeout`](../lark-story-closeout/SKILL.md)
- **整篇本地 `.md`（含 ` ```mermaid ` 自动转画板）导入飞书云文档** → [`markdown-to-lark-doc`](../markdown-to-lark-doc/SKILL.md)
- **把架构图画成飞书画板里的原生可编辑节点** → [`architecture-to-lark-whiteboard`](../architecture-to-lark-whiteboard/SKILL.md)
- **按中文姓名 / 邮箱前缀 / `open_id` 查单聊（P2P）历史记录** → [`finding-lark-chat-history`](../finding-lark-chat-history/SKILL.md)

---

## 核心工作流（强制二级加载）

**严禁凭记忆盲猜 `lark-cli` 的子命令或 flag。** 执行任何域操作前，按以下三步走：

1. **选定子域**：从下方「业务域路由表」确定目标 `<skill-name>`（多步跨端任务按执行顺序依次加载，如“查人并发消息”先读 `lark-contact` 再读 `lark-im`）。
2. **加载内嵌规范**：执行以下命令读取与本机二进制版本 100% 同步的官方子技能正文：
   ```bash
   lark-cli skills read <skill-name>
   ```
   当子技能正文要求阅读某个前置 reference 时，使用斜杠路径读取（不要遍历本地目录）：
   ```bash
   lark-cli skills read <skill-name>/<relative-path>
   # 例：lark-cli skills read lark-doc/references/lark-doc-xml.md
   ```
   > 若当前 CLI 二进制版本尚未内嵌某个新域，先跑 `lark-cli skills list` 核对名称，或回退读取本仓只读镜像 `../../refs/lark-skills/skills/<skill-name>/SKILL.md`。
3. **遵循共享铁律执行**：严格遵守下方「全局共享铁律（`lark-shared`）」发起调用与结果校验。

---

## 全局共享铁律（内化自 `lark-shared`）

1. **身份决定你代表谁操作（`--as user` vs `--as bot`）**
   - `--as user` 代表当前登录用户本人（访问/操作个人日历、云空间/云盘、文档、聊天等）。
   - `--as bot` 代表应用自身（仅能访问应用自己的资源；用 `bot` 查用户资源会返回空成功而非报错）。
   - 动手前必须明确身份；涉及身份诊断、`missing_scopes`、`console_url` 或发起 `auth login` 时，先跑：
     `lark-cli skills read lark-shared/references/lark-shared-identity-and-permissions.md`
2. **JSON 输出契约：用 `ok == true` 判断成功，禁止用 `code == 0`**
   - 默认 `--format json` 下，成功信封只有 `"ok": true` 和 `"data": ...`，**没有**顶层 `code` / `msg` 字段（`code` 只出现在错误信封的 `error` 内）。按旧 OpenAPI 格式判 `code == 0` 会把所有成功调用误判为失败。
   - 编写脚本封装前先读：`lark-cli skills read lark-shared/references/lark-shared-output-contract.md`
3. **退出码 `10` 是高风险确认门禁（`risk: "high-risk-write"`），不是报错**
   - 遇到 exit code `10`（`confirmation_required`）时：立即停下 → 向用户展示 `action`、`risk` 与关键参数 → **取得用户显式同意后**，再将 `hint` 指定的确认 flag（如 `--yes`）追加到原始命令末尾重试。**严禁**静默加 `--yes` 绕过。
   - 详见：`lark-cli skills read lark-shared/references/lark-shared-high-risk-approval.md`
4. **文件路径参数只接受相对路径**
   - `--file`、`--output`、`--output-dir`、`@file` 等参数只接受当前工作目录（`cwd`）下的相对路径，传绝对路径会直接报 `unsafe file path`。先 `cd` 到目标目录再调用，或优先通过 stdin 传大 JSON / 内容。
5. **授权与配置 URL 必须配二维码，严禁泄露密钥**
   - 命令输出含 `verification_url`、`verification_uri_complete`、`console_url` 时，必须用 `lark-cli auth qrcode --output <rel.png>` 生成二维码（除非用户明确要求才用 `--ascii`），原样展示 URL 在前、二维码在后。
   - 严禁将 `appSecret`、`accessToken` 等敏感凭据明文输出到终端。
6. **`_notice` 处理规范**
   - 输出中出现 `_notice.update` / `_notice.skills` 时，先完成用户当前任务，不要中断任务去查 help；需要给脚本提供干净 JSON 时加环境变量 `LARKSUITE_CLI_NO_UPDATE_NOTIFIER=1 LARKSUITE_CLI_NO_SKILLS_NOTIFIER=1`。

---

## 业务域路由表

按用户意图或 URL 路径模式（包括 `feishu.cn`、`larksuite.com` 及 `doubao.com` 托管链接）选择 `<skill-name>` 并执行 `lark-cli skills read <skill-name>`：

| 业务域 / URL 特征 | `<skill-name>` | CLI 帮助入口 | 职责边界与路由要点 |
|---|---|---|---|
| 认证、登录态、权限 scope、初始化 | `lark-shared` | `lark-cli auth --help` / `config --help` | `auth login/status/logout`、`--domain`、缺 scope、应用配置初始化 |
| 云文档（`/docx/`、`/wiki/` 正文）与思维笔记 | `lark-doc` | `lark-cli docs --help` / `mindnotes --help` | 文档读取、创建、编辑（优先 `--api-version v2`）、媒体插图下载；独立评论走 `lark-drive` |
| 知识库空间与目录树（`/wiki/` 节点管理） | `lark-wiki` | `lark-cli wiki --help` | 知识空间、节点树创建/移动、空间成员管理；仅读写文档正文直接走 `lark-doc` |
| 云盘 / 云空间（`/drive/`、`/file/`） | `lark-drive` | `lark-cli drive --help` | 文件夹管理、文件上传下载、权限协作者、独立全文/局部评论、知识库整理工作流 |
| 电子表格（`/sheets/`、Excel/CSV 互转） | `lark-sheets` | `lark-cli sheets --help` | 工作表结构、单元格/公式/样式读写、图表、透视表、条件格式、筛选、导入导出 |
| 多维表格与 Base 应用（`/base/`、`/app/`） | `lark-base` | `lark-cli base --help` | 建表、字段、记录、视图、统计、表单、仪表盘、BaseApp 页面组件、workflow、权限 |
| 幻灯片（`/slides/`） | `lark-slides` | `lark-cli slides --help` | 演示文稿创建、读取、单页增删与局部替换 |
| 飞书画板（Whiteboard） | `lark-whiteboard` | `lark-cli whiteboard --help` | 画板查询、导出图片/节点、用 Mermaid / PlantUML / SVG / DSL 更新画板内容 |
| 即时通讯（消息、群聊、卡片） | `lark-im` | `lark-cli im --help` | 发消息/回复、搜聊天记录、群与群成员管理、上传下载聊天文件、加急、交互卡片与回调 |
| 通讯录（找人、反查 `open_id`、查机器人） | `lark-contact` | `lark-cli contact --help` | 按姓名/邮箱解析 `open_id`，按 `open_id` 反查姓名/部门/邮箱/状态，搜可见机器人 |
| 日历与会议室 | `lark-calendar` | `lark-cli calendar --help` | 查看/搜索/创建/修改日程、参会人管理、忙闲查询与时段推荐、会议室查询与预定 |
| 视频会议、妙记与纪要（`/minutes/`） | `lark-minutes` / `lark-vc` / `lark-note` | `lark-cli minutes --help` / `vc --help` | 历史会议记录、妙记转写与总结、纪要与参会智能体（新版本 CLI 合并为 `lark-meeting`） |
| 飞书任务与清单 | `lark-task` | `lark-cli task --help` | 待办任务、子任务、任务清单、协作成员、任务附件、任务智能体（非审批待办） |
| 飞书审批 | `lark-approval` | `lark-cli approval --help` | 查询处理审批待办/已办/实例、搜索审批定义并发起原生审批实例 |
| 飞书邮箱 | `lark-mail` | `lark-cli mail --help` | 邮件查询、读取、发送与 HTML 邮件校验修复 |
| OKR | `lark-okr` | `lark-cli okr --help` | OKR 周期与目标查询管理 |
| 考勤打卡 | `lark-attendance` | `lark-cli attendance --help` | 查询自己的考勤打卡记录 |
| 飞书原生 Markdown 文件 | `lark-markdown` | `lark-cli markdown --help` | 飞书云端原生 `.md` 文件查看、创建、编辑与版本比对（纯本地 `.md` 不触发） |
| 妙搭应用（`/page/`、`*.aiforce.cloud`） | `lark-apps` | `lark-cli apps --help` | Spark/Miaoda 应用创建、静态站点发布、全栈开发、数据库/日志/监控/触发器管理 |
| 实时事件监听（Event Stream） | `lark-event` | `lark-cli event --help` | `lark-cli event consume <EventKey>` 订阅 IM、审批、任务等实时 NDJSON 事件流 |
| 原生 OpenAPI 探索与兜底调用 | `lark-openapi-explorer` | `lark-cli api --help` / `schema --help` | 当现有子命令未封装时，检索开放平台文档并用 `lark-cli api` 调用原生接口 |
| 自定义 Skill 封装与工作流模板 | `lark-skill-maker` | `lark-cli skills --help` | 封装自定义 `lark-cli` 技能；另有内嵌模板 `lark-workflow-meeting-summary`、`lark-workflow-standup-report` |
