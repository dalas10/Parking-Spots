#!/bin/bash
# Install Apache Bench for advanced load testing

echo "📦 Installing Apache Bench (ab)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if command -v ab &> /dev/null; then
    echo "✓ Apache Bench is already installed"
    ab -V | head -1
    exit 0
fi

echo ""
echo "Installing apache2-utils package..."
sudo apt update && sudo apt install -y apache2-utils

echo ""
if command -v ab &> /dev/null; then
    echo "✅ Apache Bench installed successfully!"
    ab -V | head -1
    echo ""
    echo "Example usage:"
    echo "  ab -n 1000 -c 100 http://localhost:8000/api/v1/parking-spots/?limit=10"
    echo ""
    echo "  -n: Total requests"
    echo "  -c: Concurrent requests"
else
    echo "❌ Installation failed"
    exit 1
fi
