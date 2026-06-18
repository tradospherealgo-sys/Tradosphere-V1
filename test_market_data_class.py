#!/usr/bin/env python3
from market_data import AngelOneMarketData

print("Testing AngelOneMarketData class...\n")

try:
    market = AngelOneMarketData()

    print("✅ Market data initialized\n")

    print("Testing get_nifty_price()...")
    nifty = market.get_nifty_price()
    print(f"  Result: {nifty}\n")

    print("Testing get_banknifty_price()...")
    banknifty = market.get_banknifty_price()
    print(f"  Result: {banknifty}\n")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
