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
NEXT=$((${HIGHEST:-0} + 1))
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
[One sentence describing the end state]

## Current Phase
Phase 1

## Phases

### Phase 1: Requirements & Discovery
- [ ] Understand user intent
- [ ] Identify constraints and requirements
- [ ] Document findings in findings.md
- **Status:** in_progress

### Phase 2: Planning & Structure
- [ ] Define technical approach
- [ ] Create project structure if needed
- [ ] Document decisions with rationale
- **Status:** pending

### Phase 3: Implementation
- [ ] Execute the plan step by step
- [ ] Write code to files before executing
- [ ] Test incrementally
- **Status:** pending

### Phase 4: Testing & Verification
- [ ] Verify all requirements met
- [ ] Document test results in progress.md
- [ ] Fix any issues found
- **Status:** pending

### Phase 5: Delivery
- [ ] Review all output files
- [ ] Ensure deliverables are complete
- [ ] Deliver to user
- **Status:** pending

## Decisions Made
| Decision | Rationale |
|----------|-----------|

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
EOF
    echo "  Created $PLAN_DIR/task_plan.md"
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

### Phase 1: Requirements & Discovery
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
