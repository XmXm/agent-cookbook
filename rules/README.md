# Rules

## Structure

Rules are intentionally flat: every installable rule lives directly under `rules/`.

```text
rules/
├── common-*.md          # Cross-language defaults and optional workflow notes
├── typescript-*.md      # TypeScript / JavaScript rules
├── python-*.md          # Python rules
├── go-*.md              # Go rules
├── swift-*.md           # Swift rules
├── csharp-*.md          # C# rules
└── markdown-*.md        # Markdown authoring rules
```

Use filename prefixes instead of subdirectories so rules can be copied into tools that expect a single `rules/` directory without overwriting same-named files.

## Installation

Install only the rules that match the project and the agent runtime you actually use.

```bash
# Common rules worth considering for most projects
cp rules/common-git-workflow.md ~/.claude/rules/
cp rules/common-security.md ~/.claude/rules/

# Add language-specific rules as needed
cp rules/typescript-*.md ~/.claude/rules/
cp rules/python-*.md ~/.claude/rules/
cp rules/go-*.md ~/.claude/rules/
cp rules/swift-*.md ~/.claude/rules/
cp rules/csharp-*.md ~/.claude/rules/
cp rules/markdown-*.md ~/.claude/rules/
```

Do not install everything by default. Broad rules consume context and can conflict with repository-local conventions.

## Rules vs Skills

- **Rules** should be durable constraints that are cheap to keep always-on: naming, formatting, security invariants, language-specific conventions.
- **Skills** should hold deep workflows, long examples, agent-routing instructions, and task-specific procedures.
- If a rule mainly says “which agent/tool to use” or repeats a model’s normal senior-engineer behavior, prefer deleting it or moving it into a skill.

## 2026 audit: what is stale vs worth keeping

This audit treats modern coding agents as already capable of planning, searching, testing, and reviewing when the task requires it. Always-on rules should therefore be short, specific, and hard to infer from the local codebase.

| Rule | Recommendation | Why |
| --- | --- | --- |
| `common-agents.md` | Retire | Hard-codes old `~/.claude/agents/` names and mandates proactive agent usage. This is runtime-specific and mostly superseded by skills/tool routing. |
| `common-development-workflow.md` | Retire or convert to a skill | Mandatory GitHub/Exa/package-registry research, planning docs, TDD, review, and push for every feature is too heavy for small changes. Modern agents should scale process to risk. |
| `common-performance.md` | Retire | Model names, capability ratios, keyboard shortcuts, and “extended thinking” settings are runtime/version-specific and will drift quickly. |
| `common-hooks.md` | Optional runtime note | Hook concepts are useful only for Claude Code users maintaining hooks. `TodoWrite` guidance and auto-accept details do not belong in portable project rules. |
| `common-testing.md` | Rewrite before reuse | “80% coverage” and mandatory test-first/E2E for all work are too absolute. Prefer risk-based verification requirements. |
| `common-coding-style.md` | Rewrite before reuse | Some advice is sound, but “always immutable”, fixed function/file size limits, and generic checklists are over-prescriptive and often language- or repo-dependent. |
| `common-patterns.md` | Retire | Repository pattern, API envelope, and skeleton-project search are architectural choices, not universal rules. Let local code and task context decide. |
| `common-security.md` | Keep after trimming | Secret handling, input validation, and injection/XSS/CSRF checks remain valuable, but “rate limiting on all endpoints” and “before ANY commit” should be softened to risk-based wording. |
| `common-git-workflow.md` | Keep | Conventional commit shape and PR diff guidance are compact and still useful. |
| `markdown-mermaid.md` | Keep | The `<br/>` vs `\n` Mermaid note is small, concrete, and easy to forget. |
| `csharp-coding-style.md` | Keep if this is your team style | The naming and “AI Behavior” constraints are specific enough to be useful; they are not universal C# conventions, so install only in matching projects. |
| `go-coding-style.md` | Keep | `gofmt`, small interfaces, and contextual error wrapping are idiomatic and stable. |
| `go-security.md` | Keep | `gosec`, environment secrets, and context timeouts are practical Go-specific checks. |
| `go-testing.md` | Keep with nuance | `go test`, table-driven tests, race detector, and coverage commands are useful; avoid requiring `-race` for every tiny edit if it is too slow. |
| `go-patterns.md` | Optional | Functional options, local interfaces, and constructor DI are useful patterns, but should not be forced on simple code. |
| `go-hooks.md` | Optional runtime note | Formatter/linter hooks are useful but environment-specific. Prefer repository scripts when available. |
| `python-coding-style.md` | Keep | PEP 8, type annotations, Black/isort/Ruff are still standard enough to be useful. |
| `python-testing.md` | Keep | Pytest and coverage command examples are concise and stable. |
| `python-security.md` | Keep with caution | Bandit and env-based secrets are useful; `python-dotenv` should be project-dependent, not required globally. |
| `python-patterns.md` | Optional | Protocols, dataclasses, context managers, and generators are useful reminders, but modern models usually infer them from context. |
| `python-hooks.md` | Optional runtime note | Useful only if the target environment supports these hooks. |
| `swift-coding-style.md` | Keep | SwiftFormat/SwiftLint, value semantics, Apple naming, typed throws, and strict concurrency remain current. |
| `swift-patterns.md` | Keep | Protocol-oriented design, `Sendable`, actors, and DI are still high-value Swift guidance. |
| `swift-security.md` | Keep | Keychain, ATS, certificate validation, and input validation remain important. |
| `swift-testing.md` | Keep | Swift Testing is the right default for new Swift tests. |
| `swift-hooks.md` | Optional runtime note | Useful if hooks are configured; otherwise repository scripts should drive formatting/linting. |
| `typescript-coding-style.md` | Keep after trimming | Immutable updates, validation, and logging are useful, but Zod and try/catch examples should be project-dependent. |
| `typescript-security.md` | Keep | Environment-secret handling is small and durable. |
| `typescript-testing.md` | Optional | Playwright is a strong E2E default for web apps, but this file is too thin to be a general testing rule. |
| `typescript-patterns.md` | Retire or move to skill | API envelopes, React hooks, and repository interfaces are framework/application patterns, not global rules. |
| `typescript-hooks.md` | Optional runtime note | Formatter/typecheck hooks are useful only when the runtime supports them. |

## Suggested always-on set

Start small, then add project-specific rules only when they prevent repeated mistakes:

- `common-git-workflow.md`
- `common-security.md` after trimming absolutes
- `markdown-mermaid.md` for Markdown-heavy repos
- Language-specific coding/security/testing rules for the project stack
- Team-specific rules such as `csharp-coding-style.md` only where they are truly expected

Avoid always-on installation of agent orchestration, performance/model-selection, broad workflow, generic patterns, and hook configuration rules unless the target runtime explicitly depends on them.

## Adding a New Rule

1. Put the file directly under `rules/`.
2. Prefix it by scope, for example `rust-coding-style.md`, `rust-testing.md`, or `common-security.md`.
3. Add `paths:` frontmatter when the rule should only apply to matching files.
4. Keep the rule short and durable. If it needs long examples or a multi-step workflow, make it a skill instead.
