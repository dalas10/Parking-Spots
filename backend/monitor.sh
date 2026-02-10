#!/bin/bash
# Real-time Performance Monitoring for ParkingSpots API
# Shows live stats every 2 seconds

INTERVAL=2

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Function to get worker count
get_worker_count() {
    ps aux | grep -c "[u]vicorn.*app.main:app" || echo "0"
}

# Function to get CPU usage
get_cpu_usage() {
    ps aux | grep "[u]vicorn.*app.main:app" | awk '{sum+=$3} END {printf "%.1f", sum}'
}

# Function to get memory usage
get_memory_usage() {
    ps aux | grep "[u]vicorn.*app.main:app" | awk '{sum+=$4} END {printf "%.1f", sum}'
}

# Function to check if background tasks are running
check_background_tasks() {
    if ps aux | grep -q "[r]un_background_tasks.py"; then
        echo -e "${GREEN}Running${NC}"
    else
        echo -e "${RED}Not Running${NC}"
    fi
}

# Function to get Redis stats
get_redis_stats() {
    HITS=$(redis-cli INFO stats 2>/dev/null | grep "keyspace_hits" | cut -d: -f2 | tr -d '\r')
    MISSES=$(redis-cli INFO stats 2>/dev/null | grep "keyspace_misses" | cut -d: -f2 | tr -d '\r')
    KEYS=$(redis-cli DBSIZE 2>/dev/null | awk '{print $2}')
    MEMORY=$(redis-cli INFO memory 2>/dev/null | grep "used_memory_human:" | cut -d: -f2 | tr -d '\r')
    
    TOTAL=$(($HITS + $MISSES))
    if [ $TOTAL -gt 0 ]; then
        HIT_RATE=$(echo "scale=1; $HITS * 100 / $TOTAL" | bc)
    else
        HIT_RATE="0.0"
    fi
    
    echo "$HITS|$MISSES|$HIT_RATE|$KEYS|$MEMORY"
}

# Function to get database stats
get_db_stats() {
    CONNECTIONS=$(sudo -u postgres psql -d parkingspots -t -c "SELECT count(*) FROM pg_stat_activity WHERE datname='parkingspots';" 2>/dev/null | tr -d ' ' || echo "N/A")
    echo "$CONNECTIONS"
}

# Clear screen and show header
clear
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       🚀 ParkingSpots API - Real-Time Monitor               ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop monitoring${NC}"
echo ""

# Store previous values for rate calculation
PREV_HITS=0
PREV_MISSES=0
START_TIME=$(date +%s)

while true; do
    # Move cursor to line 7
    tput cup 6 0
    
    # Get current time
    CURRENT_TIME=$(date "+%Y-%m-%d %H:%M:%S")
    UPTIME=$(( $(date +%s) - START_TIME ))
    
    # API Workers
    WORKERS=$(get_worker_count)
    CPU=$(get_cpu_usage)
    MEM=$(get_memory_usage)
    
    # Background Tasks
    BG_STATUS=$(check_background_tasks)
    
    # Redis Stats
    IFS='|' read -r HITS MISSES HIT_RATE KEYS MEMORY <<< "$(get_redis_stats)"
    
    # Database
    DB_CONN=$(get_db_stats)
    
    # Calculate rates
    HITS_RATE=$(( ($HITS - $PREV_HITS) / $INTERVAL ))
    MISSES_RATE=$(( ($MISSES - $PREV_MISSES) / $INTERVAL ))
    
    PREV_HITS=$HITS
    PREV_MISSES=$MISSES
    
    # Display stats
    echo -e "${CYAN}┌─ System Status ────────────────────────────────────────────────┐${NC}"
    echo -e "${CYAN}│${NC} Time: ${CURRENT_TIME}   Uptime: ${UPTIME}s              "
    echo -e "${CYAN}└────────────────────────────────────────────────────────────────┘${NC}"
    echo ""
    
    echo -e "${CYAN}┌─ API Workers ──────────────────────────────────────────────────┐${NC}"
    if [ "$WORKERS" -gt 0 ]; then
        echo -e "${CYAN}│${NC} Workers:  ${GREEN}${WORKERS} active${NC}                                       "
        echo -e "${CYAN}│${NC} CPU:      ${GREEN}${CPU}%${NC}                                             "
        echo -e "${CYAN}│${NC} Memory:   ${GREEN}${MEM}%${NC}                                             "
    else
        echo -e "${CYAN}│${NC} Status:   ${RED}No workers running${NC}                                "
        echo -e "${CYAN}│${NC} Start:    ${YELLOW}./start_production.sh${NC}                            "
    fi
    echo -e "${CYAN}└────────────────────────────────────────────────────────────────┘${NC}"
    echo ""
    
    echo -e "${CYAN}┌─ Background Tasks ─────────────────────────────────────────────┐${NC}"
    echo -e "${CYAN}│${NC} Status:   ${BG_STATUS}                                     "
    echo -e "${CYAN}└────────────────────────────────────────────────────────────────┘${NC}"
    echo ""
    
    echo -e "${CYAN}┌─ Redis Cache ──────────────────────────────────────────────────┐${NC}"
    echo -e "${CYAN}│${NC} Hits:     ${GREEN}${HITS}${NC} (+${HITS_RATE}/s)                                  "
    echo -e "${CYAN}│${NC} Misses:   ${YELLOW}${MISSES}${NC} (+${MISSES_RATE}/s)                              "
    echo -e "${CYAN}│${NC} Hit Rate: ${GREEN}${HIT_RATE}%${NC}                                          "
    echo -e "${CYAN}│${NC} Keys:     ${BLUE}${KEYS}${NC}                                                "
    echo -e "${CYAN}│${NC} Memory:   ${BLUE}${MEMORY}${NC}                                          "
    echo -e "${CYAN}└────────────────────────────────────────────────────────────────┘${NC}"
    echo ""
    
    echo -e "${CYAN}┌─ PostgreSQL Database ──────────────────────────────────────────┐${NC}"
    echo -e "${CYAN}│${NC} Connections: ${BLUE}${DB_CONN}${NC}                                         "
    echo -e "${CYAN}└────────────────────────────────────────────────────────────────┘${NC}"
    echo ""
    
    # Performance indicators
    if [ "$HIT_RATE" != "0.0" ]; then
        HIT_NUM=$(echo "$HIT_RATE" | cut -d'.' -f1)
        if [ "$HIT_NUM" -ge 80 ]; then
            PERF_STATUS="${GREEN}✓ Excellent${NC}"
        elif [ "$HIT_NUM" -ge 60 ]; then
            PERF_STATUS="${YELLOW}○ Good${NC}"
        else
            PERF_STATUS="${RED}⚠ Poor${NC}"
        fi
    else
        PERF_STATUS="${YELLOW}○ No data${NC}"
    fi
    
    echo -e "${CYAN}┌─ Performance ──────────────────────────────────────────────────┐${NC}"
    echo -e "${CYAN}│${NC} Cache Performance: ${PERF_STATUS}                             "
    echo -e "${CYAN}└────────────────────────────────────────────────────────────────┘${NC}"
    
    sleep $INTERVAL
done
