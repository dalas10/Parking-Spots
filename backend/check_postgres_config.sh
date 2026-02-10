#!/bin/bash
# PostgreSQL Configuration Update Script
# Increases max_connections for multi-worker production setup

set -e

echo "📊 PostgreSQL Configuration Optimizer"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check current settings
echo ""
echo "1️⃣ Current PostgreSQL Settings:"
echo "--------------------------------"
sudo -u postgres psql -c "SHOW max_connections;" -t | xargs echo "   max_connections ="
sudo -u postgres psql -c "SHOW shared_buffers;" -t | xargs echo "   shared_buffers  ="

# Calculate recommended settings
TOTAL_RAM=$(free -g | awk '/^Mem:/{print $2}')
RECOMMENDED_BUFFERS=$((TOTAL_RAM / 4))

echo ""
echo "2️⃣ Recommended Settings:"
echo "------------------------"
echo "   max_connections = 300  (for 12 workers × 20 pool + overhead)"
echo "   shared_buffers  = ${RECOMMENDED_BUFFERS}GB  (25% of ${TOTAL_RAM}GB RAM)"

echo ""
echo "3️⃣ To apply these settings:"
echo "---------------------------"
echo "   sudo nano /etc/postgresql/14/main/postgresql.conf"
echo ""
echo "   Change the following lines:"
echo "   max_connections = 300"
echo "   shared_buffers = ${RECOMMENDED_BUFFERS}GB"
echo ""
echo "   Then restart PostgreSQL:"
echo "   sudo systemctl restart postgresql"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
