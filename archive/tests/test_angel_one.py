"""
ANGEL ONE API TEST
Specific Angel One API connectivity diagnostic
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

print("\n" + "="*80)
print("🔌 ANGEL ONE API CONNECTIVITY TEST")
print("="*80)
print(f"⏱️  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Step 1: Check credentials
print("─"*80)
print("STEP 1: Checking Credentials")
print("─"*80)

api_key = os.getenv("ANGEL_ONE_API_KEY")
api_secret = os.getenv("ANGEL_ONE_API_SECRET")
client_code = os.getenv("ANGEL_ONE_CLIENT_CODE")

print(f"\n  API Key: {api_key if api_key and api_key != 'mock_key' else '❌ Not configured (using mock)'}")
print(f"  API Secret: {'✅ Loaded' if api_secret and api_secret != 'mock_secret' else '❌ Not configured (using mock)'}")
print(f"  Client Code: {client_code if client_code and client_code != 'mock_code' else '❌ Not configured (using mock)'}")

if api_key == "mock_key" or not api_key:
    print("\n⚠️  WARNING: Using mock credentials. To test real Angel One API:")
    print("  1. Get credentials from https://smartapi.angelbroking.com/")
    print("  2. Update .env file with real credentials")
    print("  3. Run this script again")
    print("\nℹ️  Proceeding with mock credentials for demonstration...\n")
    using_mock = True
else:
    using_mock = False
    print("\n✅ Real credentials detected. Attempting actual API connection...\n")

# Step 2: Attempt Authentication
print("─"*80)
print("STEP 2: Angel One Authentication")
print("─"*80)

auth_success = False
jwt_token = None

try:
    print("\n🔐 Sending authentication request to Angel One...")
    print("   Endpoint: https://smartapi.angelbroking.com/rest/secure/login")
    
    auth_payload = {
        "apikey": api_key,
        "password": api_secret,
        "clientcode": client_code,
        "totp": "000000"  # For testing without OTP
    }
    
    print(f"\n   Payload:")
    print(f"     - API Key: {api_key[:20]}..." if len(api_key) > 20 else f"     - API Key: {api_key}")
    print(f"     - Password: {'*' * len(api_secret)}")
    print(f"     - Client Code: {client_code}")
    
    response = requests.post(
        "https://smartapi.angelbroking.com/rest/secure/login",
        json=auth_payload,
        timeout=15
    )
    
    print(f"\n📨 Response Status: {response.status_code}")
    print(f"📨 Response Headers: {dict(response.headers)}")
    
    print(f"\n📝 Full Response:")
    try:
        response_json = response.json()
        print(f"   {json.dumps(response_json, indent=2)}")
        
        if response.status_code == 200:
            if response_json.get("status"):
                jwt_token = response_json.get("data", {}).get("jwtToken")
                if jwt_token:
                    print(f"\n✅ AUTHENTICATION SUCCESSFUL!")
                    print(f"   JWT Token: {jwt_token[:50]}...")
                    print(f"   Token Length: {len(jwt_token)} characters")
                    auth_success = True
                else:
                    print(f"\n❌ Response missing JWT token")
            else:
                print(f"\n❌ Authentication failed: {response_json.get('message', 'Unknown error')}")
        else:
            print(f"\n❌ HTTP Error {response.status_code}")
    
    except json.JSONDecodeError:
        print(f"   {response.text}")
        print(f"\n❌ Could not parse JSON response")
        
except requests.exceptions.Timeout:
    print(f"\n❌ Request timed out. Angel One API may be unreachable.")
except requests.exceptions.ConnectionError:
    print(f"\n❌ Connection error. Could not reach Angel One servers.")
except Exception as e:
    print(f"\n❌ Exception: {str(e)}")

# Step 3: Test Live Price Fetch (if authenticated)
print("\n" + "─"*80)
print("STEP 3: Fetch Live Price (requires authentication)")
print("─"*80)

if auth_success and jwt_token:
    print(f"\n🔑 Using JWT Token for authenticated request...")
    
    try:
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }
        
        # For NIFTY 50 Index (instrument token: 99926000)
        payload = {
            "mode": "LTP",
            "exchangeTokens": {
                "NSE": ["99926000"]  # NIFTY 50 token
            }
        }
        
        print(f"\n   Endpoint: https://smartapi.angelbroking.com/rest/secure/quotes/")
        print(f"   Mode: LTP (Last Traded Price)")
        print(f"   Symbol: NIFTY 50 (Token: 99926000)")
        
        response = requests.post(
            "https://smartapi.angelbroking.com/rest/secure/quotes/",
            headers=headers,
            json=payload,
            timeout=15
        )
        
        print(f"\n📨 Response Status: {response.status_code}")
        
        try:
            data = response.json()
            print(f"\n📝 Price Data Response:")
            print(f"   {json.dumps(data, indent=2)[:500]}...")
            
            if response.status_code == 200 and data.get("status"):
                price_data = data.get("data", {})
                
                if price_data:
                    print(f"\n✅ PRICE DATA RECEIVED!")
                    
                    # Extract price info
                    if "fetched" in price_data:
                        for token, price_info in price_data["fetched"].items():
                            ltp = price_info.get("ltp")
                            bid = price_info.get("bid")
                            ask = price_info.get("ask")
                            
                            print(f"\n   💹 NIFTY 50 Live Prices:")
                            print(f"      LTP (Last Traded Price): {ltp}")
                            print(f"      Bid: {bid}")
                            print(f"      Ask: {ask}")
                            
                            # Validate realistic range
                            if ltp and 23000 <= float(ltp) <= 24000:
                                print(f"      ✅ Price in realistic range (23000-24000)")
                            elif ltp:
                                print(f"      ⚠️  Price outside expected range: {ltp}")
                else:
                    print(f"\n⚠️  No price data in response")
            else:
                print(f"\n❌ API error: {data.get('message', 'Unknown error')}")
        
        except json.JSONDecodeError:
            print(f"   {response.text}")
            print(f"\n❌ Could not parse response")
    
    except Exception as e:
        print(f"\n❌ Exception: {str(e)}")

else:
    print(f"\n⏭️  Skipped (authentication required)")

# Step 4: Test with Market Data Module
print("\n" + "─"*80)
print("STEP 4: Test with Market Data Module")
print("─"*80)

try:
    from market_data import AngelOneMarketData
    
    print(f"\n🔌 Initializing AngelOneMarketData module...")
    
    market = AngelOneMarketData(api_key, api_secret, client_code)
    
    print(f"   ✅ Module initialized")
    
    print(f"\n📊 Fetching NIFTY price...")
    nifty = market.get_live_price("NIFTY")
    
    print(f"\n   📈 NIFTY Data:")
    print(f"      Symbol: {nifty.get('symbol')}")
    print(f"      LTP: {nifty.get('ltp')}")
    print(f"      Bid: {nifty.get('bid')}")
    print(f"      Ask: {nifty.get('ask')}")
    print(f"      High: {nifty.get('high')}")
    print(f"      Low: {nifty.get('low')}")
    print(f"      Volume: {nifty.get('volume')}")
    
    price = nifty.get('ltp')
    if price and 23000 <= price <= 24000:
        print(f"\n   ✅ Real price data from Angel One!")
    elif price and price == 0:
        print(f"\n   ℹ️  Mock data (expected if Angel One API unavailable)")
    else:
        print(f"\n   ℹ️  Mock data returned")

except ImportError:
    print(f"❌ Could not import market_data module")
except Exception as e:
    print(f"❌ Exception: {str(e)}")

# Final Summary
print("\n" + "="*80)
print("📋 FINAL SUMMARY")
print("="*80)

print(f"\n🔍 Connection Status:")
if using_mock:
    print(f"   ⚠️  Using mock credentials - real API not tested")
    print(f"   ℹ️  To enable real Angel One connection:")
    print(f"       1. Create account at https://smartapi.angelbroking.com/")
    print(f"       2. Get API credentials from dashboard")
    print(f"       3. Update .env file with credentials")
    print(f"       4. Run: python3 test_angel_one.py")
else:
    if auth_success:
        print(f"   ✅ Successfully authenticated with Angel One API")
        print(f"   ✅ JWT token obtained")
        if jwt_token:
            print(f"   ✅ Ready to make authenticated requests")
    else:
        print(f"   ❌ Could not authenticate with Angel One API")
        print(f"   💡 Common fixes:")
        print(f"      - Verify credentials in .env file")
        print(f"      - Check that Angel One account is active")
        print(f"      - Ensure internet connection is working")
        print(f"      - Check Angel One API status: https://smartapi.angelbroking.com/")

print("\n" + "="*80)
print(f"✨ Test Complete: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80 + "\n")
