# AGENTS.md

Guidance for coding agents working in **agent-cookbook** — a personal,
deployable collection of agent skills, rules, and scripts.

## What this repo is

This repo is the source of truth for the skills the user runs day to day. It is
symlinked into the agent runtime:

```text
~/.agents/skills  ->  /Users/ansz/dev/agent-cookbook/skills
```

Editing `skills/` here changes what the agent loads. There is no build step and
no deploy — the symlink makes changes live immediately.

## Layout

```text
agent-cookbook/
├── skills/           # ACTIVE skills (own dirs + symlinks into refs/ or mt-skills/)
│   └── RESOLVER.md   # human routing table; every active skill must be listed here
├── mt-skills/        # user's own shared skill submodule (editable; not third-party)
│   ├── skills/       # four front doors + cs-coding + kb-search + lark-proj + lark-story-closeout + bcompare-diff
│   └── shared/       # cross-skill base conventions (common-core, languages, knowledge-preflight, etc.)
├── refs/             # third-party repos as git submodules (read-only references)
├── scripts/          # verify-skills.sh (contract checker), update-submodules.sh
└── legacy/           # parked skills and retired rules
    └── rules/        # retired always-on rule files (content folded into shared/ and skills)
```

Ownership:

- `skills/`, `scripts/`, `legacy/` — the user's own / reused content. Edit freely.
- `mt-skills/` — the user's own shared skills, tracked as a submodule so they can
  be reused elsewhere. Edit here when changing those skills, then commit and push
  inside `mt-skills/` before committing the parent repo pointer.
- `refs/` — **third-party submodules**. Do not hand-edit; they are upstream code
  pulled in for reference and for symlink targets. Treat `refs/` as read-only;
  only update it by moving submodule pointers via the script below.

## Front Doors

Four self-contained work entry points plus a coding guide, all in
`mt-skills/skills/` and symlinked into `skills/`:

| Door | What it does |
|---|---|
| `plan` | Design, evaluate, refactor-plan, grill, acceptance. Produces the plan; does not implement code. |
| `check` | Code review, plan execution ("按计划实施"), release follow-through, project audit. |
| `hunt` | Root-cause diagnosis for errors, regressions, broken behavior. |
| `write-document` | Structured document creation (README, design doc, postmortem, weekly report, KB knowledge, Feishu delivery). |
| `cs-coding` | C# authoring guide for MLBB battle core — read before writing. |

Each door embeds a knowledge preflight (nmem + KB via `/kb-search`) and project
routing (to battle-debug, p4-review, etc.) at fixed nodes. The shared base
conventions live in `mt-skills/shared/` and are referenced via per-skill
`shared -> ../../shared` symlinks.

## Methodology & Maintenance

Full methodology: `mt-skills/METHODOLOGY.md` (门·证·环·剃). Condensed:

- **门 (Doors)** — entry points cut by task lifecycle: `plan` before code,
  `cs-coding` while writing, `check` after, `hunt` when broken,
  `write-document` to record. Every skill declares what it is NOT for and
  names its neighbor.
- **证 (Evidence)** — conclusions must be auditable: graded evidence strength,
  live values over memory, verification run in-session.
- **环 (Loop)** — knowledge preflight (nmem + KB) before substantive work,
  decisions written back to nmem after. The flywheel needs both ends.
- **剃 (Razor)** — a skill or rule exists only if deleting it would make a
  modern agent measurably worse. Reuse ladder: symlink upstream → fork and
  strip → distill ideas only.

Daily flows: bug → `hunt` (→ project battle-debug family); feature → `plan` →
"按计划实施" → `check`; documents → `write-document`.

Maintenance cadence:

| Trigger | Action |
|---|---|
| Skill or RESOLVER change | `bash scripts/verify-skills.sh` (see Validation) |
| mt-skills change | Commit/push submodule first, then parent pointer (see Submodules) |
| `update-submodules.sh` run | Skim upstream deltas (esp. Waza); distill worthwhile ideas into own skills, do not re-link |
| Monthly | Run `/skill-usage-report`: stats vs baseline, miss/misfire sampling, monthly report into nmem |
| Pillar-level decision lands | Sync `mt-skills/METHODOLOGY.md` — decision-driven, never calendar-driven |
| New skill proposed | Deletion test + Codex 2% context budget check first |

## Skills

A skill is a directory under `skills/` containing `SKILL.md` (plus optional
`references/`, `agents/`, `scripts/` subdirs). Two kinds coexist:

- **Own skills** — real directories (e.g. `commitall`, `markdown-to-lark-doc`,
  `pc-wsl-docker`).
- **Symlinked skills** — symlinks into `mt-skills/` for the user's shared skills
  (front doors, cs-coding, kb-search, lark-proj, lark-story-closeout,
  bcompare-diff), or into `refs/` submodules for upstream skills (`design`,
  `write` → `refs/Waza`; `lark-*` → `refs/lark-skills`).

### SKILL.md contract (enforced by `scripts/verify-skills.sh`)

- Must start with `---` YAML frontmatter containing non-empty `name` and `description`.
- `name` must exactly match the directory name.
- No duplicate skill names; symlinks must not be broken.
- Every active skill must be listed in `skills/RESOLVER.md` as `skills/<name>/SKILL.md`.
- `RESOLVER.md` must not reference a skill that no longer exists.
- Relative `references/…`, `agents/…`, `scripts/…` mentions and Markdown links
  must resolve to real files.
- Markdown table rows must not contain unescaped `|`.

### Adding or changing a skill

1. Create `skills/<name>/SKILL.md` with matching `name` frontmatter (or symlink
   an upstream skill from `refs/`, or a user-owned shared skill from `mt-skills/`).
2. Add a routing row in `skills/RESOLVER.md`.
3. Run `bash scripts/verify-skills.sh` until it passes.

## Rules (Retired)

`rules/` has been moved to `legacy/rules/`. Its content was folded into
`mt-skills/shared/` (common-core, languages) and individual skill references
(cs-coding, write-document). The `~/.claude/rules` symlink has been removed.
See `legacy/rules/README.md` for the full mapping.

## Submodules

`mt-skills/` is a user-owned submodule, not a third-party reference. It may be
edited directly. When it changes, commit and push `mt-skills/` first, then commit
the parent repo's submodule pointer update.

### Third-party submodules (`refs/`)

Third-party repos pinned as submodules (`Waza`, `mattpocock-skills`,
`lark-skills`, `hai-stack`, `ponytail`). Update with:

```bash
scripts/update-submodules.sh   # git submodule update --remote --merge
```

After cloning, init submodules so symlinked skills resolve:
`git submodule update --init --recursive`.

## Validation

Always run before committing skill or resolver changes:

```bash
bash scripts/verify-skills.sh
```

It validates the SKILL.md contract, legacy parking, RESOLVER coverage, link
integrity, and table formatting across all active skills.

> Known false positive: the link checker flags `![Image](img_xxx)`, a doc
> example inside the read-only `refs/lark-skills` submodule
> (`skills/lark-im/references/lark-im-chat-messages-list.md`). It is upstream
> content, not a routing or own-skill problem.

## Conventions

- Commits follow Conventional Commits with a scope (e.g.
  `chore(scripts): …`, `docs(git-remote-sync): …`).
- Don't commit or push unless explicitly asked.
- `CLAUDE.md` is an `@AGENTS.md` include pointing at this file; edit `AGENTS.md` only.
