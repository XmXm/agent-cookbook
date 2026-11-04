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
| Rough idea, architecture, value judgment, refactor plan, plan stress-test, acceptance, detached check (交接检查) of a persisted plan | `skills/plan/SKILL.md` |
| User explicitly invokes `/check` or asks for a code review ("review 一下"); other modes (plan execution, release gate, project audit) only via `/check`; never auto-triggered | `skills/check/SKILL.md` |
| Error, crash, regression, failing test, broken behavior, screenshot-reported defect | `skills/hunt/SKILL.md` |
| Documents and prose: create, rewrite, polish, review, remove AI tone (design doc, weekly report, postmortem, README, runbook, KB, release notes, social copy) | `skills/write-document/SKILL.md` |

### Coding Guides

| Trigger | Skill |
|---|---|
| Authoring/modifying MLBB battle C# (naming, frame-sync, hot-path GC, object pool, ISHOW, feature flags) — read before writing | `skills/cs-coding/SKILL.md` |

### Delegation

| Trigger | Skill |
|---|---|
| User explicitly invokes `/delegate` only (never auto-routed): ROI-gated dispatch to coding agents (default: Claude Code opus subagent; codex / kimi / pi / copilot when the user names one), concurrent multi-instance capable; Claude plans + routes + accepts | `skills/delegate/SKILL.md` |

### Design And Style

| Trigger | Skill |
|---|---|
| UI, component, page, visual surface, screenshot taste feedback | `skills/ui/SKILL.md` |

### Knowledge

| Trigger | Skill |
|---|---|
| Search the battle knowledge base for patterns, cases, config relations, postmortems | `skills/kb-search/SKILL.md` |
| Saving memories to nmem (m add / 写回 nmem / 记到记忆 / remember this): search-first dedupe, update/supersede/deprecate routing, unit-type and importance grading, no spaces | `skills/nmem-save/SKILL.md` |
| Compress the current session into a handoff doc for a fresh session (session-level; making a persisted plan executable by a fresh session is plan's Detached check) | `skills/handoff/SKILL.md` |
| User invokes `/skill-usage-report` only: monthly skill usage observation, miss/misfire sampling, nmem monthly report writeback | `skills/skill-usage-report/SKILL.md` |

### Content And Web

| Trigger | Skill |
|---|---|
| Open/read/summarize a URL, web search, research, clip an article | `skills/webforage/SKILL.md` |

### Lark / Feishu

| Trigger | Skill |
|---|---|
| Feishu / Lark general CLI operations (incl. P2P chat history lookup via `references/p2p-chat-history.md`): Docx / Wiki / Drive / Sheets / Base (Bitable) / Slides / Whiteboard / IM messages & group chats / Contact lookup / Calendar / Meeting & Minutes / Task / Approval / Mail / OKR / Attendance / native Markdown / Miaoda Apps / Event stream / auth & config / raw OpenAPI | `skills/lark-cli/SKILL.md` |
| Import a whole local `.md` into a Feishu doc (mermaid → 画板) | `skills/markdown-to-lark-doc/SKILL.md` |
| Read/fetch Feishu Project (Meego) bug/story work items | `skills/lark-proj/SKILL.md` |
| Generate/publish story closeout comments, finish owned nodes | `skills/lark-story-closeout/SKILL.md` |

### Git And Ops

| Trigger | Skill |
|---|---|
| User invokes `/bcompare-diff` only: open or summarize diffs in Beyond Compare from Git, P4, SVN, unified diff text, or explicit left/right paths | `skills/bcompare-diff/SKILL.md` |
| Full git sync pipeline ("git-sync", "同步主仓和子仓", "commitall"): commit nested-repo (mt-skills) + parent work, pull with rebase, refresh third-party ref clones via update-refs, push — editors always disabled | project-level `.claude/skills/git-sync` (this repo only) |

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
| `legacy/git-sync/SKILL.md` (v1, user-level Commit/Sync modes) | project-level `.claude/skills/git-sync` (fixed four-step pipeline incl. third-party clone refresh; repo-local, not distributed via `~/.agents`) |
| `refs/Waza/skills/think` (upstream, unlinked) | `skills/plan/SKILL.md` (think skeleton internalized; Lightweight/Triage/attack angles ported) |
| `legacy/pc-wsl/SKILL.md` (ex `pc-wsl-docker`) | none — parked; its broad SSH/remote-machine triggers over-matched. Revive from `legacy/` if the PC/WSL workflow returns |
| `legacy/lazy/SKILL.md` | `skills/plan/SKILL.md` (simplicity ladder `references/lazy-ladder.md`, 苟 mode) |
| `legacy/notion-md-sync/SKILL.md` | none — Notion no longer a delivery target; docs go to Feishu via `skills/markdown-to-lark-doc/SKILL.md` |
| `legacy/finding-lark-chat-history/SKILL.md` | `skills/lark-cli/SKILL.md` (`references/p2p-chat-history.md`) |
| `legacy/architecture-to-lark-whiteboard/SKILL.md` (+ its `legacy/architecture-diagram/` design-system dependency) | none — parked for low use; revive from `legacy/` if needed |

## Routing Notes

- Read the matched skill before acting.
- When several skills match, choose the most specific workflow.
- `check` is user-invoked only: `/check` or an explicit code review request ("review 一下"). Never enter it from commit/push, release, or "按计划实施" wording. For broken behavior, use `hunt`.
- For UI taste and composition work, use `ui` (upstream Waza renamed `design` → `ui` at df08298 to stop shadowing Claude Code's built-in `/design`); for UI regressions, use `hunt`.
- `write-document` owns the whole writing door: creating, rewriting, polishing, and reviewing documents and prose. There is no separate polish skill.
- `plan` produces the plan; implementation happens directly, or through `check` Plan Execution mode when the user invokes `/check`. `plan` does not write code.
