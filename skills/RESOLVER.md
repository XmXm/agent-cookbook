# Agent Cookbook Skill Resolver

This file is the human routing table for active skills in this repository.
`scripts/verify-skills.sh` checks that each active `skills/<name>/SKILL.md`
appears here and that every listed active skill exists.

## Active Routing

### Planning And Design

| Trigger | Skill |
|---|---|
| Rough idea, architecture choice, value judgment, executable plan | `skills/think/SKILL.md` |
| UI, component, page, visual surface, screenshot taste feedback | `skills/design/SKILL.md` |
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
| Completion claim, fixed claim, passing claim | `skills/verification-before-completion/SKILL.md` |

### Content, Web, And External Systems

| Trigger | Skill |
|---|---|
| Writing, editing prose, release notes, bilingual polish | `skills/write/SKILL.md` |
| Push a local Markdown file to Notion | `skills/notion-md-sync/SKILL.md` |

### Git Convenience

| Trigger | Skill |
|---|---|
| Commit all local changes, optionally push | `skills/commitall/SKILL.md` |

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
