#!/usr/bin/env python3
import os
import pyotp
from SmartApi import SmartConnect

# Load from .env file
env_file = '/Users/anshhdodia/Desktop/Tradosphere/.env'
env_vars = {}
with open(env_file) as f:
    for line in f:
        if '=' in line:
            key, value = line.strip().split('=', 1)
            env_vars[key] = value

api_key = env_vars.get("ANGEL_ONE_API_KEY")
client_code = env_vars.get("ANGEL_ONE_CLIENT_CODE")
pin = env_vars.get("ANGEL_ONE_PIN")
totp_secret = env_vars.get("ANGEL_ONE_TOTP_SECRET")

print(f"API Key: {api_key}")
print(f"Client Code: {client_code}")

smart = SmartConnect(api_key=api_key)
totp_code = pyotp.TOTP(totp_secret).now()
response = smart.generateSession(client_code, pin, totp_code)

if response.get("status"):
    print("✅ Authenticated\n")

    # Try ltpData
    print("Testing ltpData method...")
    try:
        result = smart.ltpData("NSE", "NSE", "99926000")
        print(f"  Response type: {type(result)}")
        print(f"  Response: {result}\n")
    except Exception as e:
        print(f"  ❌ Error: {type(e).__name__}: {e}\n")

    # Try getMarketData
    print("Testing getMarketData method...")
    try:
        params = {
            "mode": "LTP",
            "exchangeTokens": "99926000"
        }
        result = smart.getMarketData(params)
        print(f"  Response type: {type(result)}")
        print(f"  Response: {result}\n")
    except Exception as e:
        print(f"  ❌ Error: {type(e).__name__}: {e}\n")
else:
    print("❌ Auth failed")
