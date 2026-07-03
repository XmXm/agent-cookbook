#!/bin/bash
# Initialize planning files in .plans/NNN-description/
# Usage: ./init-session.sh <description>
# Description is required — auto-numbered with NNN prefix.

set -e

if [ -z "$1" ]; then
    echo "Error: description is required. Usage: init-session.sh <description>" >&2
    exit 1
fi

SLUG="$1"
# Auto-number: find highest NNN in .plans/ and increment
HIGHEST=$(ls -d .plans/[0-9]* 2>/dev/null | sed 's|.plans/||' | sed 's/-.*//' | sort -n | tail -1)
# Force base-10 to avoid bash interpreting leading-zero numbers like 020 as octal.
NEXT=$((10#${HIGHEST:-0} + 1))
NUM=$(printf "%03d" $NEXT)

PLAN_NAME="${NUM}-${SLUG}"
PLAN_DIR=".plans/$PLAN_NAME"
DATE=$(date +%Y-%m-%d)

mkdir -p "$PLAN_DIR"
echo "Initializing plan '$PLAN_NAME' in: $PLAN_DIR/"

# Count existing active plans (subdirectories of .plans/ with task_plan.md, excluding active/ and archive/)
PLAN_COUNT=$(find .plans -maxdepth 2 -name task_plan.md -exec dirname {} \; 2>/dev/null | wc -l | tr -d ' ')
echo "Active plans: $PLAN_COUNT"

# Create task_plan.md
if [ ! -f "$PLAN_DIR/task_plan.md" ]; then
    cat > "$PLAN_DIR/task_plan.md" << EOF
# Task Plan: $PLAN_NAME

## Goal
[One sentence end state]

## Building / Not Building
**Building:** [what this plan delivers]
**Not Building (out of scope):** [explicit non-goals; protects against scope drift]

## Approach
[Chosen direction with rationale. Mention the rejected alternative only if the tradeoff was close.]

## Key Decisions
| Decision | Rationale |
|----------|-----------|

## Premise Collapse
- **Most fragile assumption:** [the load-bearing assumption most likely to be wrong]
- **If it fails:** [what breaks]
- **Mitigation:** [how the design survives or how we detect early]

## External Dependencies
| Dependency | Why needed | Source / owner | Reachability check | Status |
|------------|------------|----------------|--------------------|--------|
| (API key name / env var name / MCP / 3rd-party CLI / credential owner) | | | | pending / ready / blocked |

## Verification Plan
| Phase | Command | Expected outcome |
|-------|---------|------------------|

## Rollback
[For each irreversible step: how to undo. Write \`N/A — local-only\` when there is no external state change.]

---

## Current Phase
Phase 1

## Phases

### Phase 1: [Concrete name derived from Approach]
- [ ] [Specific action]
- [ ] [Specific action]
- **Verification:** [exact command, must match Verification Plan row]
- **Status:** in_progress

<!-- Add additional phases as the work naturally splits.
     Do NOT pad to 5 phases. A bug fix may need 2; a refactor may need 6.
     Every phase MUST have a concrete Verification command. -->

## Decisions Made
| Decision | Rationale |
|----------|-----------|

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
EOF
    echo "  Created $PLAN_DIR/task_plan.md"
    echo "  [planning-in] Skeleton created. Fill Approach / Premise Collapse / External Dependencies BEFORE writing phase tasks."
else
    echo "  $PLAN_DIR/task_plan.md already exists, skipping"
fi

# Create findings.md
if [ ! -f "$PLAN_DIR/findings.md" ]; then
    cat > "$PLAN_DIR/findings.md" << 'EOF'
# Findings & Decisions

## Requirements
-

## Research Findings
-

## Technical Decisions
| Decision | Rationale |
|----------|-----------|

## Issues Encountered
| Issue | Resolution |
|-------|------------|

## Resources
-
EOF
    echo "  Created $PLAN_DIR/findings.md"
else
    echo "  $PLAN_DIR/findings.md already exists, skipping"
fi

# Create progress.md
if [ ! -f "$PLAN_DIR/progress.md" ]; then
    cat > "$PLAN_DIR/progress.md" << EOF
# Progress Log

## Session: $DATE

### Phase 1: [name from task_plan.md]
- **Status:** in_progress
- **Started:** $DATE
- Actions taken:
  -
- Files created/modified:
  -

## Test Results
| Test | Expected | Actual | Status |
|------|----------|--------|--------|

## Error Log
| Timestamp | Error | Attempt | Resolution |
|-----------|-------|---------|------------|
EOF
    echo "  Created $PLAN_DIR/progress.md"
else
    echo "  $PLAN_DIR/progress.md already exists, skipping"
fi

echo ""
echo "Plan: $PLAN_NAME"
echo "Directory: $PLAN_DIR/"
echo "Files: task_plan.md | findings.md | progress.md"
echo "Active plans: $PLAN_COUNT"

# Update the global index. Failure here is non-fatal (index is a cache and can
# always be rebuilt from disk via `plans-index.py rebuild`).
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if command -v python3 >/dev/null 2>&1 && [ -f "$SCRIPT_DIR/plans-index.py" ]; then
    python3 "$SCRIPT_DIR/plans-index.py" sync "$PLAN_DIR" >/dev/null 2>&1 \
        && echo "Index updated: .plans/_index.json" \
        || echo "Index update skipped (non-fatal; run plans-index.py rebuild to recover)."
fi
