#!/bin/bash
# Wiki Data Alerting Script
# 
# This script monitors wiki data health and sends alerts when issues are detected.
# It can be run from cron for automated monitoring.

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
MONITOR_SCRIPT="$SCRIPT_DIR/monitor_wiki_freshness.py"
LOG_FILE="/var/log/wiki-monitor.log"
ALERT_EMAIL="${WIKI_ALERT_EMAIL:-admin@example.com}"
ALERT_THRESHOLD_HOURS="${WIKI_ALERT_THRESHOLD:-48}"

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Send alert function
send_alert() {
    local subject="$1"
    local message="$2"
    local priority="$3"  # high, medium, low
    
    log "ALERT [$priority]: $subject"
    
    # Send email if configured
    if command -v mail >/dev/null 2>&1 && [ -n "$ALERT_EMAIL" ]; then
        echo "$message" | mail -s "[$priority] Wiki Monitor: $subject" "$ALERT_EMAIL"
        log "Alert email sent to $ALERT_EMAIL"
    fi
    
    # Send to syslog
    if command -v logger >/dev/null 2>&1; then
        logger -t wiki-monitor -p daemon.warning "[$priority] $subject: $message"
    fi
    
    # Print to console with color
    case "$priority" in
        "high")
            echo -e "${RED}CRITICAL: $subject${NC}"
            ;;
        "medium")
            echo -e "${YELLOW}WARNING: $subject${NC}"
            ;;
        "low")
            echo -e "${GREEN}INFO: $subject${NC}"
            ;;
    esac
}

# Check if monitor script exists
if [ ! -f "$MONITOR_SCRIPT" ]; then
    send_alert "Monitor script not found" "Wiki monitoring script not found at $MONITOR_SCRIPT" "high"
    exit 1
fi

# Change to project directory
cd "$PROJECT_DIR" || {
    send_alert "Cannot change to project directory" "Failed to change to $PROJECT_DIR" "high"
    exit 1
}

log "Starting wiki health check..."

# Run the health check
HEALTH_OUTPUT=$(python3 "$MONITOR_SCRIPT" --check --json 2>&1)
HEALTH_EXIT_CODE=$?

# Check if the command succeeded
if [ $HEALTH_EXIT_CODE -ne 0 ]; then
    if [ $HEALTH_EXIT_CODE -eq 1 ]; then
        # Critical or degraded status
        send_alert "Wiki system degraded" "Wiki health check failed with critical issues. Output: $HEALTH_OUTPUT" "high"
    elif [ $HEALTH_EXIT_CODE -eq 2 ]; then
        # Warning status
        send_alert "Wiki system warnings" "Wiki health check completed with warnings. Output: $HEALTH_OUTPUT" "medium"
    else
        # Script error
        send_alert "Health check script failed" "Wiki health check script failed to run. Exit code: $HEALTH_EXIT_CODE. Output: $HEALTH_OUTPUT" "high"
    fi
    exit $HEALTH_EXIT_CODE
fi

# Parse JSON output
if command -v jq >/dev/null 2>&1; then
    OVERALL_STATUS=$(echo "$HEALTH_OUTPUT" | jq -r '.overall_status // "unknown"')
    ALERTS=$(echo "$HEALTH_OUTPUT" | jq -r '.alerts[]? // empty')
    
    log "Health check completed. Status: $OVERALL_STATUS"
    
    # Process alerts
    if [ -n "$ALERTS" ]; then
        ALERT_COUNT=$(echo "$ALERTS" | wc -l)
        log "Found $ALERT_COUNT alerts"
        
        # Determine alert priority based on status
        case "$OVERALL_STATUS" in
            "critical")
                PRIORITY="high"
                ;;
            "degraded")
                PRIORITY="high"
                ;;
            "warning")
                PRIORITY="medium"
                ;;
            *)
                PRIORITY="low"
                ;;
        esac
        
        # Send consolidated alert
        ALERT_MESSAGE="Wiki system status: $OVERALL_STATUS\n\nAlerts:\n$ALERTS\n\nFull report:\n$HEALTH_OUTPUT"
        send_alert "Wiki system issues detected" "$ALERT_MESSAGE" "$PRIORITY"
    else
        log "No alerts found. System healthy."
        send_alert "Wiki system healthy" "All wiki data checks passed successfully." "low"
    fi
else
    # Fallback without jq
    log "jq not available, using basic parsing"
    
    if echo "$HEALTH_OUTPUT" | grep -q '"overall_status": "critical"'; then
        send_alert "Wiki system critical" "Critical issues detected in wiki system. Full output: $HEALTH_OUTPUT" "high"
    elif echo "$HEALTH_OUTPUT" | grep -q '"overall_status": "degraded"'; then
        send_alert "Wiki system degraded" "Wiki system is degraded. Full output: $HEALTH_OUTPUT" "high"
    elif echo "$HEALTH_OUTPUT" | grep -q '"overall_status": "warning"'; then
        send_alert "Wiki system warnings" "Wiki system has warnings. Full output: $HEALTH_OUTPUT" "medium"
    else
        log "Wiki system appears healthy"
    fi
fi

# Additional checks

# Check disk space for wiki cache
WIKI_CACHE_DIR="$PROJECT_DIR/data/wiki"
if [ -d "$WIKI_CACHE_DIR" ]; then
    CACHE_SIZE=$(du -sm "$WIKI_CACHE_DIR" 2>/dev/null | cut -f1)
    if [ -n "$CACHE_SIZE" ] && [ "$CACHE_SIZE" -gt 1000 ]; then
        send_alert "Wiki cache size large" "Wiki cache directory is ${CACHE_SIZE}MB, consider cleanup" "medium"
    fi
    
    # Check if cache directory is writable
    if [ ! -w "$WIKI_CACHE_DIR" ]; then
        send_alert "Wiki cache not writable" "Wiki cache directory $WIKI_CACHE_DIR is not writable" "high"
    fi
fi

# Check if server process is running
if ! pgrep -f "server.py" >/dev/null; then
    send_alert "MCP server not running" "Character Music MCP server process not found" "high"
fi

# Check recent log errors
if [ -f "/var/log/character-music-mcp.log" ]; then
    RECENT_ERRORS=$(tail -100 /var/log/character-music-mcp.log | grep -c "ERROR" || echo "0")
    if [ "$RECENT_ERRORS" -gt 5 ]; then
        send_alert "High error rate" "Found $RECENT_ERRORS errors in recent server logs" "medium"
    fi
fi

log "Wiki monitoring check completed"

# Optional: Clean up old log entries (keep last 1000 lines)
if [ -f "$LOG_FILE" ] && [ $(wc -l < "$LOG_FILE") -gt 1000 ]; then
    tail -1000 "$LOG_FILE" > "${LOG_FILE}.tmp" && mv "${LOG_FILE}.tmp" "$LOG_FILE"
fi

exit 0