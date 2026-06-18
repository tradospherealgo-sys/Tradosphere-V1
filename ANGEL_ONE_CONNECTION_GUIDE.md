# 🚀 CONNECT TRADOSPHERE TO REAL ANGEL ONE API
## Step-by-Step Guide for Live Data, Prices & Graphs

---

## ✅ **STEP 1: Get Your Angel One API Credentials**

### A) Log into Angel One
```
https://smartapi.angelbroking.com/
Username: Your Angel One ID
Password: Your Angel One Password
```

### B) Find Your API Credentials
1. Click **Dashboard** (top left)
2. Go to **Settings** (in sidebar)
3. Look for **API Settings** or **My Profile**
4. You'll see:
   - **API Key** (long string like: `abc123def456ghi789`)
   - **API Secret** (long string like: `xyz789abc123def456`)
   - **Client Code** (short code like: `A972731`)

### C) Copy These Values
```
📋 Write them down:
API Key:      [copy from Angel One]
API Secret:   [copy from Angel One]
Client Code:  [copy from Angel One - you have: A972731]
```

---

## ✅ **STEP 2: Check if 2FA/OTP is Enabled**

### A) In Angel One Settings
1. Look for **Two-Factor Authentication** or **Security Settings**
2. Check if **TOTP/2FA is ENABLED**

### B) Based on Your Setting:

**IF 2FA IS ENABLED:**
- Go to your **authenticator app** (Google Authenticator, Authy, Microsoft Authenticator)
- Find **Angel One** entry
- You'll see a **6-digit code** that changes every 30 seconds
- Example: `428516` → Keep this ready

**IF 2FA IS NOT ENABLED:**
- Leave OTP field **BLANK** in Tradosphere

---

## ✅ **STEP 3: Connect in Tradosphere Dashboard**

### A) Open Tradosphere
```
http://localhost:8000
```

### B) Go to Settings
1. Click **🔧 Settings** in left sidebar
2. You'll see form:
   ```
   🔐 Angel One API Credentials
   
   Connection Status: 🔴 Not Connected
   
   Angel One API Key:     [empty field]
   API Secret:            [empty field]
   Client Code:           [empty field]
   OTP/TOTP Code:         [empty field - if 2FA]
   ```

### C) Fill In Your Credentials

**IMPORTANT: Copy exactly from Angel One (no extra spaces!)**

```
API Key:      [paste your API Key]
API Secret:   [paste your API Secret]
Client Code:  A972731
OTP:          [6-digit code IF 2FA enabled, else leave blank]
```

### D) Click Button
Click: **💾 Connect & Save**

---

## ✅ **STEP 4: Wait for Connection**

You'll see:
```
🔄 Authenticating with Angel One...
```

Then one of:

### **SUCCESS ✅**
```
✅ Connected!
🟢 Connected to Angel One API
```

Dashboard will now show:
- **REAL NIFTY price** (not 0)
- **REAL BANKNIFTY price** (not 0)
- **REAL bid/ask spreads**
- **REAL option chains**
- **REAL candlestick charts**
- **Signals from REAL market data**

### **FAILURE ❌**
```
❌ OTP Invalid or 2FA Issue
or
❌ Invalid Credentials
```

**Solutions:**
- [See Troubleshooting below]

---

## 🔴 **TROUBLESHOOTING: NOT CONNECTING**

### **Problem 1: "Invalid Credentials"**

**Check:**
1. ✅ API Key exactly matches Angel One (copy again!)
2. ✅ API Secret exactly matches Angel One (no spaces!)
3. ✅ Client Code is correct (A972731)
4. ✅ No extra spaces before/after values

**Fix:**
1. Go back to Angel One Dashboard
2. Copy credentials again very carefully
3. Paste in Tradosphere
4. Click "Connect & Save"

---

### **Problem 2: "OTP Invalid"**

**Check:**
1. ✅ 2FA is actually enabled in Angel One account
2. ✅ OTP code is fresh (not expired - it changes every 30 seconds!)
3. ✅ OTP is exactly 6 digits
4. ✅ OTP contains only numbers (0-9)

**Fix:**
1. Open authenticator app (Google Authenticator/Authy)
2. Find Angel One entry
3. Get the FRESH 6-digit code (changes every 30 sec)
4. Enter in OTP field
5. Click "Connect & Save" within 30 seconds

---

### **Problem 3: "Connection failed" (General Error)**

**Possible causes:**
1. Angel One API server is down (rare)
2. API access not enabled in your Angel One account
3. Network issue

**Fix:**
1. Wait 2 minutes
2. Try again
3. If still failing, contact Angel One support

---

## 📊 **ONCE CONNECTED: What You'll See**

### **Dashboard Tab:**
- 📈 REAL NIFTY price (e.g., 23,567.45)
- 📈 REAL BANKNIFTY price (e.g., 54,823.15)
- 📊 REAL bid/ask spreads
- 📊 Performance metrics

### **NIFTY Tab:**
- Current price from Angel One
- Bid/Ask (real spread)
- High/Low for the day
- Candlestick chart (15-min candles)

### **BANKNIFTY Tab:**
- Current price from Angel One
- Live bid/ask
- Chart with real data

### **Options Tab:**
- **REAL option chain** for both indices
- Call/Put OI, LTP, IV
- PCR (Put-Call Ratio) from real data

### **Signals Tab:**
- Trading signals generated from **REAL market data**
- Entry/SL/Target calculated from real prices
- Confidence based on real PCR

---

## ✨ **VERIFICATION CHECKLIST**

After connecting, verify:

- [ ] NIFTY price is NOT 0 (shows real price)
- [ ] BANKNIFTY price is NOT 0 (shows real price)
- [ ] Prices match Angel One app (within seconds)
- [ ] Status shows 🟢 "Connected to Angel One API"
- [ ] Charts have candlesticks (not empty)
- [ ] Options show real OI values
- [ ] Data updates every 10 seconds (refresh page to see)

---

## 🎯 **SUMMARY**

| Step | Action | Result |
|------|--------|--------|
| 1 | Get API credentials from Angel One | 📋 Have 3 values |
| 2 | Check if 2FA enabled, get OTP if yes | 🔐 Know your setup |
| 3 | Enter credentials in Tradosphere Settings | 📝 Form filled |
| 4 | Click "Connect & Save" | ✅ Connected |
| 5 | See real prices & live data | 🎉 SUCCESS |

---

## 🚀 **YOU NOW HAVE:**

✅ **Real NIFTY prices** - live from Angel One  
✅ **Real BANKNIFTY prices** - live from Angel One  
✅ **Real option chains** - with actual OI & PCR  
✅ **Real candlestick charts** - 15-min candles  
✅ **Real trading signals** - from real market data  
✅ **Auto-refresh** - every 10 seconds  
✅ **All 10 dashboard pages** - working with real data

---

**You're connected to real live market data! 🎉**

