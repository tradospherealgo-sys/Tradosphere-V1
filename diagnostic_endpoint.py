#!/usr/bin/env python3
"""
Diagnostic: Verify Angel One SmartAPI endpoint and request format
Check for endpoint mismatch or security blocks
"""

import os
import requests
import json
import pyotp
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

print("\n" + "="*80)
print("🔍 ANGEL ONE SMARTAPI ENDPOINT DIAGNOSTIC")
print("="*80)

# Credentials
API_KEY = os.getenv("ANGEL_ONE_API_KEY", "")
CLIENT_CODE = os.getenv("ANGEL_ONE_CLIENT_CODE", "")
PIN = os.getenv("ANGEL_ONE_PIN", "")
TOTP_SECRET = os.getenv("ANGEL_ONE_TOTP_SECRET", "")

# Generate TOTP
totp = pyotp.TOTP(TOTP_SECRET)
totp_code = totp.now()

# Current endpoint we're using
current_endpoint = "https://apiconnect.angelone.in/rest/secure/login"

print("\n1️⃣  ENDPOINT VERIFICATION:")
print("-" * 80)
print(f"Current endpoint: {current_endpoint}")

# Parse endpoint
parsed = urlparse(current_endpoint)
print(f"\n   Breakdown:")
print(f"   - Protocol: {parsed.scheme}")
print(f"   - Domain: {parsed.netloc}")
print(f"   - Path: {parsed.path}")
print(f"   - Full URL: {parsed.scheme}://{parsed.netloc}{parsed.path}")

print("\n📚 KNOWN ANGEL ONE SMARTAPI ENDPOINTS:")
print("   (From public documentation)")
known_endpoints = [
    "https://apiconnect.angelone.in/rest/secure/login",
    "https://api.angelone.in/rest/secure/login",
    "https://smartapi.angelone.in/api/generateSession",
    "https://api.smartapi.angelone.in/rest/secure/login",
]
for endpoint in known_endpoints:
    marker = "✓ CURRENT" if endpoint == current_endpoint else " "
    print(f"   [{marker}] {endpoint}")

print("\n2️⃣  REQUEST HEADERS:")
print("-" * 80)

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

print(f"   Authorization: Bearer {API_KEY[:5]}...{API_KEY[-3:]} (hidden)")
print(f"   Content-Type: {headers['Content-Type']}")
print(f"   User-Agent: requests/2.31.0 (default)")
print(f"   Accept-Encoding: gzip, deflate")
print(f"   Accept: */*")

print("\n3️⃣  REQUEST PAYLOAD:")
print("-" * 80)

payload = {
    "clientcode": CLIENT_CODE,
    "password": PIN,
    "totp": totp_code
}

print(f"   clientcode: {CLIENT_CODE}")
print(f"   password: {PIN}")
print(f"   totp: {totp_code}")

print("\n4️⃣  FINAL REQUEST DETAILS:")
print("-" * 80)
print(f"\nRequest URL (final):")
print(f"   {current_endpoint}")

print(f"\nRequest Method: POST")

print(f"\nRequest Headers (with secrets masked):")
print(f"   Authorization: Bearer {API_KEY[:5]}...{API_KEY[-3:]}")
print(f"   Content-Type: application/json")

print(f"\nRequest Body (JSON):")
print(f"   {json.dumps(payload, indent=6)}")

print("\n5️⃣  SECURITY CHECK:")
print("-" * 80)

# Check for potential issues
checks = []

# Check 1: Bearer token format
if len(API_KEY) < 8:
    checks.append("⚠️  API Key seems very short (< 8 chars)")
else:
    checks.append("✅ API Key length reasonable")

# Check 2: Client code format
if not CLIENT_CODE.startswith("A"):
    checks.append(f"⚠️  Client Code doesn't start with 'A' (unusual): {CLIENT_CODE}")
else:
    checks.append("✅ Client Code format looks standard")

# Check 3: PIN format
if len(PIN) < 4:
    checks.append(f"⚠️  PIN seems too short: {PIN}")
else:
    checks.append("✅ PIN length reasonable")

# Check 4: TOTP
if len(totp_code) != 6 or not totp_code.isdigit():
    checks.append(f"⚠️  TOTP format invalid: {totp_code}")
else:
    checks.append(f"✅ TOTP format valid: {totp_code} (6 digits)")

for check in checks:
    print(f"   {check}")

print("\n6️⃣  SENDING TEST REQUEST...")
print("-" * 80)

try:
    response = requests.post(current_endpoint, json=payload, headers=headers, timeout=15)

    print(f"\n✅ Request sent successfully")
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Headers:")
    for key, value in response.headers.items():
        if key.lower() not in ['set-cookie', 'authorization']:
            print(f"   {key}: {value}")

    print(f"\nResponse Body (first 500 chars):")
    print(f"   {response.text[:500]}")

    # Analysis
    print("\n7️⃣  DIAGNOSIS:")
    print("-" * 80)

    if response.status_code == 200:
        print("✅ HTTP 200: Endpoint is reachable")
        if "<!DOCTYPE" in response.text or "<html" in response.text:
            print("❌ Response is HTML (not JSON)")
            print("   → Possible issues:")
            print("     • API endpoint might have changed")
            print("     • API key/credentials might be invalid")
            print("     • Account might not have API access")
            print("     • Request might be blocked by WAF/security")
        else:
            print("🔍 Response format unclear")
    else:
        print(f"❌ HTTP {response.status_code}: Unexpected status")
        print("   → Possible endpoint issue")

    if "Request Rejected" in response.text:
        print("\n🚨 'Request Rejected' message detected")
        print("   → This typically means:")
        print("     • Invalid credentials for the API")
        print("     • API access not enabled on account")
        print("     • Security/IP restriction")
        print("     • API key expired or revoked")

except Exception as e:
    print(f"\n❌ Error: {str(e)}")

print("\n" + "="*80)
print("RECOMMENDATION:")
print("="*80)
print("""
To confirm if this is endpoint vs credential issue:

1. Check Angel One SmartAPI documentation for current endpoint:
   https://smartapi.angelbroking.com/docs

2. Verify account has API access enabled:
   - Log into https://smartapi.angelbroking.com/
   - Check Settings → API Settings
   - Confirm API Access is ACTIVE

3. If endpoint has changed, update BASE_URL in market_data.py

4. If credentials are invalid, generate new API key from dashboard
""")
print("="*80 + "\n")
