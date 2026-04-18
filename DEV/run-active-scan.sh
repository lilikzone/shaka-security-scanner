#!/bin/bash

# 🧪 Run Active Vulnerability Scan
# Tests with ACTIVE intensity for better detection

set -e

echo "🧪 Running Active Vulnerability Scan..."
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${RED}✗ Backend is not running${NC}"
    echo "  Start backend first: ./start-backend.sh"
    exit 1
fi

echo -e "${GREEN}✓ Backend is running${NC}"
echo ""

# Test: Active Vulnerability Scan
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}📊 Active Vulnerability Scan${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

SCAN_REQUEST='{
  "target": {
    "url": "http://example.com",
    "base_domain": "example.com",
    "scheme": "http"
  },
  "config": {
    "test_suites": ["reconnaissance", "vulnerability", "headers", "authentication"],
    "intensity": "active",
    "rate_limit": 10,
    "timeout": 30,
    "enable_ai_analysis": false
  }
}'

echo "🎯 Target: http://example.com"
echo "🔍 Scanners: Reconnaissance, Vulnerability, Headers, Authentication"
echo "⚡ Intensity: Active"
echo ""

RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/scans \
  -H "Content-Type: application/json" \
  -d "$SCAN_REQUEST")

SCAN_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('scan_id', ''))")

if [ -z "$SCAN_ID" ]; then
    echo -e "${RED}✗ Failed to create scan${NC}"
    echo "Response: $RESPONSE"
    exit 1
fi

echo -e "${GREEN}✓ Scan created: $SCAN_ID${NC}"
echo ""

# Monitor scan
echo "📊 Monitoring scan progress..."
while true; do
    SCAN_STATUS=$(curl -s http://localhost:8000/api/v1/scans/$SCAN_ID)
    STATUS=$(echo $SCAN_STATUS | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))")
    PROGRESS=$(echo $SCAN_STATUS | python3 -c "import sys, json; print(json.load(sys.stdin).get('progress', 0))")
    FINDINGS=$(echo $SCAN_STATUS | python3 -c "import sys, json; print(json.load(sys.stdin).get('findings_count', 0))")
    
    PROGRESS_PCT=$(python3 -c "print(int(float($PROGRESS) * 100))")
    echo -ne "\r   Status: $STATUS | Progress: $PROGRESS_PCT% | Findings: $FINDINGS"
    
    if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; then
        echo ""
        break
    fi
    sleep 2
done

echo ""
if [ "$STATUS" = "completed" ]; then
    echo -e "${GREEN}✅ Scan completed: $FINDINGS findings${NC}"
    
    # Save results
    mkdir -p test-results
    RESULT_FILE="test-results/active-scan-$(date +%Y%m%d-%H%M%S).json"
    echo "$SCAN_STATUS" | python3 -m json.tool > "$RESULT_FILE"
    echo "📁 Results saved: $RESULT_FILE"
    
    # Display findings
    if [ "$FINDINGS" -gt 0 ]; then
        echo ""
        echo "🔍 Findings:"
        echo "$SCAN_STATUS" | python3 -c "
import sys, json
data = json.load(sys.stdin)
findings = data.get('findings', [])
for f in findings:
    severity = f['severity'].upper()
    title = f['title']
    category = f.get('category', 'unknown')
    print(f'   [{severity}] {title} ({category})')
"
    fi
    
    echo ""
    echo "🌐 View in browser: http://localhost:3000/scans/$SCAN_ID"
elif [ "$STATUS" = "failed" ]; then
    echo -e "${RED}✗ Scan failed${NC}"
    echo "Check backend logs: tail -f backend-logs/app.log"
fi

echo ""
