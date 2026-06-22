"""
Test Angel One API Credentials
"""

import requests
import json
import sys

def test_angel_one_credentials(api_key, api_secret, client_code):
    """Test if credentials are valid for Angel One API"""
    
    print("\n" + "="*70)
    print("🔍 ANGEL ONE API CREDENTIAL TESTER")
    print("="*70)
    
    print(f"\n📋 Credentials Entered:")
    print(f"  API Key: {api_key[:10]}***{api_key[-5:]}")
    print(f"  API Secret: {api_secret[:10]}***{api_secret[-5:]}")
    print(f"  Client Code: {client_code}")
    
    # STEP 1: Check credentials not empty
    print(f"\n[1/4] ✓ Validating credentials format...")
    if not api_key or not api_secret or not client_code:
        print("❌ FAIL: Missing required fields")
        return False
    print("✅ PASS: All fields present")
    
    # STEP 2: Try to authenticate
    print(f"\n[2/4] 🔐 Authenticating with Angel One API...")
    try:
        url = "https://smartapi.angelbroking.com/rest/secure/login"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "clientcode": client_code,
            "password": api_secret,
            "totp": "000000"
        }
        
        print(f"   POST {url}")
        print(f"   Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        print(f"\n   Response Status: {response.status_code}")
        print(f"   Response Body: {response.text[:500]}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ PASS: Got response from Angel One")
            
            if data.get("status"):
                jwt_token = data.get("data", {}).get("jwtToken")
                session_token = data.get("data", {}).get("sessionToken")
                print(f"   ✅ JWT Token: {jwt_token[:20]}..." if jwt_token else "   ❌ No JWT Token")
                print(f"   ✅ Session Token: {session_token[:20]}..." if session_token else "   ❌ No Session Token")
                print("\n🟢 SUCCESS: Credentials are VALID!")
                return True
            else:
                error_msg = data.get("message", "Unknown error")
                print(f"\n❌ FAIL: {error_msg}")
                
                # Common issues
                if "totp" in error_msg.lower():
                    print("\n💡 HINT: You might need to enable/update TOTP (2FA) in Angel One settings")
                    print("   Go to: Settings → API Settings → Generate TOTP")
                if "invalid" in error_msg.lower() or "unauthorized" in error_msg.lower():
                    print("\n💡 HINT: Check if credentials are correct")
                    print("   Verify: Dashboard → Settings → API Keys")
                
                return False
        else:
            print(f"\n❌ FAIL: HTTP {response.status_code}")
            print("Common causes:")
            print("  • Invalid API Key")
            print("  • Invalid Client Code")
            print("  • Angel One API server issue")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ FAIL: Connection timeout (Angel One server not responding)")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ FAIL: Connection error: {e}")
        print("   Check your internet connection")
        return False
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        return False

if __name__ == "__main__":
    # Try to load from saved credentials
    try:
        with open("api_credentials.json", "r") as f:
            creds = json.load(f)
            api_key = creds.get("api_key", "")
            api_secret = creds.get("api_secret", "")
            client_code = creds.get("client_code", "")
    except:
        print("❌ No saved credentials found")
        print("\nUsage: python3 test_credentials.py")
        print("Or enter credentials in Dashboard Settings first")
        sys.exit(1)
    
    success = test_angel_one_credentials(api_key, api_secret, client_code)
    
    print("\n" + "="*70)
    if success:
        print("✅ Your credentials are working!")
        print("   Dashboard should now show real prices from Angel One")
    else:
        print("❌ Credentials test failed")
        print("   Check the hints above and try again")
    print("="*70 + "\n")

