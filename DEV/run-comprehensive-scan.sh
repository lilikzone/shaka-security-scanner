#!/bin/bash

# 🧪 Run Comprehensive Test Scan
# Tests multiple scanner modules against a vulnerable target

set -e

echo "🧪 Running Comprehensive Test Scan..."
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

# Test 1: Reconnaissance + Headers + SSL/TLS
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}📊 Test 1: Security Headers & SSL/TLS Analysis${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

SCAN_REQUEST_1='{
  "target": {
    "url": "http://testphp.vulnweb.com",
    "base_domain": "testphp.vulnweb.com",
    "scheme": "http"
  },
  "config": {
    "test_suites": ["reconnaissance", "headers"],
    "intensity": "passive",
    "rate_limit": 10,
    "timeout": 30,
    "enable_ai_analysis": false
  }
}'

echo "🎯 Target: http://testphp.vulnweb.com"
echo "🔍 Scanners: Reconnaissance, Headers"
echo "⚡ Intensity: Passive"
echo ""

RESPONSE_1=$(curl -s -X POST http://localhost:8000/api/v1/scans \
  -H "Content-Type: application/json" \
  -d "$SCAN_REQUEST_1")

SCAN_ID_1=$(echo $RESPONSE_1 | python3 -c "import sys, json; print(json.load(sys.stdin).get('scan_id', ''))")

if [ -z "$SCAN_ID_1" ]; then
    echo -e "${RED}✗ Failed to create scan${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Scan created: $SCAN_ID_1${NC}"
echo ""

# Monitor scan 1
echo "📊 Monitoring scan progress..."
while true; do
    SCAN_STATUS=$(curl -s http://localhost:8000/api/v1/scans/$SCAN_ID_1)
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
    echo -e "${GREEN}✅ Test 1 completed: $FINDINGS findings${NC}"
    
    # Save results
    mkdir -p test-results
    RESULT_FILE_1="test-results/comprehensive-test1-$(date +%Y%m%d-%H%M%S).json"
    echo "$SCAN_STATUS" | python3 -m json.tool > "$RESULT_FILE_1"
    
    # Display findings
    if [ "$FINDINGS" -gt 0 ]; then
        echo ""
        echo "🔍 Findings:"
        echo "$SCAN_STATUS" | python3 -c "
import sys, json
data = json.load(sys.stdin)
findings = data.get('findings', [])
for f in findings:
    print(f\"   [{f['severity'].upper()}] {f['title']}\")
"
    fi
fi

echo ""
echo ""

# Test 2: CMS Vulnerability Scan
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}📊 Test 2: CMS Vulnerability Detection${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

SCAN_REQUEST_2='{
  "target": {
    "url": "https://wordpress.org",
    "base_domain": "wordpress.org",
    "scheme": "https"
  },
  "config": {
    "test_suites": ["cms_vulnerability"],
    "intensity": "passive",
    "rate_limit": 5,
    "timeout": 30,
    "enable_ai_analysis": false
  }
}'

echo "🎯 Target: https://wordpress.org"
echo "🔍 Scanners: CMS Vulnerability"
echo "⚡ Intensity: Passive"
echo ""

RESPONSE_2=$(curl -s -X POST http://localhost:8000/api/v1/scans \
  -H "Content-Type: application/json" \
  -d "$SCAN_REQUEST_2")

SCAN_ID_2=$(echo $RESPONSE_2 | python3 -c "import sys, json; print(json.load(sys.stdin).get('scan_id', ''))")

if [ -z "$SCAN_ID_2" ]; then
    echo -e "${RED}✗ Failed to create scan${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Scan created: $SCAN_ID_2${NC}"
echo ""

# Monitor scan 2
echo "📊 Monitoring scan progress..."
while true; do
    SCAN_STATUS=$(curl -s http://localhost:8000/api/v1/scans/$SCAN_ID_2)
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
    echo -e "${GREEN}✅ Test 2 completed: $FINDINGS findings${NC}"
    
    # Save results
    RESULT_FILE_2="test-results/comprehensive-test2-$(date +%Y%m%d-%H%M%S).json"
    echo "$SCAN_STATUS" | python3 -m json.tool > "$RESULT_FILE_2"
    
    # Display findings
    if [ "$FINDINGS" -gt 0 ]; then
        echo ""
        echo "🔍 Findings:"
        echo "$SCAN_STATUS" | python3 -c "
import sys, json
data = json.load(sys.stdin)
findings = data.get('findings', [])
for f in findings:
    print(f\"   [{f['severity'].upper()}] {f['title']}\")
"
    fi
fi

echo ""
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}📊 COMPREHENSIVE SCAN SUMMARY${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Test 1 (Headers & SSL): $SCAN_ID_1"
echo "✅ Test 2 (CMS Detection): $SCAN_ID_2"
echo ""
echo "📁 Results saved in: test-results/"
echo ""
echo "🌐 View in browser:"
echo "   http://localhost:3000/scans/$SCAN_ID_1"
echo "   http://localhost:3000/scans/$SCAN_ID_2"
echo ""
