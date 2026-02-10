#!/bin/bash
# Quick setup script for production deployment tools

set -e

echo "🔧 Setting up Production Tools"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Make all scripts executable
echo ""
echo "1️⃣ Making scripts executable..."
chmod +x start_production.sh
chmod +x start_workers.sh
chmod +x run_background_tasks.py
chmod +x load_test.sh
chmod +x monitor.sh
chmod +x check_postgres_config.sh
echo "   ✓ All scripts are now executable"

# Check for Apache Bench
echo ""
echo "2️⃣ Checking for Apache Bench (load testing tool)..."
if ! command -v ab &> /dev/null; then
    echo "   ⚠ Apache Bench not found"
    echo "   To install: sudo apt install apache2-utils"
else
    AB_VERSION=$(ab -V | head -1)
    echo "   ✓ $AB_VERSION"
fi

# Check Redis
echo ""
echo "3️⃣ Checking Redis..."
if redis-cli ping &> /dev/null; then
    REDIS_VERSION=$(redis-cli INFO server | grep "redis_version" | cut -d: -f2 | tr -d '\r')
    echo "   ✓ Redis $REDIS_VERSION is running"
else
    echo "   ✗ Redis is not running"
    echo "   To start: sudo systemctl start redis"
fi

# Check PostgreSQL
echo ""
echo "4️⃣ Checking PostgreSQL..."
if sudo -u postgres psql -c "SELECT version();" &> /dev/null; then
    PG_VERSION=$(sudo -u postgres psql -t -c "SHOW server_version;" | tr -d ' ')
    echo "   ✓ PostgreSQL $PG_VERSION is running"
    
    # Check database
    if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw parkingspots; then
        echo "   ✓ Database 'parkingspots' exists"
        
        # Check data
        SPOTS=$(sudo -u postgres psql -d parkingspots -t -c "SELECT count(*) FROM parking_spots;" 2>/dev/null | tr -d ' ')
        echo "   ✓ $SPOTS parking spots in database"
    else
        echo "   ⚠ Database 'parkingspots' not found"
    fi
else
    echo "   ✗ PostgreSQL is not running"
    echo "   To start: sudo systemctl start postgresql"
fi

# Check Python environment
echo ""
echo "5️⃣ Checking Python environment..."
if [ -d "venv" ]; then
    echo "   ✓ Virtual environment exists"
    source venv/bin/activate
    
    # Check key packages
    if python -c "import fastapi" 2>/dev/null; then
        echo "   ✓ FastAPI is installed"
    else
        echo "   ✗ FastAPI not found"
    fi
    
    if python -c "import redis" 2>/dev/null; then
        echo "   ✓ Redis client is installed"
    else
        echo "   ✗ Redis client not found"
    fi
    
    if python -c "import asyncpg" 2>/dev/null; then
        echo "   ✓ asyncpg (PostgreSQL driver) is installed"
    else
        echo "   ✗ asyncpg not found"
    fi
else
    echo "   ✗ Virtual environment not found"
    echo "   Create one: python3 -m venv venv"
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Setup Complete!"
echo ""
echo "📝 Available Commands:"
echo "   ./start_production.sh     - Start API + Background tasks"
echo "   ./start_workers.sh        - Start API only"
echo "   ./load_test.sh            - Run load tests"
echo "   ./monitor.sh              - Real-time monitoring"
echo "   ./check_postgres_config.sh - Check PostgreSQL settings"
echo ""
echo "📊 Next Steps:"
echo "   1. Review PostgreSQL config: ./check_postgres_config.sh"
echo "   2. Start production: ./start_production.sh"
echo "   3. Run load test: ./load_test.sh"
echo "   4. Monitor performance: ./monitor.sh"
