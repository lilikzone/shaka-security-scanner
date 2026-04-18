#!/bin/bash

# 🧪 DEV Environment Setup Script
# Sets up local testing environment for Shaka Security Scanner

set -e

echo "🚀 Setting up DEV environment..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p backend-logs
mkdir -p frontend-logs
mkdir -p test-results
echo -e "${GREEN}✓ Directories created${NC}"
echo ""

# Check Python version
echo "🐍 Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Python version: $PYTHON_VERSION"
if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo -e "${GREEN}✓ Python version OK${NC}"
else
    echo -e "${RED}✗ Python 3.8+ required${NC}"
    exit 1
fi
echo ""

# Check Node version
echo "📦 Checking Node version..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "   Node version: $NODE_VERSION"
    echo -e "${GREEN}✓ Node installed${NC}"
else
    echo -e "${RED}✗ Node.js not found${NC}"
    exit 1
fi
echo ""

# Check AWS CLI
echo "☁️  Checking AWS CLI..."
if command -v aws &> /dev/null; then
    AWS_VERSION=$(aws --version 2>&1 | awk '{print $1}')
    echo "   $AWS_VERSION"
    echo -e "${GREEN}✓ AWS CLI installed${NC}"
else
    echo -e "${RED}✗ AWS CLI not found${NC}"
    exit 1
fi
echo ""

# Verify AWS sandbox profile
echo "🔐 Verifying AWS sandbox profile..."
if aws configure list --profile sandbox &> /dev/null; then
    echo "   Profile: sandbox"
    ACCOUNT_ID=$(aws sts get-caller-identity --profile sandbox --query Account --output text 2>/dev/null || echo "N/A")
    echo "   Account ID: $ACCOUNT_ID"
    echo -e "${GREEN}✓ AWS sandbox profile configured${NC}"
else
    echo -e "${RED}✗ AWS sandbox profile not found${NC}"
    exit 1
fi
echo ""

# Test AWS Bedrock access
echo "🤖 Testing AWS Bedrock access..."
if aws bedrock list-foundation-models --profile sandbox --region us-east-1 --query 'modelSummaries[?modelId==`anthropic.claude-3-sonnet-20240229-v1:0`].modelId' --output text &> /dev/null; then
    echo "   Model: Claude 3 Sonnet"
    echo "   Region: us-east-1"
    echo -e "${GREEN}✓ AWS Bedrock accessible${NC}"
else
    echo -e "${YELLOW}⚠ AWS Bedrock access test failed (may need permissions)${NC}"
fi
echo ""

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd ..
if [ -f "pyproject.toml" ]; then
    echo "   Using Poetry..."
    if command -v poetry &> /dev/null; then
        poetry install --no-root
        echo -e "${GREEN}✓ Backend dependencies installed (Poetry)${NC}"
    else
        echo "   Poetry not found, using pip..."
        pip3 install -e . --quiet
        echo -e "${GREEN}✓ Backend dependencies installed (pip)${NC}"
    fi
else
    pip3 install -e . --quiet
    echo -e "${GREEN}✓ Backend dependencies installed${NC}"
fi
cd DEV
echo ""

# Install frontend dependencies
echo "🎨 Installing frontend dependencies..."
cd ../frontend
if [ -f "package.json" ]; then
    echo "   Running npm install..."
    npm install --silent
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠ package.json not found${NC}"
fi
cd ../DEV
echo ""

# Create test configuration
echo "⚙️  Creating test configuration..."
cat > test-config.yaml << 'EOF'
# Test Configuration for DEV Environment

target:
  url: "http://testphp.vulnweb.com"
  base_domain: "testphp.vulnweb.com"
  scheme: "http"

configuration:
  test_suites:
    - reconnaissance
    - vulnerability
  intensity: passive
  rate_limit: 5
  timeout: 30
  enable_ai_analysis: true
  enable_destructive_tests: false

aws:
  profile: sandbox
  region: us-east-1
  model_id: anthropic.claude-3-sonnet-20240229-v1:0
EOF
echo -e "${GREEN}✓ Test configuration created${NC}"
echo ""

# Create environment file for backend
echo "🔧 Creating backend environment file..."
cat > .env.backend << 'EOF'
# Backend Environment Variables
AWS_PROFILE=sandbox
AWS_DEFAULT_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
LOG_LEVEL=DEBUG
PORT=8000
HOST=0.0.0.0
EOF
echo -e "${GREEN}✓ Backend environment file created${NC}"
echo ""

# Create environment file for frontend
echo "🎨 Creating frontend environment file..."
cat > .env.frontend << 'EOF'
# Frontend Environment Variables
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NODE_ENV=development
PORT=3000
EOF
echo -e "${GREEN}✓ Frontend environment file created${NC}"
echo ""

# Make scripts executable
echo "🔐 Setting script permissions..."
chmod +x start-backend.sh 2>/dev/null || true
chmod +x start-frontend.sh 2>/dev/null || true
chmod +x run-test-scan.sh 2>/dev/null || true
chmod +x stop-all.sh 2>/dev/null || true
echo -e "${GREEN}✓ Script permissions set${NC}"
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ DEV Environment Setup Complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Next Steps:"
echo "   1. Start backend:  ./start-backend.sh"
echo "   2. Start frontend: ./start-frontend.sh"
echo "   3. Run test scan:  ./run-test-scan.sh"
echo ""
echo "📊 Monitoring:"
echo "   Backend:  http://localhost:8000"
echo "   Frontend: http://localhost:3000"
echo ""
echo "📝 Logs:"
echo "   Backend:  tail -f backend-logs/app.log"
echo "   Frontend: tail -f frontend-logs/next.log"
echo ""
echo "🛑 Stop all:  ./stop-all.sh"
echo ""
