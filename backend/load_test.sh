#!/bin/bash
# Load Testing Script for ParkingSpots API
# Tests concurrent request handling and performance

set -e

API_URL="http://localhost:8000"
COLORS=1

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 ParkingSpots API Load Testing${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if API is running
echo ""
echo -e "${YELLOW}Checking API status...${NC}"
if ! curl -s "${API_URL}/health" > /dev/null; then
    echo -e "${RED}✗ API is not running on ${API_URL}${NC}"
    echo "  Start it with: cd backend && ./start_production.sh"
    exit 1
fi
echo -e "${GREEN}✓ API is running${NC}"

# Test 1: Basic Response Time
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Test 1: Single Request Response Time${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
START=$(date +%s%N)
curl -s "${API_URL}/api/v1/parking-spots/?limit=10" > /dev/null
END=$(date +%s%N)
DURATION=$((($END - $START) / 1000000))
echo -e "   Response time: ${GREEN}${DURATION}ms${NC}"

# Test 2: Concurrent Requests
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Test 2: 50 Concurrent Requests${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
START=$(date +%s%N)
for i in {1..50}; do
    curl -s "${API_URL}/api/v1/parking-spots/?limit=10" > /dev/null &
done
wait
END=$(date +%s%N)
TOTAL_TIME=$((($END - $START) / 1000000))
AVG_TIME=$(($TOTAL_TIME / 50))
RPS=$((50000 / $TOTAL_TIME))
echo -e "   Total time: ${GREEN}${TOTAL_TIME}ms${NC}"
echo -e "   Average per request: ${GREEN}${AVG_TIME}ms${NC}"
echo -e "   Requests per second: ${GREEN}${RPS}${NC}"

# Test 3: Cache Performance
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Test 3: Cache Performance${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# First request (cache miss)
START=$(date +%s%N)
curl -s "${API_URL}/api/v1/parking-spots/?limit=15" > /dev/null
END=$(date +%s%N)
UNCACHED=$((($END - $START) / 1000000))
echo -e "   First request (cache miss): ${YELLOW}${UNCACHED}ms${NC}"

# Second request (cache hit)
START=$(date +%s%N)
curl -s "${API_URL}/api/v1/parking-spots/?limit=15" > /dev/null
END=$(date +%s%N)
CACHED=$((($END - $START) / 1000000))
echo -e "   Second request (cache hit): ${GREEN}${CACHED}ms${NC}"

IMPROVEMENT=$(( ($UNCACHED - $CACHED) * 100 / $UNCACHED ))
echo -e "   Cache improvement: ${GREEN}${IMPROVEMENT}%${NC}"

# Test 4: Different Endpoints
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Test 4: Multiple Endpoints (10 concurrent each)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

ENDPOINTS=(
    "/api/v1/parking-spots/?limit=10"
    "/api/v1/parking-spots/?limit=20"
    "/api/v1/parking-spots/?city=Ζάκυνθος"
    "/health"
)

for endpoint in "${ENDPOINTS[@]}"; do
    START=$(date +%s%N)
    for i in {1..10}; do
        curl -s "${API_URL}${endpoint}" > /dev/null &
    done
    wait
    END=$(date +%s%N)
    DURATION=$((($END - $START) / 1000000))
    echo -e "   ${endpoint}: ${GREEN}${DURATION}ms${NC} (10 requests)"
done

# Redis Stats
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Redis Cache Statistics${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
HITS=$(redis-cli INFO stats | grep "keyspace_hits" | cut -d: -f2 | tr -d '\r')
MISSES=$(redis-cli INFO stats | grep "keyspace_misses" | cut -d: -f2 | tr -d '\r')
TOTAL=$(($HITS + $MISSES))
if [ $TOTAL -gt 0 ]; then
    HIT_RATE=$(($HITS * 100 / $TOTAL))
else
    HIT_RATE=0
fi
KEYS=$(redis-cli DBSIZE | awk '{print $2}')
MEMORY=$(redis-cli INFO memory | grep "used_memory_human" | cut -d: -f2 | tr -d '\r')

echo -e "   Cache hits: ${GREEN}${HITS}${NC}"
echo -e "   Cache misses: ${YELLOW}${MISSES}${NC}"
echo -e "   Hit rate: ${GREEN}${HIT_RATE}%${NC}"
echo -e "   Cached keys: ${BLUE}${KEYS}${NC}"
echo -e "   Memory usage: ${BLUE}${MEMORY}${NC}"

# Database Stats
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Database Statistics${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
CONNECTIONS=$(sudo -u postgres psql -d parkingspots -t -c "SELECT count(*) FROM pg_stat_activity WHERE datname='parkingspots';" 2>/dev/null | tr -d ' ')
USERS=$(sudo -u postgres psql -d parkingspots -t -c "SELECT count(*) FROM users;" 2>/dev/null | tr -d ' ')
SPOTS=$(sudo -u postgres psql -d parkingspots -t -c "SELECT count(*) FROM parking_spots;" 2>/dev/null | tr -d ' ')
BOOKINGS=$(sudo -u postgres psql -d parkingspots -t -c "SELECT count(*) FROM bookings;" 2>/dev/null | tr -d ' ')

echo -e "   Active connections: ${BLUE}${CONNECTIONS}${NC}"
echo -e "   Total users: ${BLUE}${USERS}${NC}"
echo -e "   Total parking spots: ${BLUE}${SPOTS}${NC}"
echo -e "   Total bookings: ${BLUE}${BOOKINGS}${NC}"

# Summary
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ Load Testing Complete${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}Performance Summary:${NC}"
echo -e "   • Average response time: ~${AVG_TIME}ms"
echo -e "   • Estimated RPS: ~${RPS}"
echo -e "   • Cache efficiency: ${HIT_RATE}%"
echo -e "   • Database load: ${CONNECTIONS} connections"
echo ""
echo -e "${BLUE}For detailed load testing with Apache Bench:${NC}"
echo -e "   sudo apt install apache2-utils"
echo -e "   ab -n 1000 -c 100 ${API_URL}/api/v1/parking-spots/?limit=10"
