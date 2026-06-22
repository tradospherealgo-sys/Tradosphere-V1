#!/usr/bin/env python3
"""
Test script for /api/generate Signal Generation Endpoint
Tests the endpoint locally or on production Railway deployment
"""

import requests
import json
import sys
import time
from datetime import datetime

def test_endpoint(base_url):
    """Test the signal generation endpoint"""

    print("\n" + "="*70)
    print("SIGNAL GENERATION ENDPOINT TEST")
    print("="*70)
    print(f"Testing endpoint: {base_url}/api/generate\n")

    # Test 1: Generate signals
    print("TEST 1: Generate signals for all symbols")
    print("-" * 70)

    try:
        start_time = time.time()

        response = requests.post(
            f"{base_url}/api/generate",
            json={"symbols": ["NIFTY", "BANKNIFTY", "FINNIFTY"]},
            headers={"Content-Type": "application/json"},
            timeout=5
        )

        elapsed = time.time() - start_time

        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {elapsed*1000:.0f}ms")

        if response.status_code == 200:
            data = response.json()

            print(f"\n✅ Response Status: {data.get('status')}")
            print(f"Message: {data.get('message')}")
            print(f"Timestamp: {data.get('timestamp')}")

            if data.get('signals'):
                print(f"\nSignals Generated: {len(data['signals'])}")
                print("-" * 70)

                for i, signal in enumerate(data['signals'], 1):
                    print(f"\nSignal #{i}: {signal.get('symbol')}")
                    print(f"  Direction: {signal.get('direction')}")
                    print(f"  Entry: ₹{signal.get('entry', 0):.2f}")
                    print(f"  Target: ₹{signal.get('target', 0):.2f}")
                    print(f"  Stop Loss: ₹{signal.get('stoploss', 0):.2f}")
                    print(f"  Confidence: {signal.get('confidence')}%")
                    print(f"  Risk/Reward: {signal.get('risk_reward', 0):.2f}")
                    print(f"  Reason: {signal.get('reason')}")

                print(f"\n✅ TEST 1 PASSED: Signals generated successfully\n")
                return True
            else:
                print("❌ TEST 1 FAILED: No signals in response\n")
                return False
        else:
            print(f"❌ TEST 1 FAILED: HTTP {response.status_code}")
            print(f"Response: {response.text}\n")
            return False

    except requests.exceptions.Timeout:
        print("❌ TEST 1 FAILED: Request timeout (> 5 seconds)\n")
        return False
    except requests.exceptions.ConnectionError:
        print(f"❌ TEST 1 FAILED: Could not connect to {base_url}")
        print("Make sure the backend is running.\n")
        return False
    except Exception as e:
        print(f"❌ TEST 1 FAILED: {str(e)}\n")
        return False


def test_response_format(base_url):
    """Validate response format"""

    print("TEST 2: Validate response format")
    print("-" * 70)

    try:
        response = requests.post(
            f"{base_url}/api/generate",
            json={},
            timeout=5
        )

        if response.status_code != 200:
            print(f"❌ TEST 2 FAILED: Unexpected status code {response.status_code}\n")
            return False

        data = response.json()

        # Check top-level fields
        required_fields = ["status", "message", "signals", "timestamp"]
        missing_fields = []

        for field in required_fields:
            if field not in data:
                missing_fields.append(field)

        if missing_fields:
            print(f"❌ Missing fields: {', '.join(missing_fields)}\n")
            return False

        print("✅ Response structure:")
        print(f"  - status: {data['status']}")
        print(f"  - message: {data['message']}")
        print(f"  - signals: {len(data['signals'])} signals")
        print(f"  - timestamp: {data['timestamp']}")

        # Check signal format
        if data['signals']:
            signal = data['signals'][0]
            signal_fields = ["symbol", "direction", "entry", "target", "stoploss", "confidence", "reason"]

            missing_signal_fields = []
            for field in signal_fields:
                if field not in signal:
                    missing_signal_fields.append(field)

            if missing_signal_fields:
                print(f"\n❌ Missing signal fields: {', '.join(missing_signal_fields)}\n")
                return False

            print("\n✅ Signal structure:")
            print(f"  - symbol: {signal['symbol']}")
            print(f"  - direction: {signal['direction']}")
            print(f"  - entry: {signal['entry']}")
            print(f"  - target: {signal['target']}")
            print(f"  - stoploss: {signal['stoploss']}")
            print(f"  - confidence: {signal['confidence']}")
            print(f"  - reason: {signal['reason']}")

        print(f"\n✅ TEST 2 PASSED: Response format is valid\n")
        return True

    except Exception as e:
        print(f"❌ TEST 2 FAILED: {str(e)}\n")
        return False


def test_performance(base_url):
    """Test response time performance"""

    print("TEST 3: Performance test")
    print("-" * 70)

    try:
        times = []

        for i in range(3):
            start = time.time()
            response = requests.post(
                f"{base_url}/api/generate",
                json={},
                timeout=5
            )
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)
            print(f"  Request {i+1}: {elapsed:.0f}ms")

        avg_time = sum(times) / len(times)
        print(f"\n  Average time: {avg_time:.0f}ms")

        if avg_time < 2000:  # Less than 2 seconds
            print(f"✅ TEST 3 PASSED: Response time excellent ({avg_time:.0f}ms)\n")
            return True
        elif avg_time < 5000:  # Less than 5 seconds
            print(f"⚠️  TEST 3 PASSED: Response time acceptable ({avg_time:.0f}ms)\n")
            return True
        else:
            print(f"❌ TEST 3 FAILED: Response time too slow ({avg_time:.0f}ms)\n")
            return False

    except Exception as e:
        print(f"❌ TEST 3 FAILED: {str(e)}\n")
        return False


def main():
    """Run all tests"""

    # Determine which endpoint to test
    if len(sys.argv) > 1 and sys.argv[1] == "production":
        base_url = "https://tradosphere-backend.railway.app"
        print("\n🌐 Testing PRODUCTION environment")
    else:
        base_url = "http://localhost:8000"
        print("\n🏠 Testing LOCAL environment")

    print(f"Base URL: {base_url}")

    # Run tests
    results = []
    results.append(("Signal Generation", test_endpoint(base_url)))
    results.append(("Response Format", test_response_format(base_url)))
    results.append(("Performance", test_performance(base_url)))

    # Summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")

    all_passed = all(result[1] for result in results)

    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("\n✅ The /api/generate endpoint is working correctly")
        print("✅ Dashboard can now generate signals without authentication")
        print("✅ Endpoint is ready for production use")
    else:
        print("❌ SOME TESTS FAILED")
        print("\nPlease check:")
        print("  1. Backend is running and accessible")
        print("  2. Correct base URL is being used")
        print("  3. Network connectivity is working")

    print("=" * 70 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
