#!/bin/bash

# 🧪 Run Test Scan
# Executes a test scan against a vulnerable test site

set -e

echo "🧪 Running Test Scan..."
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

# Create test scan request
echo "📝 Creating test scan..."
echo ""

SCAN_REQUEST='{
  "target": {
    "url": "http://testphp.vulnweb.com",
    "base_domain": "testphp.vulnweb.com",
    "scheme": "http"
  },
  "config": {
    "test_suites": ["reconnaissance", "vulnerability"],
    "intensity": "passive",
    "rate_limit": 5,
    "timeout": 30,
    "enable_ai_analysis": true
  }
}'

echo "🎯 Target: http://testphp.vulnweb.com"
echo "🔍 Scanners: Reconnaissance, Vulnerability"
echo "⚡ Intensity: Passive"
echo "🤖 AI Analysis: Enabled"
echo ""

# Create scan
echo "🚀 Launching scan..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/scans \
  -H "Content-Type: application/json" \
  -d "$SCAN_REQUEST")

SCAN_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('scan_id', ''))")

if [ -z "$SCAN_ID" ]; then
    echo -e "${RED}✗ Failed to create scan${NC}"
    echo "$RESPONSE"
    exit 1
fi

echo -e "${GREEN}✓ Scan created: $SCAN_ID${NC}"
echo ""

# Monitor scan progress
echo "📊 Monitoring scan progress..."
echo ""

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

# Display results
if [ "$STATUS" = "completed" ]; then
    echo -e "${GREEN}✅ Scan completed successfully!${NC}"
    echo ""
    
    # Save results
    mkdir -p test-results
    RESULT_FILE="test-results/scan-$SCAN_ID-$(date +%Y%m%d-%H%M%S).json"
    echo "$SCAN_STATUS" | python3 -m json.tool > "$RESULT_FILE"
    
    echo "📊 Scan Results:"
    echo "   Scan ID: $SCAN_ID"
    echo "   Findings: $FINDINGS"
    echo "   Results saved: $RESULT_FILE"
    echo ""
    
    # Display findings summary
    if [ "$FINDINGS" -gt 0 ]; then
        echo "🔍 Findings Summary:"
        echo "$SCAN_STATUS" | python3 -c "
import sys, json
data = json.load(sys.stdin)
findings = data.get('findings', [])
for f in findings[:5]:  # Show first 5
    print(f\"   [{f['severity'].upper()}] {f['title']}\")
if len(findings) > 5:
    print(f\"   ... and {len(findings) - 5} more\")
"
        echo ""
    fi
    
    echo "📝 View full results:"
    echo "   cat $RESULT_FILE | python3 -m json.tool"
    echo ""
    echo "🌐 View in browser:"
    echo "   http://localhost:3000/scans/$SCAN_ID"
    echo ""
    
elif [ "$STATUS" = "failed" ]; then
    echo -e "${RED}✗ Scan failed${NC}"
    echo ""
    echo "📝 Error details:"
    echo "$SCAN_STATUS" | python3 -m json.tool
    echo ""
else
    echo -e "${YELLOW}⚠ Scan status: $STATUS${NC}"
    echo ""
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
