#!/bin/bash

API_KEY="oQbQqRnb"
API_SECRET="LOY3MAKP5U4B3LLQMXJP3XIFEM"
CLIENT_CODE="A972731"
API_URL="https://apiconnect.angelone.in/rest/secure/login"

echo "════════════════════════════════════════════════════════════"
echo "🔐 TESTING ANGEL ONE SmartAPI AUTHENTICATION"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "📍 Endpoint: $API_URL"
echo "📍 Client Code: $CLIENT_CODE"
echo ""
echo "🔄 Sending POST request..."
echo ""

curl -v -X POST "$API_URL" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"clientcode\": \"$CLIENT_CODE\",
    \"password\": \"$API_SECRET\",
    \"totp\": \"000000\"
  }"

echo ""
echo ""
echo "════════════════════════════════════════════════════════════"

