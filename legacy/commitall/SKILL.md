---
name: commitall
description: Commit all local changes in a git repository with auto-generated commit message. Accepts --push parameter to also push to remote (disabled by default). Use when user says "commit all", "commit everything", "commitall", or wants to quickly stage and commit all uncommitted changes.
---

# CommitAll

Quickly commit all local changes.

## Usage

Handle requests like:
- "commit all changes"
- "commit everything"
- "commitall"
- "commitall --push"
- "commit all and push"

## Workflow

1. **Check git status**: Verify there are changes to commit
2. **Stage all**: Run `git add -A`
3. **Generate commit message** (if not provided):
   - Analyze staged changes (files modified, added, deleted)
   - Generate a concise conventional commit message
4. **Commit**: Run `git commit -m "<message>"`
5. **Push** (only if `--push` flag): Run `git push`

## Parameters

- `--push`: Push to remote after commit (default: false)
- Custom message: User can provide a specific commit message

## Example Interactions

**User**: "commitall"
→ Stage all, generate message, commit (no push)

**User**: "commitall --push"
→ Stage all, generate message, commit, push

**User**: "commit all with message 'fix bug'"
→ Stage all, commit with "fix bug" (no push)

**User**: "commitall --push 'release v1.0'"
→ Stage all, commit with "release v1.0", push
