# 🚀 TRADOSPHERE - Real Angel One API Integration Guide

## What Changed?

**OLD**: Dashboard had fake mock data with random prices  
**NEW**: Dashboard connects to YOUR Angel One account and shows REAL live prices

---

## ✅ Step 1: Get Your Angel One API Credentials

1. Go to: **https://smartapi.angelbroking.com/**
2. Login with your trading account
3. Go to: **Dashboard → My Profile → API Keys**
4. You'll find:
   - **API Key** (e.g., `abc123def456`)
   - **API Secret** (e.g., `xyz789abc123`)
   - **Client Code** (e.g., `A123456`)

📝 **Keep these 3 values ready**

---

## ✅ Step 2: Open Dashboard Settings

1. Open **http://localhost:8000** in your browser
2. Click **⚙️ Settings** in the left sidebar
3. Scroll to **"🔐 Angel One API Credentials"** section

---

## ✅ Step 3: Enter Your Credentials

1. **Angel One API Key** field → Paste your API Key
2. **API Secret** field → Paste your API Secret  
3. **Client Code** field → Paste your Client Code
4. Click **"💾 Connect & Save"** button

---

## ✅ Step 4: Wait for Authentication

The dashboard will:
- 🔄 Connect to Angel One API
- 🟢 Turn green when authenticated
- 📊 Show REAL prices, charts, and option chains
- 🎯 Generate signals from REAL market data

---

## 🎯 What You'll See

Once connected:

✅ **NIFTY & BANKNIFTY** tabs show REAL current prices  
✅ **Charts** display REAL candlestick data  
✅ **Options Chain** shows REAL PCR analysis  
✅ **Signals** generated from REAL market sentiment  
✅ **All data** updates every 10 seconds from Angel One  

---

## ❓ Troubleshooting

### "Not Connected" status?
- Check if your API credentials are correct
- Verify you're using the CURRENT Angel One API key (not old/revoked ones)
- Some broker accounts need TOTP (two-factor) enabled for API access

### Prices still don't match Angel One app?
- Refresh the dashboard (F5)
- Wait 10 seconds for next data update
- Check System Info section shows "Connected"

### Getting HTTP 401/403 errors?
- Your credentials might be invalid
- Try regenerating API key from Angel One dashboard
- Copy-paste carefully (no extra spaces)

---

## 🔐 Security Notes

- ✅ Credentials are stored LOCALLY on your server only
- ✅ Never shared with external services
- ✅ Credentials file: `api_credentials.json` (not in version control)
- ✅ Use .gitignore to prevent accidental upload

---

## 📱 For Multiple Users

Each user can:
1. Open dashboard
2. Go to Settings
3. Enter THEIR OWN Angel One credentials
4. See THEIR OWN account's prices and signals

Multiple users can use the same Tradosphere instance with different credentials!

---

## 🎯 Next Steps

1. ✅ Enter credentials in Settings
2. ✅ Wait for "Connected" status
3. ✅ See real NIFTY/BANKNIFTY prices
4. ✅ View real option chains with PCR
5. ✅ Generate signals from real data
6. ✅ Deploy to Railway.app when ready

---

## 💬 Support

If prices still don't match:
- Check Angel One app side-by-side with Tradosphere
- Verify same index (NIFTY vs BANKNIFTY)
- Wait for 10-second refresh cycle
- Check browser console (F12) for errors

**The system is designed to show EXACTLY the same prices as Angel One!**

