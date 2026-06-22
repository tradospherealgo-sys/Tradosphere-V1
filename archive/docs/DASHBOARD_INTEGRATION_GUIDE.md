# 📊 Dashboard Integration Guide

**How to connect your existing dashboards to the Tradosphere API backend**

---

## 🚀 Quick Start

### Step 1: Add Scripts to Your Dashboard HTML

Add these two lines in the `<head>` section of your HTML file (before your other scripts):

```html
<script src="api_client.js"></script>
<script src="dashboard_utils.js"></script>
```

**Important:** These files should be in the same directory as your dashboard HTML files.

### Step 2: Initialize the Dashboard

Add this code in your main JavaScript (after page load):

```javascript
// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', async () => {
  window.dashboard = await initializeDashboard();
  
  if (window.dashboard) {
    console.log('✅ Dashboard initialized');
    loadDashboardData();
  }
});

async function loadDashboardData() {
  // Load all dashboard data
  const overview = await window.dashboard.loadDashboardOverview();
  const market = await window.dashboard.loadLiveMarketData();
  const trades = await window.dashboard.loadOpenTrades();
  const stats = await window.dashboard.loadTradingStats();
  
  // Update UI with data
  updateUI(overview, market, trades, stats);
}

function updateUI(overview, market, trades, stats) {
  // Update your HTML elements with the data
  if (overview) {
    document.getElementById('balance').textContent = 
      window.dashboard.formatCurrency(overview.balance);
  }
  if (market) {
    document.getElementById('nifty-price').textContent = 
      market.NIFTY?.price || 'Loading...';
  }
  // ... update more UI elements
}
```

---

## 📦 What's Included

### api_client.js
The main API client with 49 endpoints:

**Authentication**
- `login(email, password)`
- `signup(email, password, firstName, lastName)`
- `getMe()`
- `logout()`

**User Data**
- `getProfile()`
- `getDashboardOverview()`
- `getPortfolio()`

**Market Data**
- `getLiveMarketData()`
- `getQuote(symbol)`
- `getPriceHistory(symbol, interval, limit)`
- `openPriceStream(symbols, callback)` - WebSocket real-time

**Trading**
- `createTrade(symbol, direction, entryPrice, targetPrice, stopLoss, quantity)`
- `getOpenTrades()`
- `getClosedTrades(limit)`
- `closeTrade(tradeId, exitPrice)`
- `approveTrade(tradeId)`
- `getTradingStats()`

**Signals**
- `getSignals(limit)`
- `generateSignal(symbol, entryPrice, targetPrice, stopLoss)`
- `executeSignal(signalId)`

**Analysis**
- `getTechnicalAnalysis(symbol)`
- `getOptionsAnalysis(symbol)`
- `getAIInsights(symbol)`

**Paper Trading**
- `getPaperTradingAccount()`
- `executePaperTrade(symbol, direction, quantity, price)`

**System**
- `getHealth()`
- `getHealthDetailed()`
- `getStatus()`

### dashboard_utils.js
Helper class `DashboardManager` with:

**Data Loading**
- `loadDashboardOverview()`
- `loadLiveMarketData()`
- `loadOpenTrades()`
- `loadTradingStats()`
- `loadSignals(limit)`
- `loadTechnicalAnalysis(symbol)`
- `loadOptionsAnalysis(symbol)`

**Trading Operations**
- `createTrade(formData)`
- `closeTrade(tradeId, exitPrice)`
- `approveTrade(tradeId)`

**Events**
- `on(eventName, callback)` - Listen to events
- `emit(eventName, data)` - Trigger events

**Formatting**
- `formatCurrency(value)`
- `formatPercentage(value)`
- `formatDate(date)`
- `formatDateTime(date)`

---

## 💻 Usage Examples

### Example 1: Display User Balance

```javascript
async function displayBalance() {
  const overview = await window.dashboard.loadDashboardOverview();
  const balance = window.dashboard.formatCurrency(overview.balance);
  document.getElementById('balance').textContent = balance;
}
```

### Example 2: Create a Trade from a Form

```javascript
async function submitTradeForm(event) {
  event.preventDefault();
  
  const formData = {
    symbol: document.getElementById('symbol').value,
    direction: document.getElementById('direction').value,
    entryPrice: document.getElementById('entryPrice').value,
    targetPrice: document.getElementById('targetPrice').value,
    stopLoss: document.getElementById('stopLoss').value,
    quantity: document.getElementById('quantity').value
  };
  
  try {
    const trade = await window.dashboard.createTrade(formData);
    alert('Trade created: ' + trade.id);
    // Refresh trades list
    await displayOpenTrades();
  } catch (error) {
    alert('Error: ' + error.message);
  }
}

async function displayOpenTrades() {
  const trades = await window.dashboard.loadOpenTrades();
  // Update your trades table with the data
  const html = trades.map(trade => `
    <tr>
      <td>${trade.symbol}</td>
      <td>${trade.direction}</td>
      <td>${window.dashboard.formatCurrency(trade.entry_price)}</td>
      <td>${window.dashboard.formatCurrency(trade.target_price)}</td>
      <td>${window.dashboard.formatCurrency(trade.stop_loss)}</td>
    </tr>
  `).join('');
  
  document.getElementById('trades-table').innerHTML = html;
}
```

### Example 3: Display Live Market Data

```javascript
async function displayLiveMarket() {
  const market = await window.dashboard.loadLiveMarketData();
  
  if (market.NIFTY) {
    document.getElementById('nifty-price').textContent = 
      window.dashboard.formatCurrency(market.NIFTY.price);
    document.getElementById('nifty-change').textContent = 
      market.NIFTY.change.toFixed(2) + ' (' + 
      window.dashboard.formatPercentage(market.NIFTY.change_percent) + ')';
  }
  
  if (market.BANKNIFTY) {
    document.getElementById('banknifty-price').textContent = 
      window.dashboard.formatCurrency(market.BANKNIFTY.price);
    document.getElementById('banknifty-change').textContent = 
      market.BANKNIFTY.change.toFixed(2) + ' (' + 
      window.dashboard.formatPercentage(market.BANKNIFTY.change_percent) + ')';
  }
}
```

### Example 4: Display Trading Statistics

```javascript
async function displayStats() {
  const stats = await window.dashboard.loadTradingStats();
  
  document.getElementById('total-trades').textContent = stats.total_trades;
  document.getElementById('closed-trades').textContent = stats.closed_trades;
  document.getElementById('open-trades').textContent = stats.open_trades;
  document.getElementById('total-pnl').textContent = 
    window.dashboard.formatCurrency(stats.total_pnl);
  document.getElementById('win-rate').textContent = 
    window.dashboard.formatPercentage(stats.win_rate);
}
```

### Example 5: Listen to Events

```javascript
// Setup event listeners
window.dashboard.on('overview-loaded', (data) => {
  console.log('Overview loaded:', data);
  updateOverviewUI(data);
});

window.dashboard.on('market-data-loaded', (data) => {
  console.log('Market data loaded:', data);
  updateMarketUI(data);
});

window.dashboard.on('error', (error) => {
  console.error('Dashboard error:', error);
  showErrorNotification(error.message);
});

window.dashboard.on('trade-created', (trade) => {
  console.log('Trade created:', trade);
  refreshTradesList();
});
```

### Example 6: Real-Time Price Updates (WebSocket)

```javascript
let priceSocket = null;

function startPriceStream() {
  priceSocket = window.dashboard.subscribeToPrices(['NIFTY', 'BANKNIFTY'], 
    (error, data) => {
      if (error) {
        console.error('Price stream error:', error);
      } else {
        updateLivePrice(data);
      }
    }
  );
}

function stopPriceStream() {
  window.dashboard.unsubscribeFromPrices(priceSocket);
}

function updateLivePrice(data) {
  // data = { symbol: 'NIFTY', price: 24000, timestamp: '...' }
  const elem = document.getElementById(`price-${data.symbol}`);
  if (elem) {
    elem.textContent = window.dashboard.formatCurrency(data.price);
  }
}
```

### Example 7: Technical Analysis

```javascript
async function displayTechnicalAnalysis(symbol) {
  const analysis = await window.dashboard.loadTechnicalAnalysis(symbol);
  
  console.log('RSI:', analysis.rsi);
  console.log('EMA9:', analysis.ema9);
  console.log('EMA50:', analysis.ema50);
  console.log('Bollinger Bands:', analysis.bollinger_bands);
  console.log('MACD:', analysis.macd);
  
  // Display in your chart or table
  document.getElementById('rsi-value').textContent = analysis.rsi.toFixed(2);
  document.getElementById('trend').textContent = analysis.trend;
}
```

---

## 🔐 Authentication Flow

### Login User

```javascript
async function loginUser() {
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  
  try {
    const response = await window.dashboard.handleLogin(email, password);
    if (response) {
      // Logged in successfully, redirect to dashboard
      window.location.href = '/test/dashboard-live';
    }
  } catch (error) {
    console.error('Login failed:', error);
    alert('Login failed: ' + error.message);
  }
}

// Button click handler
document.getElementById('login-btn').addEventListener('click', loginUser);
```

### Logout User

```javascript
function logout() {
  window.dashboard.handleLogout();
}

// This will redirect to login page automatically
```

---

## ⚡ Performance Tips

### Caching

Certain endpoints cache data automatically (market data, analysis):

```javascript
// This will cache for 1 minute by default
const market = await window.dashboard.loadLiveMarketData();

// To skip cache:
window.dashboard.api.clearCache();
const market = await window.dashboard.loadLiveMarketData();
```

### Batch Loading

Load multiple pieces of data in parallel:

```javascript
// Load all data at once (faster)
const [overview, market, trades, stats, signals] = await Promise.all([
  window.dashboard.loadDashboardOverview(),
  window.dashboard.loadLiveMarketData(),
  window.dashboard.loadOpenTrades(),
  window.dashboard.loadTradingStats(),
  window.dashboard.loadSignals(20)
]);
```

### Conditional Loading

Load data only when needed:

```javascript
async function onTabChange(tabName) {
  switch(tabName) {
    case 'overview':
      await window.dashboard.loadDashboardOverview();
      break;
    case 'trading':
      await window.dashboard.loadOpenTrades();
      await window.dashboard.loadTradingStats();
      break;
    case 'research':
      await window.dashboard.loadTechnicalAnalysis('NIFTY');
      await window.dashboard.loadOptionsAnalysis('NIFTY');
      break;
  }
}
```

---

## 🧪 Testing

### Check Server Health

```javascript
// Test if server is running
async function checkServerHealth() {
  try {
    const health = await window.dashboard.api.getHealth();
    console.log('✅ Server is healthy:', health);
  } catch (error) {
    console.error('❌ Server is not responding:', error);
  }
}

checkServerHealth();
```

### Test Authentication

```javascript
// Check if user is logged in
if (window.dashboard.api.isAuthenticated()) {
  console.log('✅ User is authenticated');
  const user = await window.dashboard.api.getMe();
  console.log('User:', user);
} else {
  console.log('❌ User is not authenticated');
}
```

### Test API Endpoints

```javascript
// Test each category
async function testAPIs() {
  console.log('Testing APIs...');
  
  try {
    // Market Data
    const market = await window.dashboard.api.getLiveMarketData();
    console.log('✅ Market data:', market);
    
    // Trading
    const trades = await window.dashboard.api.getOpenTrades();
    console.log('✅ Open trades:', trades);
    
    // Analysis
    const analysis = await window.dashboard.api.getTechnicalAnalysis('NIFTY');
    console.log('✅ Technical analysis:', analysis);
    
  } catch (error) {
    console.error('❌ API test failed:', error);
  }
}

testAPIs();
```

---

## 🛠️ Troubleshooting

### Problem: "api_client is not defined"

**Solution:** Make sure `api_client.js` is loaded before `dashboard_utils.js`:

```html
<!-- Correct order -->
<script src="api_client.js"></script>
<script src="dashboard_utils.js"></script>
<script src="your-page-script.js"></script>
```

### Problem: "CORS error" or "Failed to fetch"

**Solution:** Make sure the server is running:

```bash
cd /Users/anshhdodia/Desktop/tradosphere_github
python3 tradosphere_saas_server.py
```

The server should show: `Running on http://127.0.0.1:8000`

### Problem: "Unauthorized" or "Invalid token"

**Solution:** User needs to login first. Check:

```javascript
console.log('Token:', window.dashboard.api.token);
console.log('Authenticated:', window.dashboard.api.isAuthenticated());
```

If not authenticated, redirect to login:

```javascript
if (!window.dashboard.api.isAuthenticated()) {
  window.location.href = '/test/login';
}
```

### Problem: "Data is undefined" or "null"

**Solution:** Make sure the API call succeeded:

```javascript
const data = await window.dashboard.loadLiveMarketData();
if (data) {
  console.log('Data loaded successfully:', data);
} else {
  console.error('Failed to load data');
}
```

---

## 📋 Integration Checklist

For each dashboard, ensure:

- [ ] `api_client.js` is in same directory
- [ ] `dashboard_utils.js` is in same directory
- [ ] Both scripts are loaded in HTML `<head>`
- [ ] `initializeDashboard()` called on page load
- [ ] Authentication check performed
- [ ] Data loading functions called
- [ ] UI elements updated with data
- [ ] Error handling added
- [ ] Event listeners setup
- [ ] Tested locally before pushing

---

## 🚀 Next Steps

1. **Test with existing dashboards**
   ```
   http://localhost:8000/test/dashboard-live
   http://localhost:8000/test/dashboard-saas
   http://localhost:8000/test/dashboard-unified
   ```

2. **Add to your dashboard files**
   - Add script tags
   - Add initialization code
   - Update HTML elements
   - Test thoroughly

3. **Deploy when ready**
   - Test locally first
   - Git commit the changes
   - Push to GitHub
   - Deploy to production

---

**Questions?** Check the browser console (F12) for detailed error messages and API responses.
