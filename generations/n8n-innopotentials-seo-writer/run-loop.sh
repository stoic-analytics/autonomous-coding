#!/bin/bash
# Ralph Wiggum Loop for n8n SEO Writer
# Iteratively improves the project until completion criteria are met

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROMPT_FILE="$PROJECT_DIR/PROMPT.md"
LOG_FILE="$PROJECT_DIR/loop-output.log"
MAX_ITERATIONS=${1:-10}
ITERATION=0

echo "=== Ralph Wiggum Loop ==="
echo "Project: n8n-innopotentials-seo-writer"
echo "Max iterations: $MAX_ITERATIONS"
echo "Log file: $LOG_FILE"
echo ""

# Clear previous log
> "$LOG_FILE"

# Function to check completion
check_completion() {
    if grep -q "LOOP_COMPLETE" "$LOG_FILE" 2>/dev/null; then
        return 0
    fi
    return 1
}

# Function to get current feature stats
get_stats() {
    sqlite3 "$PROJECT_DIR/features.db" "SELECT COUNT(*) || '/' || COUNT(*) || ' features, ' || SUM(passes) || ' passing' FROM features" 2>/dev/null || echo "Unable to read features.db"
}

echo "Starting stats: $(get_stats)"
echo ""

while [ $ITERATION -lt $MAX_ITERATIONS ]; do
    ITERATION=$((ITERATION + 1))
    echo "=== Iteration $ITERATION of $MAX_ITERATIONS ==="
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Starting iteration $ITERATION" >> "$LOG_FILE"

    # Run Claude with the prompt
    cd "$PROJECT_DIR"

    # Capture output while also displaying it
    claude --print "$PROMPT_FILE" 2>&1 | tee -a "$LOG_FILE"

    echo "" >> "$LOG_FILE"
    echo "--- End of iteration $ITERATION ---" >> "$LOG_FILE"
    echo ""

    # Check for completion signal
    if check_completion; then
        echo "=== LOOP COMPLETE ==="
        echo "Completion signal detected after $ITERATION iterations"
        echo "Final stats: $(get_stats)"
        exit 0
    fi

    # Brief pause between iterations
    sleep 2
done

echo "=== MAX ITERATIONS REACHED ==="
echo "Completed $MAX_ITERATIONS iterations without completion signal"
echo "Final stats: $(get_stats)"
echo "Review $LOG_FILE for details"
