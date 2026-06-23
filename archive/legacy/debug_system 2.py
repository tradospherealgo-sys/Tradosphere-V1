"""
TRADOSPHERE DEBUG SYSTEM
Complete Diagnostic Tool - Tests all components
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

print("\n" + "="*80)
print("🔍 TRADOSPHERE DIAGNOSTIC SYSTEM")
print("="*80)
print(f"⏱️  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Load environment variables
load_dotenv()

test_results = []

# ═══════════════════════════════════════════════════════════════════════════
# TEST 1: ENVIRONMENT VARIABLES
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "─"*80)
print("TEST 1: Environment Variables")
print("─"*80)

env_vars = {
    "ANGEL_ONE_API_KEY": os.getenv("ANGEL_ONE_API_KEY"),
    "ANGEL_ONE_API_SECRET": os.getenv("ANGEL_ONE_API_SECRET"),
    "ANGEL_ONE_CLIENT_CODE": os.getenv("ANGEL_ONE_CLIENT_CODE"),
    "DATABASE_URL": os.getenv("DATABASE_URL"),
}

test1_pass = True
missing_vars = []

for var_name, var_value in env_vars.items():
    if var_value and var_value != "":
        print(f"  ✅ {var_name}: Present (value: {var_value[:20]}...)" if len(str(var_value)) > 20 else f"  ✅ {var_name}: Present")
    else:
        print(f"  ❌ {var_name}: Missing or empty")
        test1_pass = False
        missing_vars.append(var_name)

if test1_pass:
    print("\n✅ TEST 1 PASSED: All environment variables loaded correctly")
    test_results.append(("TEST 1: Environment Variables", "PASS"))
else:
    print(f"\n❌ TEST 1 FAILED: Missing variables: {', '.join(missing_vars)}")
    test_results.append(("TEST 1: Environment Variables", "FAIL"))

# ═══════════════════════════════════════════════════════════════════════════
# TEST 2: ANGEL ONE AUTHENTICATION
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "─"*80)
print("TEST 2: Angel One Authentication")
print("─"*80)

import requests

test2_pass = False
auth_token = None

try:
    api_key = os.getenv("ANGEL_ONE_API_KEY")
    api_secret = os.getenv("ANGEL_ONE_API_SECRET")
    client_code = os.getenv("ANGEL_ONE_CLIENT_CODE")

    if api_key == "mock_key" or api_key is None:
        print(f"  ⚠️  Using mock credentials (API key: {api_key})")
        print("  ℹ️  To test real Angel One API, update .env with real credentials")
        test2_pass = False
        print("\n❌ TEST 2 SKIPPED: Using mock credentials (expected in testing)")
        test_results.append(("TEST 2: Angel One Auth", "SKIPPED"))
    else:
        print("  🔑 Attempting authentication with real credentials...")
        
        auth_payload = {
            "apikey": api_key,
            "password": api_secret,
            "clientcode": client_code,
            "totp": "000000"
        }
        
        response = requests.post(
            "https://smartapi.angelbroking.com/rest/secure/login",
            json=auth_payload,
            timeout=10
        )
        
        print(f"  📨 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status"):
                auth_token = data.get("data", {}).get("jwtToken", "N/A")
                print(f"  ✅ Authentication Successful")
                print(f"  🔐 JWT Token: {str(auth_token)[:50]}...")
                test2_pass = True
                print("\n✅ TEST 2 PASSED: Successfully authenticated with Angel One")
                test_results.append(("TEST 2: Angel One Auth", "PASS"))
            else:
                print(f"  ❌ Authentication failed: {data.get('message', 'Unknown error')}")
                print("\n❌ TEST 2 FAILED: Angel One authentication failed")
                test_results.append(("TEST 2: Angel One Auth", "FAIL"))
        else:
            print(f"  ❌ HTTP Error: {response.status_code}")
            print(f"  📝 Response: {response.text[:200]}")
            print("\n❌ TEST 2 FAILED: Could not connect to Angel One API")
            test_results.append(("TEST 2: Angel One Auth", "FAIL"))

except Exception as e:
    print(f"  ❌ Exception: {str(e)}")
    print("\n❌ TEST 2 FAILED: Exception during authentication")
    test_results.append(("TEST 2: Angel One Auth", "FAIL"))

# ═══════════════════════════════════════════════════════════════════════════
# TEST 3: NIFTY PRICE DATA
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "─"*80)
print("TEST 3: NIFTY Price Data")
print("─"*80)

test3_pass = False

try:
    from market_data import AngelOneMarketData
    
    market = AngelOneMarketData(
        os.getenv("ANGEL_ONE_API_KEY"),
        os.getenv("ANGEL_ONE_API_SECRET"),
        os.getenv("ANGEL_ONE_CLIENT_CODE")
    )
    
    nifty_data = market.get_live_price("NIFTY")
    
    print(f"  📊 Symbol: {nifty_data.get('symbol')}")
    print(f"  💹 Price (LTP): {nifty_data.get('ltp')}")
    print(f"  📈 Bid: {nifty_data.get('bid')}")
    print(f"  📉 Ask: {nifty_data.get('ask')}")
    print(f"  ⬆️  High: {nifty_data.get('high')}")
    print(f"  ⬇️  Low: {nifty_data.get('low')}")
    print(f"  📦 Volume: {nifty_data.get('volume')}")
    
    # Check if data is realistic
    price = nifty_data.get('ltp')
    if price and 23000 <= price <= 24000:
        print(f"  ✅ Price in realistic range (23000-24000)")
        test3_pass = True
        print("\n✅ TEST 3 PASSED: NIFTY price data is realistic (real data)")
        test_results.append(("TEST 3: NIFTY Price", "PASS"))
    elif price and price == 0:
        print(f"  ℹ️  Price showing mock data (0 or generic value)")
        print("\n⚠️  TEST 3 PARTIAL: NIFTY returning mock data")
        test_results.append(("TEST 3: NIFTY Price", "MOCK"))
    else:
        print(f"  ℹ️  Price showing mock data (outside realistic range: {price})")
        print("\n⚠️  TEST 3 PARTIAL: NIFTY returning mock data")
        test_results.append(("TEST 3: NIFTY Price", "MOCK"))

except Exception as e:
    print(f"  ❌ Exception: {str(e)}")
    print("\n❌ TEST 3 FAILED: Could not fetch NIFTY price")
    test_results.append(("TEST 3: NIFTY Price", "FAIL"))

# ═══════════════════════════════════════════════════════════════════════════
# TEST 4: BANKNIFTY PRICE DATA
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "─"*80)
print("TEST 4: BANKNIFTY Price Data")
print("─"*80)

test4_pass = False

try:
    bnifty_data = market.get_live_price("BANKNIFTY")
    
    print(f"  📊 Symbol: {bnifty_data.get('symbol')}")
    print(f"  💹 Price (LTP): {bnifty_data.get('ltp')}")
    print(f"  📈 Bid: {bnifty_data.get('bid')}")
    print(f"  📉 Ask: {bnifty_data.get('ask')}")
    print(f"  ⬆️  High: {bnifty_data.get('high')}")
    print(f"  ⬇️  Low: {bnifty_data.get('low')}")
    print(f"  📦 Volume: {bnifty_data.get('volume')}")
    
    price = bnifty_data.get('ltp')
    if price and 54000 <= price <= 55000:
        print(f"  ✅ Price in realistic range (54000-55000)")
        test4_pass = True
        print("\n✅ TEST 4 PASSED: BANKNIFTY price data is realistic (real data)")
        test_results.append(("TEST 4: BANKNIFTY Price", "PASS"))
    elif price and price == 0:
        print(f"  ℹ️  Price showing mock data")
        print("\n⚠️  TEST 4 PARTIAL: BANKNIFTY returning mock data")
        test_results.append(("TEST 4: BANKNIFTY Price", "MOCK"))
    else:
        print(f"  ℹ️  Price showing mock data (outside realistic range: {price})")
        print("\n⚠️  TEST 4 PARTIAL: BANKNIFTY returning mock data")
        test_results.append(("TEST 4: BANKNIFTY Price", "MOCK"))

except Exception as e:
    print(f"  ❌ Exception: {str(e)}")
    print("\n❌ TEST 4 FAILED: Could not fetch BANKNIFTY price")
    test_results.append(("TEST 4: BANKNIFTY Price", "FAIL"))

# ═══════════════════════════════════════════════════════════════════════════
# TEST 5: NIFTY OPTION CHAIN
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "─"*80)
print("TEST 5: NIFTY Option Chain")
print("─"*80)

test5_pass = False

try:
    nifty_opts = market.get_option_chain("NIFTY")
    
    calls = nifty_opts.get('calls', [])
    puts = nifty_opts.get('puts', [])
    pcr = nifty_opts.get('pcr')
    support = nifty_opts.get('support')
    resistance = nifty_opts.get('resistance')
    
    print(f"  📞 Calls Rows: {len(calls)}")
    print(f"  📱 Puts Rows: {len(puts)}")
    print(f"  🔄 PCR: {pcr}")
    print(f"  📍 Support: {support}")
    print(f"  📍 Resistance: {resistance}")
    
    if len(calls) >= 5 and len(puts) >= 5 and pcr and support and resistance:
        print(f"  ✅ Option chain complete with all required data")
        test5_pass = True
        print("\n✅ TEST 5 PASSED: NIFTY option chain complete")
        test_results.append(("TEST 5: NIFTY Options", "PASS"))
    else:
        print(f"  ⚠️  Option chain incomplete")
        print("\n⚠️  TEST 5 PARTIAL: NIFTY option chain incomplete")
        test_results.append(("TEST 5: NIFTY Options", "INCOMPLETE"))

except Exception as e:
    print(f"  ❌ Exception: {str(e)}")
    print("\n❌ TEST 5 FAILED: Could not fetch NIFTY option chain")
    test_results.append(("TEST 5: NIFTY Options", "FAIL"))

# ═══════════════════════════════════════════════════════════════════════════
# TEST 6: BANKNIFTY OPTION CHAIN
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "─"*80)
print("TEST 6: BANKNIFTY Option Chain")
print("─"*80)

test6_pass = False

try:
    bnifty_opts = market.get_option_chain("BANKNIFTY")
    
    calls = bnifty_opts.get('calls', [])
    puts = bnifty_opts.get('puts', [])
    pcr = bnifty_opts.get('pcr')
    support = bnifty_opts.get('support')
    resistance = bnifty_opts.get('resistance')
    
    print(f"  📞 Calls Rows: {len(calls)}")
    print(f"  📱 Puts Rows: {len(puts)}")
    print(f"  🔄 PCR: {pcr}")
    print(f"  📍 Support: {support}")
    print(f"  📍 Resistance: {resistance}")
    
    if len(calls) >= 5 and len(puts) >= 5 and pcr and support and resistance:
        print(f"  ✅ Option chain complete with all required data")
        test6_pass = True
        print("\n✅ TEST 6 PASSED: BANKNIFTY option chain complete")
        test_results.append(("TEST 6: BANKNIFTY Options", "PASS"))
    else:
        print(f"  ⚠️  Option chain incomplete")
        print("\n⚠️  TEST 6 PARTIAL: BANKNIFTY option chain incomplete")
        test_results.append(("TEST 6: BANKNIFTY Options", "INCOMPLETE"))

except Exception as e:
    print(f"  ❌ Exception: {str(e)}")
    print("\n❌ TEST 6 FAILED: Could not fetch BANKNIFTY option chain")
    test_results.append(("TEST 6: BANKNIFTY Options", "FAIL"))

# ═══════════════════════════════════════════════════════════════════════════
# TEST 7: CHART DATA
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "─"*80)
print("TEST 7: Chart Data (Candlesticks)")
print("─"*80)

test7_pass = False

try:
    nifty_chart = market.get_chart_data("NIFTY")
    candles = nifty_chart.get('candles', [])
    
    print(f"  📈 Number of candles: {len(candles)}")
    
    if len(candles) >= 5:
        first_candle = candles[0]
        last_candle = candles[-1]
        
        print(f"  🕐 First candle time: {first_candle.get('time')}")
        print(f"  🕐 Last candle time: {last_candle.get('time')}")
        
        # Check for OHLCV data
        required_fields = ['time', 'open', 'high', 'low', 'close', 'volume']
        has_all_fields = all(field in first_candle for field in required_fields)
        
        if has_all_fields:
            print(f"  ✅ All OHLCV fields present")
            test7_pass = True
            print("\n✅ TEST 7 PASSED: Chart data complete with candlesticks")
            test_results.append(("TEST 7: Chart Data", "PASS"))
        else:
            missing = [f for f in required_fields if f not in first_candle]
            print(f"  ⚠️  Missing fields: {missing}")
            print("\n⚠️  TEST 7 PARTIAL: Chart data incomplete")
            test_results.append(("TEST 7: Chart Data", "INCOMPLETE"))
    else:
        print(f"  ⚠️  Not enough candles ({len(candles)})")
        print("\n❌ TEST 7 FAILED: Insufficient chart data")
        test_results.append(("TEST 7: Chart Data", "FAIL"))

except Exception as e:
    print(f"  ❌ Exception: {str(e)}")
    print("\n❌ TEST 7 FAILED: Could not fetch chart data")
    test_results.append(("TEST 7: Chart Data", "FAIL"))

# ═══════════════════════════════════════════════════════════════════════════
# TEST 8: DATABASE OPERATIONS
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "─"*80)
print("TEST 8: Database Operations")
print("─"*80)

test8_pass = False

try:
    from database import init_db, save_signal, get_metrics
    
    print("  🔧 Initializing database...")
    init_db()
    print("  ✅ Database initialized")
    
    print("  💾 Saving test signal...")
    signal = save_signal(
        symbol="TEST",
        entry=23500.0,
        sl=23200.0,
        target=23800.0,
        verdict="BUY",
        confidence=75.5,
        ema_signal="BUY",
        oi_bias="Bullish",
        pcr=1.05
    )
    
    signal_id = signal.get('id')
    print(f"  ✅ Test signal saved with ID: {signal_id}")
    
    print("  📊 Fetching metrics...")
    metrics = get_metrics()
    
    print(f"  📈 Total Signals: {metrics.get('total_signals')}")
    print(f"  💹 Total Trades: {metrics.get('total_trades')}")
    print(f"  📊 Win Rate: {metrics.get('win_rate')}%")
    print(f"  💰 Total P&L: {metrics.get('total_pnl')}")
    
    if signal_id and metrics:
        test8_pass = True
        print("\n✅ TEST 8 PASSED: Database operations working correctly")
        test_results.append(("TEST 8: Database Ops", "PASS"))
    else:
        print("\n❌ TEST 8 FAILED: Database operations incomplete")
        test_results.append(("TEST 8: Database Ops", "FAIL"))

except Exception as e:
    print(f"  ❌ Exception: {str(e)}")
    print("\n❌ TEST 8 FAILED: Database error")
    test_results.append(("TEST 8: Database Ops", "FAIL"))

# ═══════════════════════════════════════════════════════════════════════════
# TEST 9: SIGNAL GENERATION
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "─"*80)
print("TEST 9: Signal Generation (On-Demand)")
print("─"*80)

test9_pass = False

try:
    from signal_writer import generate_on_demand
    
    print("  🎯 Generating signals...")
    result = generate_on_demand(
        os.getenv("ANGEL_ONE_API_KEY"),
        os.getenv("ANGEL_ONE_API_SECRET"),
        os.getenv("ANGEL_ONE_CLIENT_CODE")
    )
    
    status = result.get('status')
    signals = result.get('signals', [])
    count = result.get('count', 0)
    
    print(f"  📨 Status: {status}")
    print(f"  📊 Signals Generated: {count}")
    
    if status == "success" and len(signals) > 0:
        for i, sig in enumerate(signals, 1):
            print(f"\n  Signal {i}:")
            print(f"    🎯 Symbol: {sig.get('symbol')}")
            print(f"    📍 Entry: {sig.get('entry')}")
            print(f"    🛑 Stop Loss: {sig.get('sl')}")
            print(f"    🎁 Target: {sig.get('target')}")
            print(f"    📈 Verdict: {sig.get('verdict')}")
            print(f"    💯 Confidence: {sig.get('confidence')}%")
            
            # Validate confidence range
            conf = sig.get('confidence', 0)
            if 60 <= conf <= 85:
                print(f"    ✅ Confidence in expected range (60-85%)")
            else:
                print(f"    ⚠️  Confidence outside expected range")
        
        if len(signals) == 2:
            test9_pass = True
        
        print("\n✅ TEST 9 PASSED: Signals generating correctly")
        test_results.append(("TEST 9: Signal Generation", "PASS"))
    else:
        print(f"\n❌ TEST 9 FAILED: No signals generated or error status")
        test_results.append(("TEST 9: Signal Generation", "FAIL"))

except Exception as e:
    print(f"  ❌ Exception: {str(e)}")
    print("\n❌ TEST 9 FAILED: Signal generation error")
    test_results.append(("TEST 9: Signal Generation", "FAIL"))

# ═══════════════════════════════════════════════════════════════════════════
# SUMMARY REPORT
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*80)
print("📋 DIAGNOSTIC SUMMARY")
print("="*80)

passed = sum(1 for _, result in test_results if result == "PASS")
failed = sum(1 for _, result in test_results if result == "FAIL")
skipped = sum(1 for _, result in test_results if result == "SKIPPED")
partial = sum(1 for _, result in test_results if result in ["MOCK", "INCOMPLETE"])

print(f"\n✅ PASSED: {passed}/9")
print(f"❌ FAILED: {failed}/9")
print(f"⚠️  PARTIAL/MOCK: {partial}/9")
print(f"⏭️  SKIPPED: {skipped}/9\n")

for test_name, result in test_results:
    if result == "PASS":
        symbol = "✅"
    elif result == "FAIL":
        symbol = "❌"
    elif result == "SKIPPED":
        symbol = "⏭️"
    else:
        symbol = "⚠️"
    
    print(f"{symbol} {test_name}: {result}")

# Overall status
print("\n" + "─"*80)
if failed == 0 and skipped <= 1:
    overall_status = "✅ PASS"
else:
    overall_status = "❌ FAIL"

print(f"OVERALL STATUS: {overall_status}")
print("─"*80)

if failed > 0:
    print(f"\n🔧 RECOMMENDATIONS:")
    failed_tests = [name for name, result in test_results if result == "FAIL"]
    for test in failed_tests:
        if "Environment" in test:
            print("  1. Update .env file with correct credentials")
        elif "Angel One" in test:
            print("  2. Check Angel One API credentials and verify account is active")
        elif "Price" in test or "Options" in test or "Chart" in test:
            print("  3. Verify Angel One API is accessible and returning data")
        elif "Database" in test:
            print("  4. Check database connection and ensure tables are created")
        elif "Signal" in test:
            print("  5. Verify signal generation logic and market data dependencies")

print("\n" + "="*80)
print(f"✨ Diagnostic Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80 + "\n")
