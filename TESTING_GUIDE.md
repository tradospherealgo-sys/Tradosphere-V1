# 🧪 TRADOSPHERE - COMPLETE TESTING GUIDE

## ✅ SERVER STATUS
- **Status**: RUNNING ✅
- **Port**: 8000
- **Databases**: Freshly initialized (clean slate)
- **Health**: http://localhost:8000/api/health

---

## 📋 TEST WORKFLOW

### STEP 1: CREATE TEST ACCOUNT
1. Go to: **http://localhost:8000/login**
2. Click "Sign Up"
3. Fill in:
   - **Email**: testuser@example.com
   - **Password**: testpass123
   - **First Name**: Test
   - **Last Name**: User
   - **Company**: My Trading Co
4. Click "Create Account"
5. You'll get a JWT token - **save this for API testing**

---

### STEP 2: ACCESS MAIN DASHBOARD
1. After login, go to: **http://localhost:8000/dashboard**
2. You should see:

#### **📊 Overview Section**
- Live NIFTY price
- Live BANKNIFTY price
- Auto-refreshes every 30 seconds
- Real data from Angel One API

#### **📈 Technical Analysis Section**
- RSI (Relative Strength Index)
- EMA 9/50 (Crossover status)
- MACD (with histogram)
- Bollinger Bands (position)
- VWAP (Volume-weighted average)
- Trend (Bullish/Bearish)

#### **📊 Options Analysis Section**
- PCR Ratio (Put-Call Ratio)
- OI Skew (Call/Put distribution)
- Support Level
- Resistance Level
- Max Pain

#### **🎯 My Signals Section**
- Click "🔄 Generate New Signal"
- See AI-generated trading signal with:
  - Symbol (NIFTY/BANKNIFTY)
  - Direction (BUY/SELL)
  - Entry Price
  - Target Price
  - Stop Loss
  - Quality Score (0-100)

---

### STEP 3: TEST PAPER TRADING
1. On dashboard, click **"🚀 Live Paper Trading"** button
2. You'll be taken to trading dashboard

#### **Create Account**
- Click "Create Account" button
- Select symbol: NIFTY or BANKNIFTY
- Initial capital: ₹100,000
- Click "Create"

#### **Execute a Trade**
- Click "Quick Trade"
- Fill in:
  - **Entry Price**: Current NIFTY price (or any price)
  - **Quantity**: 1
  - **Stop Loss**: Entry - 200
  - **Target**: Entry + 500
- Click "OPEN BUY TRADE"

#### **View Account Stats**
- See real-time balance
- Track P&L as price moves
- View win/loss record
- Check account statistics

#### **Close a Trade**
- From open trades list
- Click "Close" button
- Trade closes at current market price
- P&L calculated automatically

---

### STEP 4: TEST BACKTESTING (API)

#### **Get Available Strategies**
```bash
curl -X GET http://localhost:8000/api/backtest/strategies \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Expected response:
```json
{
  "strategies": [
    {
      "id": "technical",
      "name": "Technical-Based Strategy",
      "description": "Uses RSI < 30 for buy and EMA crossover signals",
      "indicators": ["RSI", "EMA 9", "EMA 50"]
    },
    {
      "id": "momentum",
      "name": "Momentum-Based Strategy",
      "description": "Uses RSI oversold/overbought levels",
      "indicators": ["RSI"]
    }
  ]
}
```

#### **Run a Backtest**
```bash
curl -X POST http://localhost:8000/api/backtest/run \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "NIFTY",
    "strategy": "technical",
    "days_back": 7,
    "initial_capital": 100000
  }'
```

#### **Compare All Strategies**
```bash
curl -X POST http://localhost:8000/api/backtest/compare \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "NIFTY",
    "days_back": 7,
    "initial_capital": 100000
  }'
```

---

## 🔍 VERIFICATION CHECKLIST

### Phase 1: Technical Indicators
- [ ] RSI displayed on dashboard (0-100 range)
- [ ] EMA 9/50 showing relationship (above/below/equal)
- [ ] MACD displaying histogram
- [ ] Bollinger Bands position shown
- [ ] VWAP value visible
- [ ] Trend indicator shows Bullish/Bearish

### Phase 2: Live Dashboard
- [ ] Overview section loads without errors
- [ ] Live prices update (NIFTY & BANKNIFTY)
- [ ] Technical Analysis section displays all indicators
- [ ] Options Analysis shows PCR and OI Skew
- [ ] Signals section loads
- [ ] Page navigation works smoothly (no glitching)
- [ ] All sections switch without lag

### Phase 3: Paper Trading
- [ ] Can create account for NIFTY
- [ ] Can create account for BANKNIFTY
- [ ] Initial balance shows ₹100,000
- [ ] Can open BUY trade
- [ ] Can open SELL trade
- [ ] P&L updates as price changes
- [ ] Can close trades
- [ ] Account statistics tracked:
  - [ ] Total trades count
  - [ ] Win rate percentage
  - [ ] Total P&L
  - [ ] Average win/loss

### Phase 4: Backtesting
- [ ] Can list strategies (shows 2 strategies)
- [ ] Technical strategy description displays
- [ ] Momentum strategy description displays
- [ ] Can get strategy indicators list
- [ ] Backtesting engine recognizes parameters

---

## 🎯 TESTING SCENARIOS

### Scenario 1: Fresh Login Flow
1. Clear browser cookies
2. Go to login page
3. Sign up with new email
4. Verify account created
5. Login with credentials
6. Access dashboard

### Scenario 2: Technical Analysis
1. Go to dashboard
2. Click Technical section
3. Wait for data to load
4. Verify all 6 indicators show values
5. Check if values are realistic (RSI 0-100, etc.)

### Scenario 3: Paper Trading Flow
1. Create NIFTY account
2. Open BUY trade at ₹24,000
3. Note current balance decrease
4. Check P&L as market moves
5. Open SELL trade at higher price
6. Close SELL trade
7. Verify profit added to balance

### Scenario 4: Multiple Accounts
1. Create NIFTY account with ₹100,000
2. Execute 3-5 trades
3. Create BANKNIFTY account
4. Execute trades in BANKNIFTY
5. Verify accounts are separate
6. Check stats for each account

---

## 📊 EXPECTED DATA RANGES

**Live Prices**:
- NIFTY: 20,000 - 28,000 (typically)
- BANKNIFTY: 40,000 - 60,000 (typically)

**RSI**:
- 0-30: Oversold (Buy signal)
- 30-70: Normal range
- 70-100: Overbought (Sell signal)

**MACD**:
- Positive histogram: Bullish
- Negative histogram: Bearish
- Crossover: Signal change

**Bollinger Bands**:
- Price above upper band: Overbought
- Price below lower band: Oversold
- Within bands: Normal

---

## 🐛 TROUBLESHOOTING

### Issue: Dashboard doesn't load
**Solution**: Check browser console for errors, refresh page, verify token is valid

### Issue: Live prices not updating
**Solution**: Check if Angel One API credentials are configured, verify broker connection

### Issue: Paper trading account fails
**Solution**: Ensure you're logged in, check API response for errors

### Issue: Backtesting returns no data
**Solution**: This is expected - needs historical candle data in database

### Issue: Port 8000 already in use
**Solution**: Run `lsof -i :8000` and kill the process: `kill -9 <PID>`

---

## ✅ SUCCESS CRITERIA

The system is working correctly when:
- ✅ Login and signup work
- ✅ Dashboard loads all sections
- ✅ Live prices update in real-time
- ✅ All 6 technical indicators display
- ✅ Paper trading creates accounts
- ✅ Trades execute with P&L calculation
- ✅ Account statistics update
- ✅ No JavaScript errors in console
- ✅ No database errors in server logs
- ✅ All pages are responsive

---

## 📞 NEED HELP?

Check server logs:
```bash
tail -100 /tmp/server_fresh.log
```

Test a specific API:
```bash
curl http://localhost:8000/api/health | jq .
```

Verify database:
```bash
ls -lh *.db
```

---

**Ready to test? Start at: http://localhost:8000/login**
