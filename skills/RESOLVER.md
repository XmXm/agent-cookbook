# Agent Cookbook Skill Resolver

This file is the human routing table for active skills in this repository.
`scripts/verify-skills.sh` checks that each active `skills/<name>/SKILL.md`
appears here and that every listed active skill exists.

## Active Routing

### Planning And Design

| Trigger | Skill |
|---|---|
| Rough idea, architecture choice, value judgment, executable plan | `skills/think/SKILL.md` |
| Simplest working solution, cut over-engineering, YAGNI, minimal diff | `skills/lazy/SKILL.md` |
| UI, component, page, visual surface, screenshot taste feedback | `skills/design/SKILL.md` |
| Scan codebase for architecture deepening opportunities | `skills/improve-codebase-architecture/SKILL.md` |
| Deep-module design vocabulary: module, interface, depth, seam, adapter | `skills/codebase-design/SKILL.md` |
| Pin down domain terminology / ubiquitous language, record ADRs | `skills/domain-modeling/SKILL.md` |
| Relentless one-question-at-a-time interview to stress-test a plan | `skills/grilling/SKILL.md` |
| Compact the current conversation into a handoff doc for another agent | `skills/handoff/SKILL.md` |
| File-based planning under `.plans/` | `skills/planning-in/SKILL.md` |
| Show active `.plans/` work | `skills/planning-in-status/SKILL.md` |
| Remove stale or completed `.plans/` work | `skills/planning-in-remove/SKILL.md` |
| Reorganize planning documents for structure | `skills/planning-organize/SKILL.md` |
| Split large planning documents into task files | `skills/planning-split/SKILL.md` |
| Multi-agent review of plans or completed plan code | `skills/planning-review/SKILL.md` |

### Debug, Review, And Verification

| Trigger | Skill |
|---|---|
| Error, crash, regression, failing test, unexpected behavior | `skills/hunt/SKILL.md` |
| Diff review, merge readiness, release follow-through, issue or PR triage | `skills/check/SKILL.md` |
| C# naming and style scan | `skills/cs-style-check/SKILL.md` |

### Content And Web

| Trigger | Skill |
|---|---|
| Writing, editing prose, release notes, bilingual polish | `skills/write/SKILL.md` |
| Push a local Markdown file to Notion | `skills/notion-md-sync/SKILL.md` |
| Open/read/summarize a URL, web search, research, clip an article | `skills/webforage/SKILL.md` |

### Lark / Feishu

| Trigger | Skill |
|---|---|
| First-time lark-cli setup, auth login, identity switch, scope errors | `skills/lark-shared/SKILL.md` |
| Resolve a name/email to open_id, or look up a person by open_id | `skills/lark-contact/SKILL.md` |
| Look up P2P chat history with a specific person | `skills/finding-lark-chat-history/SKILL.md` |
| Send/reply messages, manage group chats, up/download chat files | `skills/lark-im/SKILL.md` |
| Real-time event listening/subscribing (NDJSON stream) | `skills/lark-event/SKILL.md` |
| Read/edit Feishu Docx / Wiki documents | `skills/lark-doc/SKILL.md` |
| Create/operate Feishu spreadsheets (Sheets) | `skills/lark-sheets/SKILL.md` |
| Operate Feishu Bitable (多维表格 / Base) | `skills/lark-base/SKILL.md` |
| Create/edit Feishu slides | `skills/lark-slides/SKILL.md` |
| Query/edit Feishu whiteboards (画板) | `skills/lark-whiteboard/SKILL.md` |
| Manage Feishu tasks, lists, and task agents | `skills/lark-task/SKILL.md` |
| Feishu approvals: query and act on approval tasks | `skills/lark-approval/SKILL.md` |
| Manage calendar events and meeting rooms | `skills/lark-calendar/SKILL.md` |
| Search/operate/generate Minutes (妙记) | `skills/lark-minutes/SKILL.md` |
| View/create/edit/compare Feishu Markdown files | `skills/lark-markdown/SKILL.md` |
| Import a whole local `.md` into a Feishu doc (mermaid → 画板) | `skills/markdown-to-lark-doc/SKILL.md` |
| Draw architecture diagrams as editable Lark whiteboard (画板) nodes | `skills/architecture-to-lark-whiteboard/SKILL.md` |
| Find/call raw Feishu OpenAPI not wrapped by a CLI command | `skills/lark-openapi-explorer/SKILL.md` |
| Build a custom lark-cli skill | `skills/lark-skill-maker/SKILL.md` |

### Git And Ops

| Trigger | Skill |
|---|---|
| Commit all local changes, optionally push | `skills/commitall/SKILL.md` |
| Sync parent repo and tracked-branch submodules, push safely | `skills/git-remote-sync/SKILL.md` |
| Manage Docker/Compose on the remote Windows WSL host | `skills/pc-wsl-docker/SKILL.md` |

## Legacy

These skills are parked under `legacy/` because active Waza skills now
cover the same workflow:

| Legacy skill | Active replacement |
|---|---|
| `legacy/brainstorming/SKILL.md` | `skills/think/SKILL.md` |
| `legacy/systematic-debugging/SKILL.md` | `skills/hunt/SKILL.md` |
| `legacy/p4-ops/SKILL.md` | Project-local Perforce workflow |

## Routing Notes

- Read the matched skill before acting.
- When several skills match, choose the most specific workflow.
- For completed implementation work, use `check`; for broken behavior, use `hunt`.
- For UI taste and composition work, use `design`; for UI regressions, use `hunt`.
