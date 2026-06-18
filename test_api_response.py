#!/usr/bin/env python3
"""
Quick API Test - Shows EXACT error from Angel One API
Helps diagnose if issue is credentials or API access
"""

import requests
import json
from datetime import datetime

# Current credentials in your system
API_KEY = "oQbQqRnb"
API_SECRET = "LOY3MAKP5U4B3LLQMXJP3XIFEM"
CLIENT_CODE = "A972731"

BASE_URL = "https://apiconnect.angelone.in/rest/secure"

print("\n" + "="*70)
print("🔍 ANGEL ONE API DIAGNOSTIC TEST")
print("="*70)
print(f"📍 Timestamp: {datetime.now().isoformat()}")
print(f"📍 Target: {BASE_URL}/login")
print(f"📍 Client Code: {CLIENT_CODE}")
print(f"📍 API Key: {API_KEY[:5]}...{API_KEY[-3:]}")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "clientcode": CLIENT_CODE,
    "password": API_SECRET,
    "totp": "000000"
}

print("\n📤 REQUEST DETAILS:")
print(f"   Method: POST")
print(f"   URL: {BASE_URL}/login")
print(f"   Headers: {json.dumps({'Authorization': f'Bearer {API_KEY[:5]}...', 'Content-Type': 'application/json'}, indent=6)}")
print(f"   Payload: {json.dumps(payload, indent=6)}")

try:
    print("\n⏳ Sending request...")
    response = requests.post(
        f"{BASE_URL}/login",
        json=payload,
        headers=headers,
        timeout=15
    )

    print("\n✅ RESPONSE RECEIVED:")
    print(f"   Status Code: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('Content-Type', 'unknown')}")
    print(f"   Response Length: {len(response.text)} chars")

    print("\n📋 RESPONSE BODY:")
    print("-" * 70)

    # Try to parse as JSON
    try:
        json_data = response.json()
        print("✅ JSON Response:")
        print(json.dumps(json_data, indent=2))

        if json_data.get("status"):
            print("\n✅ STATUS: SUCCESS")
            if json_data.get("data"):
                jwt = json_data.get("data", {}).get("jwtToken")
                print(f"   JWT Token: {jwt[:50]}...")
        else:
            print(f"\n❌ STATUS: FAILED")
            print(f"   Message: {json_data.get('message', 'No message')}")

    except json.JSONDecodeError:
        print("❌ NOT JSON - Response is HTML or plain text:")
        print(response.text[:500])
        if len(response.text) > 500:
            print(f"   ... (truncated, total length: {len(response.text)} chars)")

    print("\n" + "-" * 70)

    # Diagnosis
    print("\n🔍 DIAGNOSIS:")
    if response.status_code == 200:
        print("   ✅ Server is reachable (HTTP 200)")
        if "Request Rejected" in response.text or "<!DOCTYPE" in response.text:
            print("   ❌ BUT: Server returned HTML error, not JSON")
            print("   💡 This means:")
            print("      - Credentials might be invalid or expired")
            print("      - API access might be disabled on account")
            print("      - Account might have restrictions")
        elif "Invalid" in response.text or "unauthorized" in response.text.lower():
            print("   ❌ Authentication failed")
            print("   💡 Check if these are real Angel One credentials")
    elif response.status_code == 401:
        print("   ❌ Unauthorized (401)")
        print("   💡 Credentials are invalid or expired")
    elif response.status_code == 403:
        print("   ❌ Forbidden (403)")
        print("   💡 API access might be disabled on account")
    elif response.status_code == 400:
        print("   ❌ Bad Request (400)")
        print("   💡 Request format might be wrong")
    else:
        print(f"   ❌ Unexpected status: {response.status_code}")

except requests.exceptions.Timeout:
    print("\n❌ TIMEOUT: Server took too long to respond")
    print("   💡 Check internet connection or Angel One server status")
except requests.exceptions.ConnectionError as e:
    print(f"\n❌ CONNECTION ERROR: {str(e)}")
    print("   💡 Cannot reach apiconnect.angelone.in")
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")

print("\n" + "="*70)
print("📌 NEXT STEPS:")
print("="*70)
print("""
If credentials are invalid:
1. Go to https://smartapi.angelbroking.com/
2. Log in with your Angel One account
3. Go to Settings → API Settings
4. Copy REAL API Key, API Secret, Client Code
5. Update credentials in Tradosphere Settings tab

If API access is disabled:
- Contact Angel One support to enable API access on your account

If you need help, share the RESPONSE BODY section above!
""")
print("="*70 + "\n")
