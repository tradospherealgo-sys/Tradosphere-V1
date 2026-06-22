#!/usr/bin/env python3
"""
Angel One SmartAPI Official SDK Login Test
Using SmartConnect class from smartapi-python
"""

import os
from SmartApi import SmartConnect
import pyotp
from dotenv import load_dotenv

load_dotenv()

print("\n" + "="*70)
print("🔑 ANGEL ONE SmartAPI SDK LOGIN TEST")
print("="*70)

# Load credentials from .env
api_key = os.getenv("ANGEL_ONE_API_KEY", "")
client_code = os.getenv("ANGEL_ONE_CLIENT_CODE", "")
password = os.getenv("ANGEL_ONE_PIN", "")
totp_secret = os.getenv("ANGEL_ONE_TOTP_SECRET", "")

print("\n✅ CREDENTIALS LOADED FROM .env:")
print(f"   API Key: {api_key}")
print(f"   Client Code: {client_code}")
print(f"   Password: {password}")
print(f"   TOTP Secret: {totp_secret[:8]}...{totp_secret[-4:]}")

# Generate TOTP
print("\n🔐 GENERATING TOTP...")
totp = pyotp.TOTP(totp_secret)
totp_code = totp.now()
print(f"   Generated TOTP: {totp_code}")

# Initialize SmartConnect
print("\n🚀 INITIALIZING SmartConnect...")
try:
    smart = SmartConnect(api_key=api_key)
    print("   ✅ SmartConnect initialized")
except Exception as e:
    print(f"   ❌ Error initializing SmartConnect: {e}")
    exit(1)

# Call generateSession
print("\n📡 CALLING generateSession()...")
print(f"   Parameters:")
print(f"      client_code: {client_code}")
print(f"      password: {password}")
print(f"      totp: {totp_code}")

try:
    response = smart.generateSession(client_code, password, totp_code)

    print(f"\n✅ RESPONSE RECEIVED:")
    print("="*70)
    print(response)
    print("="*70)

    # Parse response
    if isinstance(response, dict):
        print(f"\n📊 RESPONSE ANALYSIS:")

        status = response.get("status")
        message = response.get("message")
        data = response.get("data", {})

        print(f"   Status: {status}")
        print(f"   Message: {message}")

        if status:
            print(f"\n🎉 ✅ AUTHENTICATION SUCCESSFUL!")
            print(f"\n🔑 TOKENS RECEIVED:")

            jwt_token = data.get("jwtToken")
            refresh_token = data.get("refreshToken")
            feed_token = data.get("feedToken")

            if jwt_token:
                print(f"   JWT Token: {jwt_token[:50]}...")
            if refresh_token:
                print(f"   Refresh Token: {refresh_token[:50]}...")
            if feed_token:
                print(f"   Feed Token: {feed_token}")

        else:
            print(f"\n❌ AUTHENTICATION FAILED")
            error_code = response.get("errorcode")
            if error_code:
                print(f"   Error Code: {error_code}")

    else:
        print(f"\n❓ UNEXPECTED RESPONSE TYPE: {type(response)}")

except Exception as e:
    print(f"\n❌ ERROR CALLING generateSession(): {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
