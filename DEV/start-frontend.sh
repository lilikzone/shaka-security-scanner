#!/bin/bash

# 🎨 Start Frontend Development Server
# Starts the Next.js frontend with hot reload

set -e

echo "🎨 Starting Shaka Security Scanner Frontend..."
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Load environment variables
if [ -f ".env.frontend" ]; then
    export $(cat .env.frontend | grep -v '^#' | xargs)
    echo -e "${GREEN}✓ Environment variables loaded${NC}"
else
    echo -e "${YELLOW}⚠ .env.frontend not found, using defaults${NC}"
    export NEXT_PUBLIC_API_URL=http://localhost:8000
    export PORT=3000
fi
echo ""

# Check if port is available
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${RED}✗ Port $PORT is already in use${NC}"
    echo "  Kill the process or use a different port"
    exit 1
fi

# Check if backend is running
echo "🔍 Checking backend availability..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend is running${NC}"
else
    echo -e "${YELLOW}⚠ Backend is not running${NC}"
    echo "  Start backend first: ./start-backend.sh"
fi
echo ""

# Create log directory
mkdir -p frontend-logs

# Navigate to frontend directory
cd ../frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo -e "${GREEN}✓ Dependencies installed${NC}"
    echo ""
fi

# Copy environment file
cp ../DEV/.env.frontend .env.local

# Start development server
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎨 Starting Frontend Server...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "📊 Server Info:"
echo "   URL: http://localhost:$PORT"
echo "   API: $NEXT_PUBLIC_API_URL"
echo "   Environment: development"
echo "   Hot Reload: enabled"
echo ""
echo "📝 Logs: ../DEV/frontend-logs/next.log"
echo ""
echo "🛑 Press Ctrl+C to stop"
echo ""

# Start Next.js dev server with logging
npm run dev 2>&1 | tee ../DEV/frontend-logs/next.log
