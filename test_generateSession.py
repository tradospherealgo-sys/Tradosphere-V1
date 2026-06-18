#!/usr/bin/env python3
"""
Minimal test for Angel One generateSession() endpoint
Print exact API response for debugging
"""

import os
import requests
import json
import pyotp
from dotenv import load_dotenv

load_dotenv()

print("\n" + "="*70)
print("🧪 MINIMAL ANGEL ONE generateSession() TEST")
print("="*70)

# Load credentials from .env
API_KEY = os.getenv("ANGEL_ONE_API_KEY", "")
CLIENT_CODE = os.getenv("ANGEL_ONE_CLIENT_CODE", "")
PIN = os.getenv("ANGEL_ONE_PIN", "")
TOTP_SECRET = os.getenv("ANGEL_ONE_TOTP_SECRET", "")

print("\n📋 LOADED CREDENTIALS FROM .env:")
print(f"   API Key: {API_KEY}")
print(f"   Client Code: {CLIENT_CODE}")
print(f"   PIN: {PIN}")
print(f"   TOTP Secret: {TOTP_SECRET[:10]}...{TOTP_SECRET[-4:]}")

# Generate TOTP
if TOTP_SECRET:
    totp = pyotp.TOTP(TOTP_SECRET)
    totp_code = totp.now()
    print(f"   Generated TOTP: {totp_code}")
else:
    totp_code = "000000"
    print(f"   Generated TOTP: {totp_code} (no secret provided)")

# Prepare request
BASE_URL = "https://apiconnect.angelone.in/rest/secure"
endpoint = f"{BASE_URL}/login"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "clientcode": CLIENT_CODE,
    "password": PIN,
    "totp": totp_code
}

print("\n📤 REQUEST:")
print(f"   URL: {endpoint}")
print(f"   Method: POST")
print(f"   Headers:")
print(f"      Authorization: Bearer {API_KEY[:8]}...{API_KEY[-4:]}")
print(f"      Content-Type: application/json")
print(f"   Body:")
print(f"      clientcode: {CLIENT_CODE}")
print(f"      password: {PIN}")
print(f"      totp: {totp_code}")

# Send request
print("\n⏳ Sending request...")

try:
    response = requests.post(endpoint, json=payload, headers=headers, timeout=15)

    print("\n📥 RESPONSE:")
    print(f"   HTTP Status: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('Content-Type', 'unknown')}")
    print(f"   Response Length: {len(response.text)} characters")

    print("\n📋 RAW RESPONSE BODY:")
    print("-" * 70)
    print(response.text)
    print("-" * 70)

    # Try to parse as JSON
    print("\n🔍 RESPONSE ANALYSIS:")
    try:
        json_data = response.json()
        print("✅ Valid JSON detected")
        print("\n📊 Parsed JSON:")
        print(json.dumps(json_data, indent=2))

        # Check for success
        if json_data.get("status"):
            print("\n✅ STATUS: SUCCESS")
            data = json_data.get("data", {})
            print(f"   JWT Token: {data.get('jwtToken', 'N/A')[:50]}...")
            print(f"   Session Token: {data.get('sessionToken', 'N/A')[:50]}...")
            print(f"   Feed Token: {data.get('feedToken', 'N/A')[:50]}...")
        else:
            print(f"\n❌ STATUS: FAILED")
            print(f"   Message: {json_data.get('message', 'No message')}")
            print(f"   Error Code: {json_data.get('errorcode', 'No code')}")

    except json.JSONDecodeError:
        print("❌ Not valid JSON")
        if "<!DOCTYPE" in response.text or "<html" in response.text:
            print("   Response is HTML (likely an error page)")
            # Extract title if present
            import re
            title_match = re.search(r'<title>(.*?)</title>', response.text)
            if title_match:
                print(f"   HTML Title: {title_match.group(1)}")
        else:
            print("   Response is plain text")

except requests.exceptions.Timeout:
    print("\n❌ Timeout: Server took too long to respond")
except requests.exceptions.ConnectionError as e:
    print(f"\n❌ Connection Error: {str(e)}")
except Exception as e:
    print(f"\n❌ Error: {str(e)}")

print("\n" + "="*70)
