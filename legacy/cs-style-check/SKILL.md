---
name: cs-style-check
model: haiku
context: fork
description: Scan C# code for coding style violations against loaded csharp rules. Use this skill when the user says "check style", "lint cs", "style check", "cs-style-check", "检查风格", "看看命名", or asks to review C# code formatting/naming compliance. Also trigger proactively before committing C# changes, after a commit, or during code review when style compliance matters. Default (no args) scans uncommitted git changes; pass a commit ref (e.g. HEAD, HEAD~1, abc1234) to scan a specific commit.
---

# C# Style Checker

Scan C# code for mechanically-verifiable style violations based on all loaded csharp rules.

This skill focuses on what can be reliably detected by reading code: formatting, naming, type inference, and common anti-patterns with clear syntactic signatures. Deeper architectural concerns (state management patterns, code organization decisions, thread safety design) are covered by the rules themselves and apply during normal code review — they don't belong in an automated-style scan because they require understanding intent.

## Input

- **No arguments**: scan only `.cs` files in uncommitted git changes (`git diff` + `git diff --cached`)
- **Commit ref** (e.g. `HEAD`, `HEAD~1`, `abc1234`): scan the diff introduced by that specific commit
- **File path(s)**: scan specified files
- **Directory**: scan all `.cs` files under that directory

## Procedure

1. **Load rules**: 加载所有已生效的 C# 编码规范（用户级 `~/.claude/rules/` 和项目级 `.claude/rules/` 中 paths 匹配 `*.cs` 的规则文件）。以加载到的规则为准执行检查。
2. **Determine mode** from the argument:
   - No args → **uncommitted mode**: collect files from `git diff --name-only` + `git diff --cached --name-only`, filter `*.cs`
   - Looks like a commit ref (short/full hash, `HEAD`, `HEAD~N`, branch name) → **commit mode**: collect files from `git diff --name-only <ref>^ <ref>`, filter `*.cs`
   - File path(s) or directory → **file mode**: use provided paths directly
3. **Get raw diff for analysis** (uncommitted mode and commit mode only):
   - **Uncommitted mode**: `rtk proxy git diff --unified=0 -- '*.cs'` (falls back to `git diff --unified=0 -- '*.cs'` if rtk not installed). Also include staged: `git diff --cached --unified=0 -- '*.cs'`
   - **Commit mode**: `rtk proxy git diff --unified=0 <ref>^ <ref> -- '*.cs'` (falls back to `git diff --unified=0 <ref>^ <ref> -- '*.cs'`). This captures exactly what that commit changed.
   - Bypassing rtk's compressed output ensures `+` lines can be correctly parsed.
4. **For each file**, read the content and check against the loaded rules, focusing on the mechanically-verifiable categories below
5. **Report** violations grouped by file, with line numbers and the violated rule

## What to Check

Check the loaded rules and apply them to the scanned code. The categories below indicate what a style scanner can reliably detect — items outside these categories are better left to code review.

### Reliably detectable (always check)

**Formatting** — pure syntax, no ambiguity:
- Brace placement (Allman vs K&R)
- Missing braces on control statements
- Single-line multi-statement blocks
- Line length

**Naming** — pattern matching on declarations:
- Field prefix conventions (`_`, `m_`, `m_b`, `m_i`, `m_p`, `m_ls`, `m_dic` etc.)
- Method/property casing (PascalCase)
- Event handler `On` prefix
- Constant casing

**Type Inference** — local assignment analysis:
- `var` usage where type is inferrable from right-hand side

### Detectable with high confidence (check when pattern is clear)

**Performance anti-patterns** — syntactic signatures that don't require understanding hot-path context:
- `using System.Linq` in files under performance-sensitive paths (BattleLogic/, Synchronization/)
- `for` loops with uncached `.Count` (`i < list.Count` in the loop condition)
- Closures/lambdas that visibly capture outer variables

**Error handling** — structural patterns:
- Bare `catch (Exception)` without specific type
- String null checks using `== null` or `== ""` instead of `string.IsNullOrEmpty`
- Nested null checks where early return would be cleaner

### Not reliably detectable (leave to code review)

These are covered by the rules but require understanding design intent — don't try to flag them in a style scan:
- Whether a feature needs a feature flag
- Whether register/unregister are properly paired (cross-method analysis)
- Whether a file should use partial class splitting
- Whether a type should be nested or standalone
- Whether a field needs `volatile`
- Whether `Reset()` clears all fields (requires knowing all fields)

## Output Format

```
## cs-style-check: {N} violation(s) in {M} file(s)

### path/to/File.cs
- **Line {n}**: [Formatting] 控制语句缺少大括号 — `if (x) return;`
- **Line {n}**: [Naming] 私有字段命名不规范 — `private int count` → `_count`

### path/to/Other.cs
- **Line {n}**: [Performance] for 循环未缓存 Count — `i < list.Count`

---
{N} total violation(s). {passed} file(s) clean.
```

If zero violations: output `cs-style-check: all clean`.

## Scope Awareness

When scanning git diff, only check the **changed lines and their immediate context** (the `+` lines in the diff). Existing code that wasn't touched in this diff is out of scope — the goal is to enforce style on new/modified code, not audit the entire codebase.

## Important

- This is a read-only scan. Never auto-fix code unless the user explicitly asks.
- Naming rules apply to NEW declarations only. Don't flag existing project identifiers that follow a legacy convention.
- The `AI Behavior` section of the rules is about Claude's own behavior, not code to scan — skip it.
- When in doubt about whether something is a violation, err on the side of not reporting it. False positives erode trust in the checker.
