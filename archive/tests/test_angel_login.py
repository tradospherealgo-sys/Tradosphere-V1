#!/usr/bin/env python3
"""
Angel One SmartAPI Login Test
Verify authentication with new account
"""

import os
import requests
import json
import pyotp
from dotenv import load_dotenv

load_dotenv()

print("\n" + "="*70)
print("🔑 ANGEL ONE SmartAPI LOGIN TEST")
print("="*70)

# Load credentials from .env
API_KEY = os.getenv("ANGEL_ONE_API_KEY", "")
CLIENT_CODE = os.getenv("ANGEL_ONE_CLIENT_CODE", "")
PIN = os.getenv("ANGEL_ONE_PIN", "")
TOTP_SECRET = os.getenv("ANGEL_ONE_TOTP_SECRET", "")

print("\n✅ CREDENTIALS LOADED FROM .env:")
print(f"   API Key: {API_KEY}")
print(f"   Client ID: {CLIENT_CODE}")
print(f"   PIN: {PIN}")
print(f"   TOTP Secret: {TOTP_SECRET[:8]}...{TOTP_SECRET[-4:]}")

# Generate TOTP
print("\n🔐 GENERATING TOTP...")
totp = pyotp.TOTP(TOTP_SECRET)
totp_code = totp.now()
print(f"   Generated TOTP: {totp_code}")

# Prepare request
endpoint = "https://apiconnect.angelone.in/rest/secure/login"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "clientcode": CLIENT_CODE,
    "password": PIN,
    "totp": totp_code
}

print("\n📡 CALLING generateSession()...")
print(f"   Endpoint: {endpoint}")
print(f"   Method: POST")

try:
    response = requests.post(endpoint, json=payload, headers=headers, timeout=15)

    print(f"\n📥 RESPONSE RECEIVED:")
    print(f"   HTTP Status: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('Content-Type')}")

    print(f"\n📋 RESPONSE BODY:")
    print("-" * 70)
    print(response.text)
    print("-" * 70)

    # Try to parse JSON
    try:
        json_data = response.json()
        print(f"\n✅ JSON PARSED SUCCESSFULLY:")
        print(json.dumps(json_data, indent=2))

        # Check for success
        if json_data.get("status"):
            print("\n🎉 ✅ AUTHENTICATION SUCCESSFUL!")
            data = json_data.get("data", {})
            jwt_token = data.get("jwtToken")
            session_token = data.get("sessionToken")
            feed_token = data.get("feedToken")

            print(f"\n🔑 TOKENS RECEIVED:")
            print(f"   JWT Token: {jwt_token[:50]}..." if jwt_token else "   JWT Token: Not received")
            print(f"   Session Token: {session_token[:50]}..." if session_token else "   Session Token: Not received")
            print(f"   Feed Token: {feed_token}" if feed_token else "   Feed Token: Not received")

        else:
            print(f"\n❌ AUTHENTICATION FAILED!")
            print(f"   Status: {json_data.get('status')}")
            print(f"   Message: {json_data.get('message')}")
            print(f"   Error Code: {json_data.get('errorcode')}")

    except json.JSONDecodeError:
        print(f"\n❌ NOT JSON RESPONSE")
        print(f"   Response is: {type(response.text)}")
        if "<html" in response.text.lower():
            print(f"   (HTML error page - credentials likely invalid)")

except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")

print("\n" + "="*70)
