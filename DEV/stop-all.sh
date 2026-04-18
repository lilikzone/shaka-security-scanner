#!/bin/bash

# 🛑 Stop All Services
# Stops backend and frontend servers

echo "🛑 Stopping all services..."
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Stop backend (port 8000)
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "🔴 Stopping backend (port 8000)..."
    kill $(lsof -t -i:8000) 2>/dev/null || true
    echo -e "${GREEN}✓ Backend stopped${NC}"
else
    echo "   Backend not running"
fi

# Stop frontend (port 3000)
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "🔴 Stopping frontend (port 3000)..."
    kill $(lsof -t -i:3000) 2>/dev/null || true
    echo -e "${GREEN}✓ Frontend stopped${NC}"
else
    echo "   Frontend not running"
fi

echo ""
echo -e "${GREEN}✅ All services stopped${NC}"
echo ""
