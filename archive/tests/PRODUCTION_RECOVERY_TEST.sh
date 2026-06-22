#!/bin/bash

# TRADOSPHERE PRODUCTION RECOVERY TEST
# This script verifies the production deployment is working correctly
# Run this AFTER:
# 1. Vercel redeploys with new code (auto-deploys after commit d6e8149)
# 2. NEXT_PUBLIC_API_URL is set on Vercel dashboard
# 3. Angel One credentials are set on Railway dashboard

set -e

VERCEL_URL="https://tradosphere-v1.vercel.app"
RAILWAY_URL="https://tradosphere-v1-production.up.railway.app"
TEMP_FILE="/tmp/tradosphere_test.html"

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║        TRADOSPHERE PRODUCTION DEPLOYMENT VERIFICATION        ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# TEST 1: Verify config.js is accessible
echo "TEST 1: Verify config.js loads from Vercel"
echo "─────────────────────────────────────────"
config_status=$(curl -s -o /dev/null -w "%{http_code}" "$VERCEL_URL/config.js")
if [ "$config_status" = "200" ]; then
    echo "✓ config.js returns HTTP 200"
    config_content=$(curl -s "$VERCEL_URL/config.js")
    if echo "$config_content" | grep -q "API_BASE_URL"; then
        echo "✓ config.js contains API_BASE_URL"
    else
        echo "✗ config.js missing API_BASE_URL"
        exit 1
    fi
    if echo "$config_content" | grep -q "railway.app"; then
        echo "✓ config.js contains Railway URL fallback"
    else
        echo "✗ config.js missing Railway URL"
        exit 1
    fi
else
    echo "✗ config.js returns HTTP $config_status (expected 200)"
    exit 1
fi
echo ""

# TEST 2: Verify Vercel dashboard loads
echo "TEST 2: Verify Vercel dashboard HTML loads"
echo "──────────────────────────────────────────"
dashboard_status=$(curl -s -o /dev/null -w "%{http_code}" "$VERCEL_URL/")
if [ "$dashboard_status" = "200" ]; then
    echo "✓ Vercel dashboard returns HTTP 200"
    # Check if it contains the config.js script tag
    dashboard_html=$(curl -s "$VERCEL_URL/" | head -50)
    if echo "$dashboard_html" | grep -q "script.*config.js"; then
        echo "✓ Dashboard HTML contains <script src=\"config.js\"></script>"
    else
        echo "✗ Dashboard HTML missing config.js import"
        exit 1
    fi
else
    echo "✗ Dashboard returns HTTP $dashboard_status"
    exit 1
fi
echo ""

# TEST 3: Verify Railway backend is accessible
echo "TEST 3: Verify Railway backend health"
echo "────────────────────────────────────"
health_response=$(curl -s "$RAILWAY_URL/api/health")
if echo "$health_response" | grep -q '"status":"healthy"'; then
    echo "✓ Railway /api/health returns healthy"
else
    echo "⚠ Railway health status: $(echo $health_response | grep -o '"status":"[^"]*"')"
fi
echo ""

# TEST 4: Verify signal generation endpoint works
echo "TEST 4: Verify signal generation endpoint"
echo "────────────────────────────────────────"
signal_response=$(curl -s -X POST "$RAILWAY_URL/api/generate" \
    -H "Content-Type: application/json" \
    -d '{}')

if echo "$signal_response" | grep -q '"status":"success"'; then
    echo "✓ Signal generation returns success"

    # Check price source
    price_source=$(echo "$signal_response" | grep -o '"price_source":"[^"]*"')
    echo "  Price source: $price_source"

    # Check number of signals
    signal_count=$(echo "$signal_response" | grep -o '"symbol"' | wc -l)
    echo "  Signals generated: $signal_count"

    if echo "$signal_response" | grep -q '"price_source":"live_angel_one"'; then
        echo "✓ Using LIVE Angel One prices (broker connected)"
    elif echo "$signal_response" | grep -q '"price_source":"fallback"'; then
        echo "⚠ Using FALLBACK prices (Angel One not connected - check Railway env vars)"
    fi
else
    echo "✗ Signal generation failed"
    echo "Response: $signal_response"
    exit 1
fi
echo ""

# TEST 5: Verify market data endpoint works
echo "TEST 5: Verify live market data endpoint"
echo "──────────────────────────────────────"
market_status=$(curl -s -o /dev/null -w "%{http_code}" \
    -X GET "$RAILWAY_URL/api/market/live" \
    -H "Authorization: Bearer test_token")

if [ "$market_status" = "401" ]; then
    echo "✓ Market endpoint requires authentication (expected)"
elif [ "$market_status" = "200" ]; then
    echo "✓ Market endpoint returns data"
else
    echo "✗ Market endpoint returned HTTP $market_status"
fi
echo ""

# TEST 6: Frontend → Backend communication test
echo "TEST 6: Frontend → Backend communication"
echo "───────────────────────────────────────"
cat > "$TEMP_FILE" << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Test</title>
    <script src="config.js"></script>
</head>
<body>
    <script>
        console.log('API_BASE_URL:', typeof window.API_BASE_URL !== 'undefined' ? window.API_BASE_URL : 'UNDEFINED');
        fetch(window.API_BASE_URL + '/api/generate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({})
        })
        .then(r => r.json())
        .then(data => {
            console.log('API call successful:', data.status);
            if (data.status === 'success') {
                console.log('✓ Frontend → Backend communication working');
            }
        })
        .catch(e => console.log('✗ Error:', e));
    </script>
</body>
</html>
EOF

echo "⚠ Frontend → Backend test requires browser execution"
echo "  Visit: $VERCEL_URL in browser"
echo "  Open Developer Tools → Console"
echo "  Should see: ✓ Frontend → Backend communication working"
echo ""

# SUMMARY
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                    DEPLOYMENT CHECKLIST                      ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "✓ Config.js deployed and accessible"
echo "✓ Vercel dashboard HTML updated with config.js import"
echo "✓ Railway backend responding to API calls"
echo "✓ Signal generation endpoint working"
echo ""
echo "NEXT STEPS (Manual):"
echo "1. Go to https://vercel.com/projects/tradosphere-v1"
echo "   → Settings → Environment Variables"
echo "   → Add: NEXT_PUBLIC_API_URL = https://tradosphere-v1-production.up.railway.app"
echo "   → Redeploy"
echo ""
echo "2. Go to https://railway.app"
echo "   → Select tradosphere-v1 project"
echo "   → Variables tab"
echo "   → Add: ANGEL_ONE_API_KEY=2G8dEMEq"
echo "   → Add: ANGEL_ONE_CLIENT_CODE=M625536"
echo "   → Add: ANGEL_ONE_PIN=3958"
echo "   → Add: ANGEL_ONE_TOTP_SECRET=W7IMZ4ZLGFWR2SYX4OXFBSU2DM"
echo "   → Redeploy"
echo ""
echo "3. Test: curl -X POST https://tradosphere-v1-production.up.railway.app/api/generate"
echo "         Should show: \"price_source\":\"live_angel_one\""
echo ""
