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
├── skills/        # ACTIVE skills the agent loads (own dirs + symlinks into refs/)
│   └── RESOLVER.md  # human routing table; every active skill must be listed here
├── refs/          # third-party repos as git submodules (read-only references)
├── rules/         # portable, always-on rule files (flat, prefix-named)
├── scripts/       # verify-skills.sh (contract checker), update-submodules.sh
└── legacy/        # parked skills superseded by active ones
```

Ownership:

- `skills/`, `rules/`, `scripts/`, `legacy/` — the user's own / reused content. Edit freely.
- `refs/` — **third-party submodules**. Do not hand-edit; they are upstream code
  pulled in for reference and for symlink targets. Update via the script below.

## Skills

A skill is a directory under `skills/` containing `SKILL.md` (plus optional
`references/`, `agents/`, `scripts/` subdirs). Two kinds coexist:

- **Own skills** — real directories (e.g. `commitall`, `cs-style-check`,
  `markdown-to-lark-doc`, `planning-*`, `pc-wsl-docker`).
- **Symlinked skills** — symlinks into a `refs/` submodule, reusing upstream
  skills (e.g. `think`, `hunt`, `check`, `design`, `write` → `refs/Waza`;
  `lark-*` → `refs/lark-skills`; `handoff`, `improve-codebase-architecture` →
  `refs/mattpocock-skills`).

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
   an upstream skill from `refs/`).
2. Add a routing row in `skills/RESOLVER.md`.
3. Run `bash scripts/verify-skills.sh` until it passes.

## Rules

`rules/` holds portable, durable, always-on constraints (naming, formatting,
security invariants, language conventions). Flat layout, prefix-named by scope
(`common-*`, `typescript-*`, `python-*`, `go-*`, `swift-*`, `csharp-*`,
`markdown-*`) so they can be copied into a single `rules/` dir without name
clashes. See `rules/README.md` for the install guidance and the staleness audit.

Rules vs skills: rules = short durable constraints; skills = deep workflows,
long examples, and agent routing. Don't put workflow procedures in rules.

## Submodules (`refs/`)

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
- `CLAUDE.md` is a relative symlink to this file; edit `AGENTS.md` only.
