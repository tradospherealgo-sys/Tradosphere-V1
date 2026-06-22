# 🌐 LOCAL TESTING GUIDE - TRADOSPHERE DASHBOARD

**Server Running:** http://localhost:8000  
**Status:** ✅ LIVE & READY  

---

## 📋 ALL DASHBOARDS - TESTING URLS

### 🔓 PUBLIC DASHBOARDS (No Login Required)

#### 1. **Login Page**
```
http://localhost:8000/test/login
```
- Simple login interface
- Use credentials:
  - Email: `testuser@example.com`
  - Password: `TestPass123!`

#### 2. **Demo Dashboard** (No Auth)
```
http://localhost:8000/demo
```
- Unified dashboard
- Shows sample/demo data
- Can browse without login

---

### 🔐 PROTECTED DASHBOARDS (Login Required)

**After logging in, test these:**

#### 3. **Dashboard Live** (Angel One Style)
```
http://localhost:8000/test/dashboard-live
```
- Live market prices (NIFTY, BANKNIFTY)
- 8 tabs with trading interface
- Technical analysis
- Options chain
- AI insights

#### 4. **SAAS Dashboard** (Subscription Focused)
```
http://localhost:8000/test/dashboard-saas
```
- Subscription management
- Billing information
- User account settings
- API keys management
- Analytics

#### 5. **Unified Dashboard**
```
http://localhost:8000/test/dashboard-unified
```
- Consolidated interface
- Multiple sections
- Market overview
- Trading controls

#### 6. **Pro Dashboard**
```
http://localhost:8000/test/dashboard-pro
```
- Premium features
- Advanced analytics
- Pro-only sections

#### 7. **Live Trading Dashboard**
```
http://localhost:8000/test/dashboard-live-trading
```
- Real-time trading interface
- Order entry forms
- Position management
- Price ticker

---

## 🔑 HOW TO LOGIN & GET TOKEN

### Step 1: Go to Login
```
http://localhost:8000/test/login
```

### Step 2: Enter Credentials
```
Email: testuser@example.com
Password: TestPass123!
```

### Step 3: Click Login
- You'll get a JWT token
- Token is saved in localStorage
- You can now access protected dashboards

### Alternative: Get Token via API
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@test.com",
    "password": "TestPass123!",
    "first_name": "Test",
    "last_name": "User"
  }'
```

---

## 🧪 WHAT TO TEST IN EACH DASHBOARD

### Dashboard Live
- [ ] Can see NIFTY prices
- [ ] Can see BANKNIFTY prices
- [ ] Tabs switch correctly
- [ ] Forms load properly
- [ ] Charts display (if any)
- [ ] Options chain shows
- [ ] Trading signals show

### SAAS Dashboard
- [ ] Subscription section loads
- [ ] Plan details display
- [ ] Billing history shows
- [ ] API keys management works
- [ ] Profile section works
- [ ] Account settings load

### Unified Dashboard
- [ ] All sections render
- [ ] Prices update
- [ ] Tables display correctly
- [ ] Forms are functional
- [ ] No console errors

### Pro Dashboard
- [ ] All pro features display
- [ ] Advanced sections work
- [ ] Premium indicators show

### Live Trading Dashboard
- [ ] Order entry form works
- [ ] Price ticker updates
- [ ] Positions display
- [ ] Trade history shows

---

## 📊 API ENDPOINTS TO TEST

### Health & Status (No Auth)
```
GET http://localhost:8000/api/health
GET http://localhost:8000/api/status
GET http://localhost:8000/api/health/detailed
```

### User & Profile (With Token)
```
GET http://localhost:8000/api/auth/me
GET http://localhost:8000/api/user/profile
GET http://localhost:8000/api/user/dashboard-overview
```

### Market Data (With Token)
```
GET http://localhost:8000/api/market/live
GET http://localhost:8000/api/analysis/technical?symbol=NIFTY
GET http://localhost:8000/api/analysis/options?symbol=NIFTY
```

### Trading (With Token)
```
GET http://localhost:8000/api/trading/open-trades
GET http://localhost:8000/api/trading/closed-trades
GET http://localhost:8000/api/trading/stats
POST http://localhost:8000/api/trading/create-trade
```

### Signals (With Token)
```
GET http://localhost:8000/api/signals
POST http://localhost:8000/api/signals/generate
```

---

## 🔍 BROWSER DEVELOPER TOOLS

When testing, open **Developer Tools (F12)** and check:

### Console Tab
- Look for any JavaScript errors
- Check API call logs
- Verify no warnings

### Network Tab
- See all API calls being made
- Check response status (200 = good)
- Verify response data is correct

### Application Tab
- Check localStorage for token
- Verify cookies are set
- Check IndexedDB if used

---

## ⚠️ ISSUES TO CHECK

### If Dashboard is Blank
1. Check browser console (F12)
2. Check Network tab for failed requests
3. Make sure you're logged in
4. Clear browser cache and reload

### If Prices Don't Show
1. Verify API endpoint: `http://localhost:8000/api/market/live`
2. Check if token is valid
3. Ensure Flask server is running
4. Check server logs: `tail -50 /tmp/flask_server.log`

### If Forms Don't Work
1. Open browser console (F12)
2. Check for JavaScript errors
3. Verify API endpoints are responding
4. Check form submission in Network tab

---

## 🚀 TEST CHECKLIST

### Phase 1: Accessibility
- [ ] Can reach http://localhost:8000/test/login
- [ ] Can see login form
- [ ] Can enter credentials
- [ ] Can click login button

### Phase 2: Authentication
- [ ] Login succeeds
- [ ] Redirected to dashboard
- [ ] Token saved in browser
- [ ] Can see "Logout" option

### Phase 3: Dashboard Loading
- [ ] http://localhost:8000/test/dashboard-live loads
- [ ] No console errors
- [ ] All UI elements visible
- [ ] Tabs are clickable

### Phase 4: Data Display
- [ ] Live prices showing (NIFTY, BANKNIFTY)
- [ ] Account balance displays
- [ ] Recent trades list shows
- [ ] No "undefined" values

### Phase 5: API Integration
- [ ] API calls visible in Network tab
- [ ] Responses are JSON with "status": "success"
- [ ] Data updates in real-time
- [ ] Error handling works

### Phase 6: Forms & Interactions
- [ ] Can fill order entry form
- [ ] Can submit forms
- [ ] Get success/error messages
- [ ] Data updates after submission

---

## 📝 REPORTING ISSUES

If you find issues, note:
1. **URL tested:** e.g., `http://localhost:8000/test/dashboard-live`
2. **Expected:** What should happen
3. **Actual:** What actually happened
4. **Console error:** Copy exact error from F12 console
5. **API response:** Check Network tab for error response

---

## 🎯 SUCCESS CRITERIA

**Dashboard is working COMPLETELY when:**
- ✅ Can login
- ✅ Can see all dashboard pages
- ✅ Live prices display
- ✅ Forms submit without errors
- ✅ Data persists
- ✅ No console errors
- ✅ Network tab shows successful API calls

---

## 💡 TIPS

1. **Keep F12 Developer Tools open** - watch Network and Console tabs
2. **Test with multiple browsers** - Chrome, Firefox, Safari
3. **Test on different screen sizes** - Desktop, Tablet, Mobile
4. **Clear cache between tests** - Prevents stale data
5. **Check server logs** - `tail -50 /tmp/flask_server.log`

---

## 📞 TROUBLESHOOTING

**Server not responding?**
```bash
ps aux | grep flask
# If not running, start it:
cd /Users/anshhdodia/Desktop/tradosphere_github
python3 tradosphere_saas_server.py
```

**Getting 404 errors?**
```bash
# Check if file exists:
ls -la /Users/anshhdodia/Desktop/tradosphere_github/*.html
```

**API returning errors?**
```bash
# Test API directly:
curl http://localhost:8000/api/health
curl http://localhost:8000/api/status
```

**Token issues?**
```bash
# Clear browser localStorage:
# Open F12 → Application → Local Storage → delete token
# Then login again
```

---

**Ready to test?** Start with: http://localhost:8000/test/login

Report any issues and we'll fix them before pushing to GitHub! 🚀
