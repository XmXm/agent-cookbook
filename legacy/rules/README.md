# Rules (Retired)

> **Retired 2026-07-02.** Content folded into `mt-skills/shared/` and skill
> references. The `~/.claude/rules` symlink has been removed; rules are no
> longer loaded by the agent runtime. Files are preserved here for reference.
>
> **Where the content went:**
>
> | Rule file | New location |
> |---|---|
> | common-coding-style, common-security, common-testing | `mt-skills/shared/common-core.md` |
> | python-\*, go-\* | `mt-skills/shared/languages.md` |
> | markdown-mermaid | `mt-skills/skills/write-document/SKILL.md` (inline) |
> | csharp-coding-style | `mt-skills/skills/cs-coding/SKILL.md` (folded earlier) |
> | typescript-\* | No active consumer — archived as-is |

---

*Original README below for reference.*

Portable, always-on rule files. Each is short, durable, and hard for a model to
infer from the local codebase. Anything project-specific belongs in that
project's own config, not here.

## Structure

Rules are intentionally flat: every installable rule lives directly under `rules/`.

```text
rules/
├── common-*.md          # Cross-language defaults
├── typescript-*.md      # TypeScript / JavaScript rules
├── python-*.md          # Python rules
├── csharp-*.md          # C# rules
├── go-*.md              # Go rules
└── markdown-*.md        # Markdown authoring rules
```

Filename prefixes (not subdirectories) so rules can be copied into a single
`rules/` directory without same-named files overwriting each other.

## Installation

Install only the rules that match the project stack and the agent runtime you
actually use.

```bash
cp rules/common-*.md ~/.claude/rules/
cp rules/python-*.md ~/.claude/rules/     # add language rules as needed
```

Don't install everything by default — broad rules consume context and can
conflict with repository-local conventions.

## Rules vs Skills

- **Rules** = durable constraints cheap to keep always-on: naming, formatting,
  security invariants, language conventions.
- **Skills** = deep workflows, long examples, agent-routing, task procedures.
- If a rule mainly says "which agent/tool to use" or just repeats a modern
  model's normal senior-engineer behavior, delete it or move it into a skill.

## Current set (after 2026-06 cleanup)

Baseline: treat a modern coding agent (Opus 4.8-class) as already able to plan,
search, test, and review. An always-on rule earns its place only if removing it
would make that agent measurably worse — i.e. it encodes a non-inferrable,
cross-project, durable constraint.

Kept:

| Rule | Why it stays |
| --- | --- |
| `common-coding-style.md` | Soft immutability + small-files leaning (language rules may override). |
| `common-security.md` | Secret hygiene, untrusted-input validation, injection/XSS guardrails. |
| `common-testing.md` | Risk-based testing posture (no fixed coverage gate). |
| `python-coding-style.md` / `python-security.md` / `python-testing.md` | ruff, bandit, pytest+markers. |
| `go-security.md` / `go-testing.md` | gosec + govulncheck; table-driven/race/cover. |
| `markdown-mermaid.md` | Mermaid `<br/>` vs `\n` gotcha — one line, model gets it wrong. |

Retired (deleted as model-default redundancy, runtime-coupling, or stale model
facts):

- `common-performance.md` — hardcoded model versions / capability ratios / Claude Code shortcuts (drifts every release).
- `common-hooks.md`, `typescript-hooks.md`, `python-hooks.md`, `go-hooks.md`, `swift-hooks.md` — runtime hook config, not portable rules.
- `common-patterns.md`, `typescript-patterns.md`, `python-patterns.md`, `go-patterns.md` — textbook patterns / architectural choices, not universal rules.
- `common-development-workflow.md` — heavy per-feature workflow with hardcoded agent names; belongs in a skill.
- `go-coding-style.md` — Go textbook consensus with no project-specific constraint.
- `typescript-security.md` — only demoed the most basic env-var practice.
- `common-git-workflow.md` — conventional-commit format a modern model already follows by default.
- `swift-coding-style.md`, `swift-security.md`, `swift-testing.md`, `swift-patterns.md` — Swift is not in the active stack.
- `csharp-coding-style.md` — folded into the `cs-coding` skill (authoring guide) as its naming/formatting core. The rule form was retired because some agent runtimes don't load `rules/`; a skill is portable. The battle-core `_camelCase`/`m_Type` convention now lives in that skill.

## Adding a New Rule

1. Put the file directly under `rules/`.
2. Prefix it by scope, e.g. `rust-coding-style.md`, `rust-testing.md`.
3. Add `paths:` frontmatter when the rule should only apply to matching files.
4. Keep it short and durable. If it needs long examples or a multi-step
   workflow, make it a skill instead.
