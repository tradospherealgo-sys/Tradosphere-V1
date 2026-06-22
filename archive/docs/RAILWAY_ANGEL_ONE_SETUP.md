# RAILWAY: ANGEL ONE BROKER CONNECTION SETUP

## Current Status

```
✗ Broker Connection: DISCONNECTED
✗ Auth Token: NULL
✗ Price Source: FALLBACK (mock prices)
⚠ Service Status: DEGRADED
```

Evidence:
```bash
curl https://tradosphere-v1-production.up.railway.app/api/health/detailed
# Shows: "broker": {"status": "disconnected", "token": null}
```

---

## Root Cause

Angel One credentials are NOT set as environment variables on Railway production.

Local .env has them:
```
ANGEL_ONE_API_KEY=2G8dEMEq
ANGEL_ONE_CLIENT_CODE=M625536
ANGEL_ONE_PIN=3958
ANGEL_ONE_TOTP_SECRET=W7IMZ4ZLGFWR2SYX4OXFBSU2DM
```

But Railway environment does NOT have them.

---

## How Angel One Authentication Works

```
Railway Server Starts
  ↓
tradosphere_saas_server.py loads
  ↓
init_market_data() function runs
  ↓
Reads environment variables:
  - ANGEL_ONE_API_KEY
  - ANGEL_ONE_CLIENT_CODE
  - ANGEL_ONE_PIN
  - ANGEL_ONE_TOTP_SECRET
  ↓
If any are empty:
  - Sets market = None
  - Broker stays disconnected
  ↓
If all present:
  - AngelOneMarketData class initializes
  - Calls SmartApi.generateSession()
  - Gets JWT token from Angel One
  - Broker marked as "connected"
```

---

## FIX: Set Environment Variables on Railway

### Step 1: Go to Railway Dashboard

https://railway.app → Select "tradosphere-v1" project

### Step 2: Navigate to Variables

Click: "Variables" tab (or "Settings" → "Environment Variables")

### Step 3: Add 4 Variables

Add these EXACTLY as shown:

| Key | Value |
|-----|-------|
| ANGEL_ONE_API_KEY | 2G8dEMEq |
| ANGEL_ONE_CLIENT_CODE | M625536 |
| ANGEL_ONE_PIN | 3958 |
| ANGEL_ONE_TOTP_SECRET | W7IMZ4ZLGFWR2SYX4OXFBSU2DM |

**CRITICAL:** No extra spaces, exact values only.

### Step 4: Save and Redeploy

1. Click "Save" on each variable
2. Go to "Deployments" tab
3. Click "Deploy" or "Redeploy Latest" to restart server with new env vars

**Note:** Redeploy will restart the service. This is required for env vars to take effect.

---

## Verification Steps (After Railway Redeploys)

### Verification 1: Broker Connection Status

```bash
curl https://tradosphere-v1-production.up.railway.app/api/health/detailed
```

Expected response:
```json
{
  "broker": {
    "status": "connected",
    "token": "eyJhbGciOi..."
  },
  "service": {
    "status": "healthy"
  }
}
```

### Verification 2: Signal Generation Uses Live Prices

```bash
curl -X POST https://tradosphere-v1-production.up.railway.app/api/generate \
  -H "Content-Type: application/json" \
  -d '{}'
```

Expected response:
```json
{
  "status": "success",
  "price_source": "live_angel_one",
  "signals": [
    {
      "symbol": "NIFTY",
      "entry": 24159.75,
      "confidence": 72,
      ...
    }
  ]
}
```

**Key check:** `"price_source": "live_angel_one"` (NOT "fallback")

### Verification 3: Current Market Prices

```bash
curl https://tradosphere-v1-production.up.railway.app/api/market/live \
  -H "Authorization: Bearer test_token"
```

Should return current NIFTY/BANKNIFTY/FINNIFTY prices from Angel One.

---

## What Happens When Credentials Are Wrong

If credentials are invalid:
- Angel One auth fails
- `market = None`
- `price_source = "fallback"` returned
- Signals show mock prices: 24047.5, 57489.75, 18950.00

## What Happens When Credentials Are Correct

If credentials are valid:
- Angel One auth succeeds  
- JWT token obtained
- `price_source = "live_angel_one"` returned
- Signals show real prices: 24159.75, 57512.00, 18961.50 (actual market)

---

## If Verification Fails After Setting Variables

### Issue: Still showing "disconnected"

**Check 1:** Did you save the variables?
- Go to Variables tab
- Verify all 4 variables are listed with correct values

**Check 2:** Did you redeploy?
- Go to Deployments tab  
- Click "Deploy Latest" to restart server
- Check deployment log for errors

**Check 3:** Credentials are correct?
- Double-check values match exactly:
  - ANGEL_ONE_API_KEY: 2G8dEMEq
  - ANGEL_ONE_CLIENT_CODE: M625536
  - ANGEL_ONE_PIN: 3958
  - ANGEL_ONE_TOTP_SECRET: W7IMZ4ZLGFWR2SYX4OXFBSU2DM

**Check 4:** Check Railway deployment logs
- Deployments tab → Click latest deployment
- View "Logs" section
- Look for errors about Angel One authentication

---

## Local Testing (Before Deploying to Railway)

To test Angel One integration locally:

```bash
cd /Users/anshhdodia/Desktop/tradosphere_github

# Make sure local .env has credentials
cat .env | grep ANGEL_ONE

# Run signal generation
python3 << 'EOF'
from unified_signal_service import get_unified_signal_service
service = get_unified_signal_service()
signals = service.generate_signals_batch(symbols=['NIFTY', 'BANKNIFTY', 'FINNIFTY'])
print(f"Signals: {len(signals.get('signals', {}))}")
print(f"Price source: {signals.get('price_source')}")
EOF
```

---

## Summary

- Angel One broker needs credentials
- Credentials must be set on Railway dashboard (not local .env)
- After setting, REDEPLOY is required
- Verification checks if broker is connected and prices are live
- Once live, all signals will use real Angel One market data
