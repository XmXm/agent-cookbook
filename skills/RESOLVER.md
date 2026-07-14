# Agent Cookbook Skill Resolver

This file is the human routing table for active skills in this repository.
`scripts/verify-skills.sh` checks that each active `skills/<name>/SKILL.md`
appears here and that every listed active skill exists.

## Active Routing

### Front Doors

Four self-contained work entry points (plan → check → hunt → write-document).
Each covers one phase of a task; they do not chain automatically.

| Trigger | Skill |
|---|---|
| Rough idea, architecture, value judgment, refactor plan, plan stress-test, acceptance | `skills/plan/SKILL.md` |
| Diff review, merge readiness, plan execution ("按计划实施"), release follow-through, project audit | `skills/check/SKILL.md` |
| Error, crash, regression, failing test, broken behavior, screenshot-reported defect | `skills/hunt/SKILL.md` |
| Structured document creation: README, design doc, postmortem, weekly report, KB knowledge, Feishu delivery | `skills/write-document/SKILL.md` |

### Coding Guides

| Trigger | Skill |
|---|---|
| Authoring/modifying MLBB battle C# (naming, frame-sync, hot-path GC, object pool, ISHOW, feature flags) — read before writing | `skills/cs-coding/SKILL.md` |

### Delegation

| Trigger | Skill |
|---|---|
| User explicitly invokes `/delegate` only (never auto-routed): ROI-gated dispatch to external coding agents (codex / kimi / pi / copilot), concurrent multi-instance capable; Claude plans + routes + accepts | `skills/delegate/SKILL.md` |

### Design And Style

| Trigger | Skill |
|---|---|
| Simplest working solution, cut over-engineering, YAGNI, minimal diff | `skills/lazy/SKILL.md` |
| UI, component, page, visual surface, screenshot taste feedback | `skills/ui/SKILL.md` |

### Knowledge

| Trigger | Skill |
|---|---|
| Search the battle knowledge base for patterns, cases, config relations, postmortems | `skills/kb-search/SKILL.md` |
| Saving memories to nmem (m add / 写回 nmem / 记到记忆 / remember this): search-first dedupe, update/supersede/deprecate routing, unit-type and importance grading, no spaces | `skills/nmem-save/SKILL.md` |
| Compress the current session into a handoff doc for a fresh session (session-level; task-level tracking lives in plan's `.plans/`) | `skills/handoff/SKILL.md` |
| Monthly skill usage observation: transcript stats, miss/misfire sampling, nmem monthly report writeback | `skills/skill-usage-report/SKILL.md` |

### Content And Web

| Trigger | Skill |
|---|---|
| Writing, editing prose, release notes, bilingual polish, remove AI tone | `skills/write/SKILL.md` |
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
| Read/fetch Feishu Project (Meego) bug/story work items | `skills/lark-proj/SKILL.md` |
| Generate/publish story closeout comments, finish owned nodes | `skills/lark-story-closeout/SKILL.md` |

### Git And Ops

| Trigger | Skill |
|---|---|
| Open or summarize diffs in Beyond Compare from Git, P4, SVN, unified diff text, or explicit left/right paths | `skills/bcompare-diff/SKILL.md` |
| Full git sync pipeline ("git-sync", "同步主仓和子仓", "commitall"): commit submodule + parent work, pull with rebase, refresh third-party ref submodules, commit pointer bumps, push submodules before parent — editors always disabled | project-level `.claude/skills/git-sync` (this repo only) |
| Manage Docker/Compose on the remote Windows WSL host | `skills/pc-wsl-docker/SKILL.md` |

## Legacy

These skills are parked under `legacy/` because an active skill or workflow
now covers the same need:

| Legacy skill | Active replacement |
|---|---|
| `legacy/brainstorming/SKILL.md` | `skills/plan/SKILL.md` (Design mode) |
| `legacy/systematic-debugging/SKILL.md` | `skills/hunt/SKILL.md` |
| `legacy/p4-ops/SKILL.md` | Project-local Perforce workflow |
| `legacy/cs-style-check/SKILL.md` | `skills/cs-coding/SKILL.md` (C# authoring); review via `check` / `p4-review` |
| `legacy/planning-in/SKILL.md` | `skills/plan/SKILL.md` (Persist the Plan) |
| `legacy/planning-in-remove/SKILL.md` | `skills/plan/SKILL.md` |
| `legacy/planning-in-status/SKILL.md` | `skills/plan/SKILL.md` |
| `legacy/planning-organize/SKILL.md` | `skills/plan/SKILL.md` |
| `legacy/planning-review/SKILL.md` | `skills/plan/SKILL.md` (Grill / Review modes) |
| `legacy/planning-split/SKILL.md` | `skills/plan/SKILL.md` |
| `legacy/commitall/SKILL.md` | project-level `.claude/skills/git-sync` ("只提交" partial run) |
| `legacy/git-remote-sync/SKILL.md` | project-level `.claude/skills/git-sync` (full pipeline) |
| `legacy/git-sync/SKILL.md` (v1, user-level Commit/Sync modes) | project-level `.claude/skills/git-sync` (fixed five-step pipeline incl. third-party submodule refresh; repo-local, not distributed via `~/.agents`) |
| `refs/Waza/skills/think` (upstream, unlinked) | `skills/plan/SKILL.md` (think skeleton internalized; Lightweight/Triage/attack angles ported) |

## Routing Notes

- Read the matched skill before acting.
- When several skills match, choose the most specific workflow.
- For completed implementation work, use `check`; for broken behavior, use `hunt`.
- For UI taste and composition work, use `ui` (upstream Waza renamed `design` → `ui` at df08298 to stop shadowing Claude Code's built-in `/design`); for UI regressions, use `hunt`.
- `write-document` creates structured documents; `write` polishes/rewrites prose and removes AI tone. They do not overlap.
- `plan` produces the plan; `check` Plan Execution mode implements it. `plan` does not write code.
