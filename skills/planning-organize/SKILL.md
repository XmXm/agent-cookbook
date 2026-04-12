---
name: planning-organize
description: "Reorganize planning documents (task_plan.md or similar) for structural coherence. Moves context sections (architecture, design decisions, constraints, risks) before work sections (task lists, execution order, progress). Normalizes item density, extracts bloated inline detail, removes duplicates, and ensures index completeness. Use when the user says 'organize plan', 'restructure plan', 'clean up plan', 'plan structure is messy', or when a planning document has inconsistent section ordering or formatting."
user-invocable: true
disable-model-invocation: true
---

# Organize Plan

Restructure planning documents so they read like a briefing: understand the mission and constraints first, then see the battle plan.

## Directory Resolution

Follow the shared Directory Resolution rules in `~/.claude/skills/planning-archive/references/conventions.md` to determine `PLAN_DIR`. Read `$PLAN_DIR/task_plan.md` (and optionally findings.md, progress.md) as the target documents.

## Core Principle

**Context before work.** A reader should grasp *what*, *why*, and *under what constraints* before seeing *how* and *when*. Sections that establish understanding come before sections that track execution.

## Section Classification

Classify every top-level section as either **context** or **work**:

### Context sections (come first)
Sections that help the reader understand the problem space, boundaries, and decisions already made. Common examples:
- Goals / objectives / scope
- Architecture / system overview
- Design decisions / ADRs
- Constraints / notes / conventions
- Risks / open questions
- Prerequisites / dependencies

### Work sections (come after)
Sections that track what needs to be done, what's in progress, and what's complete. Common examples:
- Task breakdown / backlog
- Execution order / dependency graph
- Progress / status / changelog
- Appendices with detailed per-task plans

**Don't force a fixed template.** Different projects use different section names. Classify by intent, not by name. A section called "Design Notes" is context; a section called "Sprint Plan" is work. If ambiguous, ask.

## Reorganization Rules

### 1. Group by classification, preserve internal order

Move all context sections before all work sections. Within each group, keep the original relative order unless there's a clear logical dependency (e.g., "Architecture" before "Design Decisions" that reference the architecture).

### 2. Normalize item density

Items in the same list section should have roughly the same level of detail. If most tasks are 1-2 lines but one task has 100 lines of inline design, that task's detail needs extraction.

**Threshold**: if an item is >5x longer than its siblings, extract the excess.

**How to extract**:
- Move the detail to a linked file (e.g., `docs/planning-archive/active/tasks/task-N-plan.md`)
- Replace the inline content with a compact summary + link
- Match the format of sibling items

Active/pending items may keep slightly more inline detail than completed ones, since readers need to act on them. But they should still be within range of their siblings.

### 3. Eliminate duplicates and conflicts

Scan for sections covering the same topic. This happens when a document evolves over time and an old version of a section persists alongside the replacement.

- If two sections cover the same topic, keep the newer/more complete one
- If they have complementary content, merge
- Never leave conflicting versions in the document

### 4. Enforce heading hierarchy

Peer items must use the same heading level. If tasks 6-24 use `###` but task 26 uses `#`, fix it. Consistent hierarchy is non-negotiable for readability and tooling (outline views, TOC generators).

### 5. Ensure index completeness

If the document has an index/summary section (like an execution order tree), every item in the detail section must appear in the index, and vice versa. Missing entries are a common symptom of incremental editing.

Check both directions:
- Every task in the breakdown appears in the execution tree
- Every entry in the execution tree has a corresponding task description

### 6. Clean up cross-references

- Links to plan files: verify the target exists (glob check)
- Remove dead links or flag them
- Anchor links (e.g., `#task-26-detail`) must point to an actual heading

## Workflow

1. **Read the full document** to understand its current structure
2. **Classify each section** as context or work
3. **Identify issues**: wrong ordering, density outliers, duplicates, missing index entries, heading inconsistencies
4. **Present a summary** of planned changes to the user before rewriting
5. **Execute the reorganization**
6. **Verify**: re-read the result and confirm section flow, link validity, and index completeness

## What NOT to change

- Don't alter the content/meaning of any section
- Don't rename sections unless asked
- Don't remove sections (only merge true duplicates)
- Don't add new content beyond summary lines replacing extracted detail
- Don't change the writing style or language

The goal is purely structural: same information, better organization.
