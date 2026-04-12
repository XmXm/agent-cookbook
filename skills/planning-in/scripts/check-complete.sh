#!/bin/bash
# Check if all phases are complete across all registered plans
# Reads .planning-dir registry and checks each plan's task_plan.md
# Always exits 0 — uses stdout for status reporting (used by Stop hook)

REGISTRY=".planning-dir"

if [ ! -f "$REGISTRY" ]; then
    echo "[planning-in] No .planning-dir found — no active plans."
    exit 0
fi

OVERALL_TOTAL=0
OVERALL_COMPLETE=0
PLAN_COUNT=0

while IFS= read -r PLAN_DIR; do
    [ -z "$PLAN_DIR" ] && continue
    PLAN_FILE="$PLAN_DIR/task_plan.md"
    [ ! -f "$PLAN_FILE" ] && continue

    PLAN_NAME="$(basename "$PLAN_DIR")"
    PLAN_COUNT=$((PLAN_COUNT + 1))

    TOTAL=$(grep -c "### Phase" "$PLAN_FILE" || true)
    COMPLETE=$(grep -cF "**Status:** complete" "$PLAN_FILE" || true)
    IN_PROGRESS=$(grep -cF "**Status:** in_progress" "$PLAN_FILE" || true)
    PENDING=$(grep -cF "**Status:** pending" "$PLAN_FILE" || true)

    # Fallback: check for [complete] inline format
    if [ "$COMPLETE" -eq 0 ] && [ "$IN_PROGRESS" -eq 0 ] && [ "$PENDING" -eq 0 ]; then
        COMPLETE=$(grep -c "\[complete\]" "$PLAN_FILE" || true)
        IN_PROGRESS=$(grep -c "\[in_progress\]" "$PLAN_FILE" || true)
        PENDING=$(grep -c "\[pending\]" "$PLAN_FILE" || true)
    fi

    : "${TOTAL:=0}"
    : "${COMPLETE:=0}"

    OVERALL_TOTAL=$((OVERALL_TOTAL + TOTAL))
    OVERALL_COMPLETE=$((OVERALL_COMPLETE + COMPLETE))

    if [ "$COMPLETE" -eq "$TOTAL" ] && [ "$TOTAL" -gt 0 ]; then
        echo "[planning-in] [$PLAN_NAME] ALL PHASES COMPLETE ($COMPLETE/$TOTAL)"
    else
        echo "[planning-in] [$PLAN_NAME] $COMPLETE/$TOTAL phases complete"
        [ "$IN_PROGRESS" -gt 0 ] && echo "  $IN_PROGRESS phase(s) in progress"
        [ "$PENDING" -gt 0 ] && echo "  $PENDING phase(s) pending"
    fi
done < "$REGISTRY"

if [ "$PLAN_COUNT" -eq 0 ]; then
    echo "[planning-in] No active plans found in registry."
elif [ "$OVERALL_COMPLETE" -eq "$OVERALL_TOTAL" ] && [ "$OVERALL_TOTAL" -gt 0 ]; then
    echo "[planning-in] ALL $PLAN_COUNT PLAN(S) COMPLETE ($OVERALL_COMPLETE/$OVERALL_TOTAL total phases)"
else
    echo "[planning-in] Summary: $OVERALL_COMPLETE/$OVERALL_TOTAL phases across $PLAN_COUNT plan(s)"
fi

exit 0
