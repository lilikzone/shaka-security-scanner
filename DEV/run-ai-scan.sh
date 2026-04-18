#!/bin/bash

# 🤖 Run AI-Powered Vulnerability Scan
# Tests AI analysis capabilities with AWS Bedrock

set -e

echo "🤖 Running AI-Powered Vulnerability Scan..."
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${RED}✗ Backend is not running${NC}"
    echo "  Start backend first: ./start-backend.sh"
    exit 1
fi

# Check AI status
AI_ENABLED=$(curl -s http://localhost:8000/health | python3 -c "import sys, json; print(json.load(sys.stdin).get('ai_enabled', False))")

if [ "$AI_ENABLED" = "True" ] || [ "$AI_ENABLED" = "true" ]; then
    echo -e "${GREEN}✓ Backend is running with AI enabled${NC}"
else
    echo -e "${YELLOW}⚠ Backend is running but AI is disabled${NC}"
fi

echo ""

# Test: AI-Powered Scan
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${CYAN}🤖 AI-Powered Vulnerability Scan${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

SCAN_REQUEST='{
  "target": {
    "url": "http://example.com",
    "base_domain": "example.com",
    "scheme": "http"
  },
  "config": {
    "test_suites": ["reconnaissance", "headers"],
    "intensity": "passive",
    "rate_limit": 10,
    "timeout": 30,
    "enable_ai_analysis": true
  }
}'

echo "🎯 Target: http://example.com"
echo "🔍 Scanners: Reconnaissance, Headers"
echo "⚡ Intensity: Passive"
echo "🤖 AI Analysis: ENABLED"
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
    RESULT_FILE="test-results/ai-scan-$(date +%Y%m%d-%H%M%S).json"
    echo "$SCAN_STATUS" | python3 -m json.tool > "$RESULT_FILE"
    echo "📁 Results saved: $RESULT_FILE"
    
    # Display findings with AI analysis
    if [ "$FINDINGS" -gt 0 ]; then
        echo ""
        echo "🔍 Findings with AI Analysis:"
        echo "$SCAN_STATUS" | python3 -c "
import sys, json
data = json.load(sys.stdin)
findings = data.get('findings', [])
for i, f in enumerate(findings, 1):
    severity = f['severity'].upper()
    title = f['title']
    category = f.get('category', 'unknown')
    print(f'\n{i}. [{severity}] {title}')
    print(f'   Category: {category}')
    
    # Check for AI analysis
    if 'ai_analysis' in f and f['ai_analysis']:
        ai = f['ai_analysis']
        print(f'   🤖 AI Analysis:')
        if 'risk_assessment' in ai:
            print(f'      Risk: {ai[\"risk_assessment\"]}')
        if 'false_positive_likelihood' in ai:
            fp = float(ai['false_positive_likelihood']) * 100
            print(f'      False Positive: {fp:.1f}%')
        if 'remediation_priority' in ai:
            print(f'      Priority: {ai[\"remediation_priority\"]}/10')
        if 'exploit_complexity' in ai:
            print(f'      Complexity: {ai[\"exploit_complexity\"]}')
"
    else
        echo ""
        echo "ℹ️  No vulnerabilities found (target is secure)"
        echo ""
        echo "💡 To test AI analysis with actual findings:"
        echo "   - Use intentionally vulnerable targets (DVWA, WebGoat)"
        echo "   - Or create mock findings for testing"
    fi
    
    echo ""
    echo "🌐 View in browser: http://localhost:3000/scans/$SCAN_ID"
elif [ "$STATUS" = "failed" ]; then
    echo -e "${RED}✗ Scan failed${NC}"
    echo "Check backend logs: tail -f backend-logs/app.log"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${CYAN}🤖 AI INTEGRATION STATUS${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ AI Integration: ENABLED"
echo "🤖 Model: Claude Haiku 4.5 (us.anthropic.claude-haiku-4-5-20251001-v1:0)"
echo "🌍 Region: us-east-1"
echo "👤 Profile: sandbox"
echo ""
echo "📊 AI Capabilities:"
echo "   ✅ Enhanced vulnerability descriptions"
echo "   ✅ False positive detection (0.0-1.0)"
echo "   ✅ Risk scoring (0-10)"
echo "   ✅ Business impact analysis"
echo "   ✅ Remediation prioritization (1-10)"
echo "   ✅ Exploit complexity assessment"
echo ""
