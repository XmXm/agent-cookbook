---
name: nmem-save
description: "nmem 记忆保存与管理规范：先搜后存去重、update/supersede/deprecate 分流、unit-type 与 importance 分级、禁止自建 space。Use whenever an agent is about to run nmem m add / memories add, or the user says 写回 nmem、记到记忆、存个记忆、沉淀决策、remember this、save this insight/decision. Not for battle domain facts (use kb-search / battle-debug-write-knowledge), not for session handoff docs (use handoff or nmem t create), and not for reading memories (read side lives in shared knowledge-preflight)."
---

# nmem-save: 记忆保存与管理

nmem 是个人决策、偏好、程序性经验的长期记忆层。这份规范管写入端；
读取端（preflight）的契约在仓根 `shared/knowledge-preflight.md`，
本 skill 是「环」的另一半：决策产生后按此写回。

## 1. 先判断值不值得存

存：跨会话仍然成立的个人决策、偏好、教训、可复用的操作程序。
不存：

- 会话内琐事、一次性状态（下次会话没人需要）
- 代码本身或 git 里已有的东西（记"为什么"，不记"是什么"）
- 战斗领域事实、配置关系、案例 → 归 Battle KB（`/kb-search` 的写入侧
  `/battle-debug-write-knowledge`），nmem 只放个人层
- 密钥、token、密码等敏感信息 — 永远不存

## 2. 先搜后存（去重门）

每次 add 之前必须先搜，防止重复与自相矛盾：

```bash
nmem --json m search "<主题关键词>" -n 5
```

按结果分流：

| 搜索结果 | 动作 |
|---|---|
| 无相关记忆 | 新增（见第 3 节） |
| 已有且仍正确 | 不存；确有关联可 `nmem m link add` |
| 已有但小幅过时（措辞、细节） | `nmem m update <id> -c "<新内容>"` 原地改 |
| 已有但被新决策实质替代 | 新增一条，然后 `nmem m supersede <old-id> <new-id> --reason "<为什么替代>"` |
| 已有但已经错了、无替代 | `nmem m deprecate <id> --reason "<为什么不再成立>"` |

历史教训：agent 曾把同一条"Automations 模块架构"存了两遍——跳过搜索
就会制造这种重复。

## 3. 新增记忆的字段规范

```bash
nmem --json m add "<自包含正文>" \
  -t "<一句话结论式标题>" \
  --unit-type <type> -i <importance> -s droid
```

- **标题**：带结论，不是主题词。写"LogicThread barrier 必须识别帧内
  战斗自停为合法出口"，不写"LogicThread 笔记"。
- **正文自包含**：不写"如上所述/本次会话"，未来读者没有上下文。
  背景、结论、理由三要素齐。
- **unit-type**（不要全部默认成 fact）：

  | 类型 | 用于 |
  |---|---|
  | decision | 拍板的取舍及理由（最常用） |
  | preference | 用户偏好、口味 |
  | procedure | 可复用的操作步骤 |
  | learning | 踩坑教训、调试结论 |
  | fact | 稳定的客观事实 |
  | plan / context / event | 计划、背景、带日期的事件 |

- **importance 阶梯**：0.5 常规；0.7 正式决策、月报级结论；0.85+
  支柱级（影响整个工作方式的决定）。不要无脑全 0.8。
- **来源标签**：Droid 会话用 `-s droid`，便于日后按来源审计。

## 4. 硬约束

- **禁止 `--space`，禁止创建空间**。2026-07-05 已定：单一 Default
  空间，spaces 功能整体关闭。此前 agent 自建的 5 个空间造成知识碎片化，
  已全部合并回 Default。除非用户明说，永远不带空间参数。
- **不用 delete 清理**。错了用 deprecate（留审计），被替代用 supersede
  （留链路）；delete 只在用户明确要求时执行。

## 5. m add 与 t create 的分工

- `m add`：沉淀单条可检索的知识（本 skill 的对象）。
- `nmem --json t create -t "Session Handoff - <topic>" -c "Goal/Decisions/Files/Risks/Next" -s droid`：
  会话交接检查点，整段上下文打包，不做去重分流。两者不互相替代。

## 6. 降级

nmem 不可达（server 未启动、命令不存在）→ 明说"nmem 不可用，本次
不写回"，继续主任务。写回失败永远不阻塞正事。
