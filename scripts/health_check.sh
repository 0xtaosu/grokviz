#!/bin/bash
# Health check script for GrokViz Docker container

set -e

# Check if cron process is running (without pgrep dependency)
if ! cat /proc/*/comm 2>/dev/null | grep -q "^cron$"; then
    echo "ERROR: Cron process is not running"
    exit 1
fi

# Check if log file exists and has been updated recently (within 24 hours)
LOG_FILE="/app/data/logs/grokviz.log"

if [ -f "$LOG_FILE" ]; then
    # Get last modification time in seconds since epoch
    LAST_MODIFIED=$(stat -c %Y "$LOG_FILE" 2>/dev/null || stat -f %m "$LOG_FILE" 2>/dev/null)
    CURRENT_TIME=$(date +%s)
    AGE=$((CURRENT_TIME - LAST_MODIFIED))

    # 24 hours = 86400 seconds
    if [ $AGE -gt 86400 ]; then
        echo "WARNING: Log file not updated in 24 hours (age: ${AGE}s)"
        # Don't fail on this - log might not exist yet on first run
    fi
else
    echo "INFO: Log file does not exist yet (first run)"
fi

# Check if temp directory is accessible
if [ ! -d "/app/data/temp" ]; then
    echo "ERROR: Temp directory not accessible"
    exit 1
fi

# Check if we can write to temp directory
TEST_FILE="/app/data/temp/.health_check_test"
if ! touch "$TEST_FILE" 2>/dev/null; then
    echo "ERROR: Cannot write to temp directory"
    exit 1
fi
rm -f "$TEST_FILE"

echo "OK: Health check passed"
exit 0
