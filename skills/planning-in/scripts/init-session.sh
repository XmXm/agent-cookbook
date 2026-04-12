#!/bin/bash
# Initialize planning files in a specified directory
# Usage: ./init-session.sh <directory>
# Plan name is inferred from directory basename

set -e

PLAN_DIR="${1:-.}"
DATE=$(date +%Y-%m-%d)

if [ "$PLAN_DIR" = "." ]; then
    PLAN_NAME="$(basename "$(pwd)")"
    echo "Initializing plan '$PLAN_NAME' in project root: $(pwd)"
else
    PLAN_NAME="$(basename "$PLAN_DIR")"
    mkdir -p "$PLAN_DIR"
    echo "Initializing plan '$PLAN_NAME' in: $PLAN_DIR"
fi

# Register plan in .planning-dir (append, avoid duplicates)
grep -qxF "$PLAN_DIR" .planning-dir 2>/dev/null || echo "$PLAN_DIR" >> .planning-dir
PLAN_COUNT=$(wc -l < .planning-dir | tr -d ' ')
echo "Registered in .planning-dir ($PLAN_COUNT active plan(s))"

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
