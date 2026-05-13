---
name: p4-ops
description: "Perforce helper for the MLBB Unity project. Trigger only when the user explicitly invokes p4-ops by name, e.g. $p4-ops or 调用 p4-ops. Covers P4 status, sync, streams, workspaces, changelists, shelves, diffs, history, export, P4V, SimpleProj, and Lark Project review workflows."
---

# P4 Operations Skill for MLBB Project

## Invoke Policy

Use this skill only after the user explicitly invokes `p4-ops` by name, such as `$p4-ops`, `使用 p4-ops`, or `调用 p4-ops`.

## 项目结构（核心知识）

### 多 Depot 映射

项目使用 **5 个 Depot** 通过 Stream View 映射到同一个 Unity 工程目录：

| Depot | 内容 | 映射到 Workspace |
|-------|------|-------------------|
| `//MLBB` | 主工程（资产、配置、lua、UI 等） | 根目录 `./` |
| `//MLBBArtBridge` | 美术资源（Art_cns, Art_cns_exthigh, Art_exthigh） | `Assets/Art_cns/`, `Assets/Art_cns_exthigh/`, `Assets/Art_exthigh/` |
| `//MLBBClientCode` | C# 代码（MobaBattle, MobaScripts） | `Assets/Scripts/MobaBattle/`, `Assets/Scripts/MobaScripts/` |
| `//MLBBPlugin` | 插件代码（MobaPlugin） | `Assets/Scripts/MobaPlugin/` |
| `//MLBBRelease` | 构建产物 | `Assets/StreamingAssets/` |

**关键点**：切换分支时 Stream spec 会同时切换所有 Depot 的映射，不需要逐个操作。

### 本地路径 → Depot 路径映射

当用户提到本地文件路径时，需要映射到正确的 Depot：

| 本地路径 | 所属 Depot | Depot 路径示例 |
|----------|-----------|----------------|
| `Assets/Scripts/MobaBattle/**` | MLBBClientCode | `//MLBBClientCode/{stream}/Scripts/MobaBattle/...` |
| `Assets/Scripts/MobaScripts/**` | MLBBClientCode | `//MLBBClientCode/{stream}/Scripts/MobaScripts/...` |
| `Assets/Scripts/MobaPlugin/**` | MLBBPlugin | `//MLBBPlugin/{stream}/MobaPlugin/Scripts/...` |
| `Assets/Art_cns/**` | MLBBArtBridge | `//MLBBArtBridge/{stream}/Art_cns/...` |
| `Assets/Art_cns_exthigh/**` | MLBBArtBridge | `//MLBBArtBridge/{stream}/Art_cns_exthigh/...` |
| `Assets/Art_exthigh/**` | MLBBArtBridge | `//MLBBArtBridge/{stream}/Art_exthigh/...` |
| `Assets/StreamingAssets/**` | MLBBRelease | `//MLBBRelease/{stream}/Windows/...` |
| 其它 `Assets/**`, `Tools/**`, etc. | MLBB | `//MLBB/{stream}/...` |

如果不确定某个文件属于哪个 Depot，用 `p4 where <local_path>` 查询。

### 分支命名规则

主干 Stream：`//MLBB/trunk`（各 Depot 类似，如 `//MLBBClientCode/trunk`）

分支从主干周期性创建，命名格式：
- `Android-{大版本}.{小版本}.{构建号}` — 基础分支，如 `Android-2.1.18.1123.1`
- `Android-{版本}_{后缀}` — 特殊用途分支，如：
  - `_loading` — loading 相关
  - `_newplayer05` — 新手相关
  - `_pmh` — 特定功能分支

每个 Depot 都有同名的分支 Stream（如 `//MLBB/Android-2.1.18.1123.1` 和 `//MLBBClientCode/Android-2.1.18.1123.1` 是同一个分支的不同 Depot 部分）。

### 开发者关注目录

C# 程序员日常主要涉及：

| 目录 | 用途 | Depot |
|------|------|-------|
| `Assets/Scripts/` | C# 代码 | MLBBClientCode / MLBBPlugin |
| `Assets/Document/` | 配置文件 | MLBB |
| `Assets/lua/`, `lua_add/`, `lua_hotfix/`, `lua_override/` | Lua 代码 | MLBB |
| `Assets/UI/` | UI 预制件（与 C# 有绑定关系） | MLBB |
| `Assets/Plugins/` | Unity first-pass 代码/资产 | MLBB |
| `Assets/StreamingAssets/` | 流式资产 | MLBBRelease |

### Workspace 特性

- `allwrite` 选项已开启 — 文件默认可写，不需要 `p4 edit` 就能修改
- 因此需要用 `p4 reconcile` 来检测本地未跟踪的变更
- Workspace 名称格式：`MLBB_{用户名}_{编号}`，如 `MLBB_brianzuo_1024`

---

## Helper 脚本

本 skill 自带 `p4_helper.py`，位于本 SKILL.md 同级的 `scripts/` 目录下，封装了日常复合操作。**环境为 Windows**，使用 `python 本Skill目录/scripts/p4_helper.py <command>` 调用。

### 可用命令

| 命令 | 用途 |
|------|------|
| `info` | 显示连接信息、当前 Stream、已打开文件数 |
| `status` | 工作区总览（Stream、已打开文件、pending/shelved CL） |
| `branches [pattern]` | 列出各 Depot 的分支，支持通配符过滤 |
| `latest [N]` | 显示最近 N 个分支（默认 5） |
| `switch <stream> [--code-only]` | 安全切换分支并全量同步（`--code-only` 仅同步代码目录） |
| `sync-code [CL]` | 仅同步代码相关目录（Scripts/Document/lua/UI/Plugins），可选指定 CL |
| `recent [N] [user]` | 显示代码 Depot 的最近 N 条提交记录，可按用户过滤 |
| `depot-map <file>` | 查看本地文件对应的 Depot 路径和版本信息 |
| `safe-shelve` | 检查 pending changes 并提示手动 shelve 命令（只读，不执行 shelve） |
| `find-cl <keyword> [max]` | 在 MLBBClientCode 搜索提交描述匹配关键词的已提交 CL（默认搜最近 200 条） |
| `describe <CL>` | 显示 CL 的描述、影响文件和统一 diff（用于代码 review） |
| `find <pattern>` | 在代码 Depot 中搜索匹配的文件 |
| `blame <file>` | 查看文件逐行归属（annotate） |
| `diff-branch [stream]` | 查看当前分支与 trunk（或指定分支）之间的待集成变更 |
| `export <depot_path> <dir>` | 导出 Depot 目录/文件到本地（不需要 Workspace 映射，自动识别目录并递归导出） |
| `p4vc <action> <target>` | 打开 P4V GUI 窗口（workspacewindow / history / diff） |
| `simpleproj <action> [args]` | 管理瘦身工程（list / pull / switch / update / clean），见下方详细说明 |

### 使用示例

```
# 查看当前状态
python p4_helper.py status

# 列出最近 10 个分支
python p4_helper.py latest 10

# 搜索某版本的分支
python p4_helper.py branches Android-2.1.18.1123*

# 安全切换到分支（默认全量同步）
python p4_helper.py safe-shelve
python p4_helper.py switch //MLBB/Android-2.1.18.1123.1

# 切换分支但仅同步代码目录（节省时间）
python p4_helper.py switch //MLBB/Android-2.1.18.1123.1 --code-only

# 单独同步代码目录（不拉美术资源）
python p4_helper.py sync-code

# 查看某同事最近的提交
python p4_helper.py recent 10 zhangsan

# 查看某文件属于哪个 Depot
python p4_helper.py depot-map Assets/Scripts/MobaBattle/SomeFile.cs

# 用单号搜索 CL（最稳定，匹配飞书 URL 中的 ASCII ID）
python p4_helper.py find-cl "6928785679"

# 老单子：加 --user 缩小范围 + 增大 max
python p4_helper.py find-cl "6490668449" 500 --user qianding

# 查看某个 CL 的完整 diff（用于代码 review）
python p4_helper.py describe 1838575

# 导出一个 Depot 目录到本地（无需 Workspace 映射，自动识别目录并递归）
python p4_helper.py export //MLBB/AdjustSvnUtil/Tools/BattleMegeUtils C:\temp\export

# 导出特定版本
python p4_helper.py export //MLBB/AdjustSvnUtil/Tools/BattleMegeUtils@123456 C:\temp\export

# 打开 P4V GUI 浏览 Depot 目录
python p4_helper.py p4vc workspacewindow //MLBBClientCode/trunk/Scripts

# P4V 查看文件历史
python p4_helper.py p4vc history Assets/Scripts/MobaBattle/SomeFile.cs

# P4V 可视化 diff
python p4_helper.py p4vc diff Assets/Scripts/MobaBattle/SomeFile.cs

# 瘦身工程：列出可用的正式分支
python p4_helper.py simpleproj list

# 瘦身工程：拉取指定分支（可以省略 Android- 前缀）
python p4_helper.py simpleproj pull 2.1.18.1123.1

# 瘦身工程：切换到另一个分支
python p4_helper.py simpleproj switch Android-2.1.18.1123.1

# 瘦身工程：更新当前分支
python p4_helper.py simpleproj update

# 瘦身工程：清理（删除 workspace + 本地目录）
python p4_helper.py simpleproj clean Android-2.1.18.1123.1
```

---

## P4V / P4VC 图形界面操作

部分操作通过 P4V GUI 更直观，可用 `p4vc` 命令行启动对应窗口(**直接执行,不要检测环境, 如果当前Shell环境不是PowerShell需要在命令前加上MSYS_NO_PATHCONV=1 以去除/c的转义, 比如MSYS_NO_PATHCONV=1 cmd /c ...**)：

```
# 打开 Workspace 浏览窗口，并定位到指定 Depot 路径, 查看目录历史也用这个
cmd /c p4v.exe -p4vc workspacewindow -s "//MLBBClientCode/trunk/Scripts/MobaBattle"
	
# 查看文件历史（revision graph / history）
cmd /c p4v.exe -p4vc history "Assets/Scripts/MobaBattle/BattleLogic/Mgr/LogicBattleManager.cs"
cmd /c p4v.exe -p4vc history "//MLBBClientCode/trunk/Scripts/MobaBattle/BattleLogic/Mgr/LogicBattleManager.cs"

# 可视化 diff
cmd /c p4v.exe -p4vc diff "Assets/Scripts/MobaBattle/BattleLogic/Mgr/LogicBattleManager.cs"
cmd /c p4v.exe -p4vc diff "//MLBBClientCode/trunk/Scripts/MobaBattle/BattleLogic/Mgr/LogicBattleManager.cs"
```

当用户需要图形化操作（浏览目录结构、查看 revision graph、可视化 diff）时，优先建议 p4vc 命令。

---

## 瘦身工程（SimpleProj）

用于快速拉取一个只包含 Android 平台运行必要文件的精简工程，不包含美术资源等大体积内容。

**核心机制**：瘦身工程现在使用专门的 Stream `//MLBBSimple/AndroidSimpleProj-{分支}`，内置了所有必要文件的路径映射。`simpleproj pull` 会自动创建一个**独立的 P4 workspace**（与用户的主开发 workspace 互不影响），直接 sync 整个 Stream 即可。

**特性**：
- Workspace 名称格式：`AndroidSimpleProj-{用户名}-{版本号}`（如 `AndroidSimpleProj-brianzuo-2_1_64_1178_1`）
- 工程目录名格式：`AndroidSimpleProj-2.1.64.1178.1`
- 可直接提交修改：`p4 -c <workspace_name> submit`

### 包含内容

瘦身工程 Stream 包含以下文件（通过 import+ 路径映射自动聚合）：

| 类别 | 路径 | 来源 |
|------|------|------|
| 配置 | `Assets/Document/` | MLBB |
| 编辑器 | `Assets/Editor/` | MLBB |
| Lua | `Assets/lua/`, `Assets/lua_add/`, `Assets/lua_hotfix/` | MLBB |
| 插件 | `Assets/Plugins/` | MLBB |
| Shader | `Assets/Shaders/` | MLBB |
| C# 代码 | `Assets/Scripts/` (MobaBattle, MobaScripts, MobaPlugin) | MLBBClientCode / MLBBPlugin |
| 场景 | `Assets/Scenes/Game/` | MLBB |
| Dragon | `Assets/dragon/` | MLBB |
| 流式资产 | `Assets/StreamingAssets/` | MLBBRelease/Android |
| 工程配置 | `Packages/`, `ProjectSettings/` | MLBB |
| 工具 | `Assets/Tools/`, `Tools/` | MLBB |
| 入口文件 | `GameEntry.cs`, `GameResids.cs`, `SplashScreen.cs`, `I18N*.dll`, `link.xml` 等 | MLBB |

**不包含**：Art_cns, Art_exthigh, UI 预制件, RawAssets, Library 等大体积目录。

### 子命令

```bash
# 列出可用的瘦身工程分支
python p4_helper.py simpleproj list

# 拉取指定分支的瘦身工程
python p4_helper.py simpleproj pull Android-2.1.64.1178.1 [目标目录]

# 简写形式（自动补全 Android- 前缀）
python p4_helper.py simpleproj pull 2.1.64.1178.1

# 切换分支（需在瘦身工程目录内执行）
python p4_helper.py simpleproj switch Android-2.1.64.1178.1

# 更新当前瘦身工程到最新
python p4_helper.py simpleproj update

# 清理：删除 workspace 和本地目录
python p4_helper.py simpleproj clean Android-2.1.64.1178.1
```

### 手动操作

如需手动操作 P4 命令：

```bash
# 查看瘦身工程 Stream
p4 stream -o //MLBBSimple/AndroidSimpleProj-2.1.64.1178.1

# 创建 workspace 并绑定到瘦身工程 Stream
p4 client -S //MLBBSimple/AndroidSimpleProj-2.1.64.1178.1 AndroidSimpleProj-brianzuo-2_1_64_1178_1

# 在指定 workspace 中执行操作
p4 -c AndroidSimpleProj-brianzuo-2_1_64_1178_1 sync
p4 -c AndroidSimpleProj-brianzuo-2_1_64_1178_1 reconcile
p4 -c AndroidSimpleProj-brianzuo-2_1_64_1178_1 submit
```

---

## Code Review 工作流

本工作流整合飞书项目（Lark Project MCP）和 P4，实现从待办列表到代码审查到节点流转的完整闭环。

### MLBB 飞书项目信息

| 字段 | 值 |
|------|---|
| project_key | `62c298b6218847b5d28c7675` |
| simple_name | `ml` |
| 工作项类型 | `story`（需求）、`67a5acd9285e67299d0bac29`（客诉/BUG） |
| Review 节点标识 | node_name 包含 `代码review` 或 `前端代码review`，node_state_key 通常为 `ReviewBoard` 或 `state_3` |

### 完整流程

#### 步骤 1：获取 Review 待办

使用 Lark Project MCP 的 `list_todo` 工具拉取当前用户的待办：

```
list_todo(action="todo", page_num=1)
```

从返回结果中筛选 `node_info.node_name` 包含 "代码review" 或 "前端代码review" 的条目，这些就是需要 review 的单子。以表格形式展示给用户：单号、名称、节点名称。

#### 步骤 2：用户选择要 Review 的单子

用户指定单号或关键词后，先通过 `get_workitem_brief` 获取单子详情（角色成员、节点状态等）：

```
get_workitem_brief(work_item_id="<单号>", project_key="62c298b6218847b5d28c7675")
```

#### 步骤 3：搜索对应的 P4 提交

用 **work_item_id** 搜索（CL 描述中的飞书 URL 是 ASCII，不受编码问题影响，最稳定）：

```
# 第一步：直接用单号搜（覆盖最近 ~2 周）
python p4_helper.py find-cl "<单号>"

# 如果没找到（老单子），用开发者用户名缩小范围 + 加大 max
python p4_helper.py find-cl "<单号>" 500 --user <developer_p4_username>
```

**搜索策略**：
1. 先用 `find-cl <单号>`（默认 200 条），能覆盖近 2 周的 CL
2. 找不到时，从 `get_workitem_brief` 的角色成员中提取"经办人"或"前端开发"的 P4 用户名（邮箱前缀），加 `--user` 过滤 + 增大 max 到 500
3. `--user` 利用 P4 的用户索引，不会触发 maxscanrows 限制，可高效搜索老 CL
4. 搜索结果中区分**原始提交**（开发者 workspace）和 **mirror/CI 同步**（mlbb_ci_Lite），review 应关注原始提交

#### 步骤 4：获取 Diff 并 Review

```
python p4_helper.py describe <CL号>
```

获取 diff 后：
1. 阅读 diff 中所有变更
2. 用 Read 工具读取本地对应文件获取完整上下文（文件已同步到 workspace）
3. 基于 diff 和上下文进行代码审查

**Review 关注点**：
- 逻辑正确性（是否解决了单子描述的问题）
- 边界条件和空值检查
- 性能影响（特别是战斗逻辑中的热路径）
- 多个 CL 之间是否有 revert/互相抵消的情况
- 代码风格和可维护性

#### 步骤 5：完成 Review 节点

- **无 P0/P1 问题** → 直接流转节点，不需要询问用户确认：
  ```
  transition_node(work_item_id="<单号>", project_key="62c298b6218847b5d28c7675",
                  node_id="<node_state_key>", action="confirm")
  ```
- **发现 P0/P1 问题** → **不流转该单子的节点**，继续处理下一个单子，最后在汇总中标注
- **无代码提交 / 回退单** → 直接流转，无需 review

### 批量 Review

当用户说"review 我的待办"或"帮我过一下 review 单子"时：
1. 拉取全部 review 待办并列表展示
2. 用户选择范围（全部 / 某个开发者 / 指定单号）
3. 逐个搜索 CL → review diff → 无 P0/P1 直接完成节点
4. **全部完成后**，汇总输出 review 结果表格（单号、名称、开发者、发现的问题/备注）
5. P0/P1 问题的单子在汇总中标注"未完成"并列出具体问题，等待用户指示

### 注意事项

- P4 服务端内容为 UTF-8 编码，p4_helper.py 已配置 UTF-8 输出，中文描述可正常显示
- 如果一个 CL 涉及多个 Depot（如同时改了 MLBBClientCode 和 MLBB），`describe` 会显示所有 Depot 的变更
- `node_state_key` 不固定，需求类通常是 `ReviewBoard`，客诉/BUG 类通常是 `state_3`，以 `get_workitem_brief` 或 `get_node_detail` 返回为准

---

## 项目特有注意事项

1. **切分支前必须清理** — 有 pending changes 时 `switch` 会拒绝执行并提示 shelve 命令，需用户手动执行 `p4 shelve` + `p4 revert` 后再切换。
2. **allwrite 模式下用 reconcile** — 文件始终可写，P4 不自动跟踪本地修改，提交前用 `p4 reconcile` 检测变更。
3. **switch 默认全量同步** — `switch` 切分支后默认执行全量 `p4 sync`。仅在明确需要时使用 `switch --code-only` 只同步代码目录。`sync-code` 命令可单独用于日常增量同步代码。
4. **Depot 路径不要搞混** — `Assets/Scripts/MobaBattle/Foo.cs` 不在 `//MLBB` 里，而在 `//MLBBClientCode` 里。用 `depot-map` 确认。
5. **export 不创建 sync 记录** — 用 `p4 print` 实现，depot 不会认为你 "have" 这些文件，适合临时查看或导出工具脚本。
6. **分支 Stream 名称各 Depot 一致** — 切换到 `//MLBB/Android-X.X.X.X` 时，View 中的 MLBBClientCode 等 Depot 也会自动指向同名分支。

---
