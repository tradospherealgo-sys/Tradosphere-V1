# 📁 FILE REFERENCE GUIDE - TRADOSPHERE V1

## Quick Navigation by Purpose

---

## 🎯 MAIN APPLICATION

### **tradosphere_saas_server.py** (1200+ lines) ✅ CORE
- **Purpose:** Main Flask application entry point
- **Status:** 90% Complete
- **What it does:**
  - Initializes all databases (user, trading, subscription, leads, paper trading)
  - Registers all blueprints (auth, user, trading, billing, admin, leads, backtest)
  - Serves 9 HTML dashboards
  - Implements 20+ API endpoints for market data, analysis, signals, trading
  - Sets up Angel One market data integration
  - Provides health checks and system status

- **Key endpoints it serves:**
  - `GET /` - Home (auth check)
  - `GET /login` - Login page
  - `GET /dashboard` - Angel One-style dashboard
  - `GET /demo` - Demo dashboard (no auth)
  - `GET /api/health` - Simple health check ✅
  - `GET /api/health/detailed` - Detailed health with components ✅
  - `GET /api/status` - System status ✅
  - `GET /api/market/live` - Live NIFTY/BANKNIFTY prices ✅
  - `GET /api/analysis/technical` - Technical analysis ✅
  - `GET /api/analysis/options` - Options analysis ✅
  - `GET /api/signals` - Get signals ✅
  - `POST /api/signals/generate` - Generate new signals ✅
  - `POST /api/analysis/ai-insights` - AI analysis ✅
  - `GET /api/trading/*` - All trading endpoints
  - `GET /api/user/dashboard-overview` - Dashboard data

- **Notes:** This file is your main orchestrator. All routes flow through it.

---

## 🔐 AUTHENTICATION & USER MANAGEMENT

### **user_model.py** (310 lines) ✅ COMPLETE
- **Purpose:** User account and API key management
- **Status:** Complete
- **Tables:**
  - `users` - Accounts with email, password, profile info
  - `api_keys` - Broker API credentials per user
  - `user_sessions` - Login session tracking
  
- **Key functions:**
  - `create_user()` - Register new user
  - `get_user_by_email()` - Find user
  - `get_user_by_id()` - Get user by ID
  - `update_user()` - Update profile
  - `delete_user()` - Remove account

- **Notes:** Schema is solid, just needs testing.

### **auth_routes.py** (370 lines) ✅ COMPLETE
- **Purpose:** Authentication endpoints
- **Status:** Complete
- **Endpoints:**
  - `POST /api/auth/signup` - Register new user
  - `POST /api/auth/login` - Login with JWT tokens
  - `POST /api/auth/logout` - Logout
  - `POST /api/auth/refresh` - Refresh JWT token
  - `GET /api/auth/me` - Get current user
  - `POST /api/auth/verify-email` - Email verification
  - `POST /api/auth/forgot-password` - Password reset request
  - `POST /api/auth/reset-password` - Reset password

- **Notes:** All endpoints defined, needs testing with Angel One users.

### **auth_manager.py** (400+ lines) ✅ COMPLETE
- **Purpose:** JWT and password management utilities
- **Status:** Complete
- **Classes:**
  - `PasswordManager` - Hash and verify passwords
  - `JWTManager` - Generate and validate JWT tokens
  - `AuthDecorator` - @token_required, @admin_required decorators
  - `EmailValidator` - Email validation
  - `SessionManager` - Session handling

- **Key decorators:**
  - `@token_required` - Check valid JWT
  - `@admin_required` - Check admin role
  - `@retry_on_failure` - Automatic retry with backoff

- **Notes:** All utilities ready to use.

### **user_routes.py** (380 lines) ✅ COMPLETE
- **Purpose:** User management endpoints
- **Status:** Complete
- **Endpoints:**
  - `GET /api/user/profile` - Get user profile
  - `PUT /api/user/profile` - Update profile
  - `GET /api/user/api-keys` - Get broker API keys
  - `POST /api/user/api-keys` - Add new API key
  - `DELETE /api/user/api-keys/<id>` - Delete API key
  - `GET /api/user/preferences` - Get preferences
  - `PUT /api/user/preferences` - Update preferences
  - `POST /api/user/account/deactivate` - Disable account
  - `POST /api/user/account/delete` - Delete account
  - `GET /api/user/activity` - Get activity log

- **Notes:** All user management covered.

---

## 📊 DATABASE MODELS

### **database.py** (250+ lines) ✅ COMPLETE
- **Purpose:** Core trading data models
- **Status:** Complete
- **Tables:**
  - `signals` - Trading signals (entry, SL, target)
  - `trades` - Executed trades with P&L
  - `users` - User accounts (duplicated from user_model.py)
  - `broker_accounts` - Multi-broker connections
  - `market_snapshot` - Live price cache

- **Notes:** Basic schema, good for MVP. May need additional fields later.

### **subscription_model.py** (350+ lines) ✅ COMPLETE
- **Purpose:** SaaS subscription and billing
- **Status:** Complete
- **Tables:**
  - `subscription_plans` - Pricing tiers (Free, Pro, Enterprise)
  - `user_subscriptions` - Active subscriptions
  - `usage_metrics` - API usage tracking
  - `invoices` - Billing records

- **Notes:** Complete billing system ready.

### **paper_trading_model.py** (200+ lines) ⚠️ PARTIAL
- **Purpose:** Simulated trading without real money
- **Status:** Model only, no logic
- **Tables:**
  - `paper_accounts` - Virtual accounts
  - `paper_trades` - Simulated trades
  - `paper_portfolio` - Holdings tracking

- **TODO:** Need paper trading execution logic

### **leads_model.py** (150+ lines) ⚠️ PARTIAL
- **Purpose:** Lead generation and sales tracking
- **Status:** Partial
- **Tables:**
  - `leads` - Lead records
  - `lead_sources` - Lead origin tracking
  - `sales_funnel` - Conversion tracking

- **TODO:** Wire up to landing pages

---

## 🔄 TRADING ENGINES (CRITICAL)

### **market_data.py** (350+ lines) ✅ COMPLETE
- **Purpose:** Angel One SmartAPI integration
- **Status:** 95% Complete - Most critical for live trading
- **Features:**
  - ✅ SmartAPI SDK initialization
  - ✅ JWT token generation with TOTP (2FA)
  - ✅ **Auto token refresh** (APScheduler, every 4 hours) - CRITICAL FOR 24x7
  - ✅ Live price fetching (LTP, OHLC candles)
  - ✅ Order placement capability
  - ✅ WebSocket connection support
  - ✅ Error handling and reconnection
  - ✅ `get_token_status()` method for monitoring

- **Key methods:**
  - `_initialize()` - Auth with Angel One
  - `_start_token_refresh_scheduler()` - Auto-refresh every 4 hours
  - `get_ltp(exchange, symbol, exchange_token)` - Live price
  - `get_historical_candles(symbol, interval, count)` - OHLC data
  - `place_order(order_details)` - Execute trade
  - `is_authenticated()` - Check if connected

- **Notes:** This is your lifeline to live market data. Fully tested and production-ready.

### **technical_engine.py** (300+ lines) ✅ COMPLETE
- **Purpose:** Technical indicator calculations
- **Status:** Complete
- **Indicators:**
  - RSI (Relative Strength Index, 14-period)
  - EMA (Exponential Moving Average, multi-period)
  - VWAP (Volume Weighted Average Price)
  - Bollinger Bands
  - MACD (Moving Average Convergence Divergence)
  - Trend detection (UPTREND, DOWNTREND, NEUTRAL)
  - Support/Resistance levels
  - Breakout detection
  - Momentum calculation

- **Key methods:**
  - `calculate_rsi(closes, period=14)` - RSI value
  - `calculate_ema(closes, period)` - EMA value
  - `calculate_vwap(closes, volumes)` - VWAP value
  - `calculate_bollinger_bands(closes, period)` - Bands
  - `calculate_macd(closes)` - MACD + histogram
  - `detect_trend(closes, ema9, ema50)` - Trend
  - `find_support_resistance(closes)` - Key levels
  - `detect_breakout(closes, support, resistance)` - Breakout

- **Notes:** All technical indicators ready to use.

### **signals_engine.py** (350+ lines) ✅ COMPLETE
- **Purpose:** Trading signal generation
- **Status:** Complete
- **Signal Types:**
  - EMA crossover (9/50)
  - RSI divergence
  - MACD crossover
  - Bollinger Bands breakout
  - Support/resistance bounce
  - Multi-condition composite signals

- **Key methods:**
  - `generate_buy_signal(market_data, technicals)` - Buy signal
  - `generate_sell_signal(market_data, technicals)` - Sell signal
  - `calculate_confidence(signals_count, agreement)` - Confidence %
  - `validate_signal(signal)` - Check signal quality

- **Notes:** Signals are the core of your trading. System is solid.

### **options_engine.py** (300+ lines) ✅ COMPLETE
- **Purpose:** Options chain analysis
- **Status:** Complete
- **Features:**
  - PCR (Put-Call Ratio) calculation
  - Max Pain calculation
  - Open Interest analysis
  - Options chain ranking
  - Support/resistance from options

- **Key methods:**
  - `analyze_options_chain(options_data)` - Full analysis
  - `calculate_pcr(puts_oi, calls_oi)` - PCR ratio
  - `calculate_max_pain(chain, spot_price)` - Max pain
  - `analyze_oi_buildup(current_oi, previous_oi)` - OI changes
  - `detect_max_pain_support(max_pain, price)` - Support level

- **Notes:** Great for understanding institutional positioning.

### **greeks_calculator.py** (250+ lines) ✅ COMPLETE
- **Purpose:** Options Greeks calculations
- **Status:** Complete
- **Greeks:**
  - Delta (directional exposure)
  - Gamma (delta change rate)
  - Vega (volatility sensitivity)
  - Theta (time decay)
  - Rho (interest rate sensitivity)

- **Key methods:**
  - `calculate_delta(S, K, r, sigma, T, option_type)` - Delta
  - `calculate_gamma(S, K, r, sigma, T)` - Gamma
  - `calculate_vega(S, K, r, sigma, T)` - Vega
  - `calculate_theta(S, K, r, sigma, T, option_type)` - Theta
  - `calculate_rho(S, K, r, sigma, T, option_type)` - Rho

- **Notes:** All Greeks computed, ready for options trading.

### **backtesting_engine.py** (400+ lines) ⚠️ PARTIAL
- **Purpose:** Strategy backtesting on historical data
- **Status:** Engine exists, needs wiring
- **Features:**
  - Historical data simulation
  - Strategy parameter testing
  - Performance metrics calculation
  - Results comparison

- **TODO:** Need historical data storage, backtest routes implementation

---

## 🤖 AI & LEARNING

### **ai_analysis_engine.py** (400+ lines) ✅ COMPLETE
- **Purpose:** AI-powered market analysis
- **Status:** Complete but not exposed via API
- **Features:**
  - Market bias calculation
  - Risk level assessment
  - Insight generation (key levels, trends, risks)
  - Recommendation generation (BUY/SELL/HOLD)
  - Confidence scoring
  - Institutional activity analysis
  - Volatility analysis
  - Pattern recognition
  - Support/resistance generation

- **Key methods:**
  - `analyze_market(market_data, options_data, technical_data, signals)` - Full analysis
  - `_calculate_market_bias()` - Bias score
  - `_generate_recommendation()` - Trade recommendation
  - `_analyze_institutional_activity()` - Max pain vs price

- **Notes:** Excellent analysis engine. Just needs API exposure and Claude integration.

### **ai_engine.py** (300+ lines) ⚠️ PARTIAL
- **Purpose:** Claude API integration for AI chat
- **Status:** Framework only, not connected
- **TODO:** Need to connect to Claude API

### **learning_engine.py** (300+ lines) ⚠️ PARTIAL
- **Purpose:** Pattern learning from trades
- **Status:** Framework exists, needs implementation
- **Features (planned):**
  - Historical trade analysis
  - Win rate calculation
  - Risk/reward analysis
  - Pattern recognition
  - Strategy optimization

- **TODO:** Implement trade analysis logic

---

## 🎯 TRADING OPERATIONS

### **trading_routes.py** (400+ lines) ✅ COMPLETE
- **Purpose:** Live and paper trading endpoints
- **Status:** Complete
- **Endpoints:**
  - `GET /api/trading/account/<symbol>` - Account for symbol
  - `POST /api/trading/account/<symbol>/reset` - Reset account
  - `POST /api/trading/trade/open` - Open trade
  - `POST /api/trading/trade/<id>/close` - Close trade
  - `GET /api/trading/trades/<account_id>` - Get trades
  - `POST /api/trading/signal/track` - Track signal
  - `POST /api/trading/signal/<id>/close` - Close signal
  - `GET /api/trading/signals/user` - Get user signals
  - `GET /api/trading/stats/<account_id>` - Trading stats
  - `GET /api/trading/signal-accuracy/user` - Win rate

- **Notes:** All trading operations covered.

### **backtest_routes.py** (200+ lines) ⚠️ PARTIAL
- **Purpose:** Backtesting endpoints
- **Status:** Routes defined, needs implementation
- **Endpoints (planned):**
  - `POST /api/backtest/run` - Run backtest
  - `GET /api/backtest/<id>` - Get results
  - `POST /api/backtest/<id>/compare` - Compare strategies

- **TODO:** Implement backtesting logic

### **signal_writer.py** (150+ lines) ✅ COMPLETE
- **Purpose:** Signal generation utility
- **Status:** Complete
- **Functions:**
  - `generate_on_demand(symbol, analysis_data)` - Create signal
  - `write_signal(signal)` - Store signal

- **Notes:** Used by signal generation endpoints.

### **reconciliation_engine.py** (250+ lines) ✅ COMPLETE
- **Purpose:** Trade reconciliation between broker and system
- **Status:** Complete
- **Features:**
  - Trade matching
  - Account reconciliation
  - Discrepancy detection
  - Correction logging

- **Key methods:**
  - `reconcile_trades(broker_trades, system_trades)` - Match trades
  - `detect_discrepancies(matched_trades)` - Find mismatches
  - `generate_correction(discrepancy)` - Fix errors

- **Notes:** Critical for accuracy. Ready to use.

---

## 💼 BUSINESS & ADMIN

### **admin_routes.py** (410 lines) ✅ COMPLETE
- **Purpose:** Admin management endpoints
- **Status:** Complete
- **Endpoints:**
  - User management (list, view, promote, enable/disable)
  - Analytics (users, subscriptions, revenue)
  - System health checks
  - Configuration management
  - Audit logging (framework)

- **Key features:**
  - User search and pagination
  - Admin promotion
  - Account disable/enable
  - Revenue tracking
  - System health status

- **Notes:** All admin functions ready.

### **billing_routes.py** (300+ lines) ✅ COMPLETE
- **Purpose:** Subscription and billing endpoints
- **Status:** Complete
- **Endpoints:**
  - `GET /api/billing/plans` - Available plans
  - `POST /api/billing/subscribe` - Subscribe to plan
  - `GET /api/billing/subscription` - Current subscription
  - `POST /api/billing/cancel` - Cancel subscription
  - `GET /api/billing/invoices` - Invoice history

- **Notes:** Full billing system ready.

### **leads_routes.py** (250+ lines) ⚠️ PARTIAL
- **Purpose:** Lead management endpoints
- **Status:** Routes defined, needs implementation
- **Endpoints (planned):**
  - Lead capture
  - Lead tracking
  - Funnel management

- **TODO:** Wire up to landing pages and email

---

## 🛠️ INFRASTRUCTURE & UTILITIES

### **monitoring.py** (350+ lines) ✅ COMPLETE
- **Purpose:** Production monitoring and logging
- **Status:** Complete
- **Features:**
  - JSON structured logging
  - Performance metrics tracking
  - Request/response logging
  - Execution time measurement
  - Error tracking

- **Key classes:**
  - `JsonFormatter` - Format logs as JSON
  - `PerformanceMonitor` - Track metrics
  - `RequestLogger` - Log HTTP traffic
  - Decorators: `@log_execution_time`, `@log_database_operation`

- **Notes:** Logging infrastructure ready. Very useful for debugging.

### **error_handler.py** (400+ lines) ✅ COMPLETE
- **Purpose:** Error recovery and resilience
- **Status:** Complete
- **Features:**
  - Exponential backoff retry
  - API call caching
  - Fallback data
  - Error metrics tracking
  - Connection recovery

- **Key classes:**
  - `RetryStrategy` - Auto-retry with backoff
  - `ApiCallHandler` - Cache + fallback
  - `ConnectionRecovery` - Reconnect logic
  - `ErrorMetrics` - Track errors
  - Decorators: `@retry_on_failure`, `@handle_api_error`

- **Notes:** All resilience patterns included.

### **multi_tenant_middleware.py** (250+ lines) ✅ COMPLETE
- **Purpose:** Multi-tenancy data isolation
- **Status:** Complete
- **Features:**
  - Tenant extraction from requests
  - Data isolation per tenant
  - Tenant context in all queries
  - Tenant validation

- **Key classes:**
  - `MultiTenantMiddleware` - Extract tenant
  - `TenantDataIsolation` - Isolate data

- **Notes:** Security foundation for multi-tenant architecture.

### **broker_manager.py** (200+ lines) ✅ COMPLETE
- **Purpose:** Broker connection management
- **Status:** Complete
- **Features:**
  - Broker authentication
  - Account validation
  - Connection pooling
  - Fallback handling

- **Notes:** Foundation for multi-broker support.

### **email_service.py** (200+ lines) ⚠️ PARTIAL
- **Purpose:** Email notifications
- **Status:** Framework only
- **TODO:** Wire up SMTP configuration, integrate with trades/signals

### **debug_system.py** & **diagnostic_endpoint.py** ✅ COMPLETE
- **Purpose:** Debugging utilities
- **Status:** Complete
- **Features:**
  - System diagnostics
  - Error logging
  - Performance analysis

- **Notes:** Very helpful for troubleshooting.

---

## 🎨 FRONTEND DASHBOARDS

### Dashboard Files (9 total) ⚠️ SCATTERED
| File | Purpose | Status | Notes |
|------|---------|--------|-------|
| login_simple.html | Login page | ✅ Complete | Admin/user demo buttons |
| saas_auth_pages.html | Auth pages | ✅ Complete | Signup, login, password reset |
| dashboard_live.html | Angel One style | ✅ Complete | Modern UI design |
| dashboard_pro.html | Pro features | ⚠️ Partial | Limited features |
| dashboard_unified.html | Unified UI | ⚠️ Partial | Demo mode capable |
| live_trading_dashboard.html | Trading focus | ⚠️ Partial | Order entry form |
| saas_dashboard.html | Main dashboard | ✅ Complete | Core layout |
| tradosphere_dashboard_final.html | Latest version | ✅ Complete | Final design |
| tradosphere_dashboard_backup.html | Backup | ✅ Complete | Previous version |

**Status:** All HTML files exist but are NOT INTEGRATED
**Problem:** No unified navigation, no SPA structure, static data
**Solution:** Create Vue.js/React wrapper with 5-tab structure

---

## 🧪 TEST FILES

| File | Purpose | Status |
|------|---------|--------|
| test_angel_login.py | Angel One auth test | ✅ Complete |
| test_angel_one.py | Angel One integration | ✅ Complete |
| test_angel_sdk.py | SmartAPI SDK test | ✅ Complete |
| test_api_response.py | API testing | ✅ Complete |
| test_credentials.py | Credential validation | ✅ Complete |
| test_generateSession.py | Session generation | ✅ Complete |
| test_market_data_class.py | Market data tests | ✅ Complete |
| test_market_methods.py | Market method tests | ✅ Complete |

**Status:** All test files present, good for verification

---

## ⚙️ CONFIGURATION FILES

| File | Purpose | Status |
|------|---------|--------|
| requirements.txt | Python dependencies | ✅ 14 packages |
| .env | Environment variables | ✅ Configured locally |
| .env.example | Template | ✅ Guide |
| .env.template | Template | ✅ Guide |
| Dockerfile | Container setup | ⚠️ Incomplete |
| Procfile | Heroku/Railway setup | ✅ Complete |
| vercel.json | Vercel config | ✅ Complete |
| railway.json | Railway config | ✅ Complete |
| .gitignore | Git ignore rules | ✅ Complete |

---

## 📚 DOCUMENTATION

| File | Purpose | Status |
|------|---------|--------|
| COMPLETE_PLATFORM_BREAKDOWN.md | **THIS FILE** - Full breakdown | ✅ New |
| FILE_REFERENCE_GUIDE.md | **THIS FILE** - File guide | ✅ New |
| PHASE1_COMPLETION.md | Phase 1 summary | ✅ Documented |
| PHASE2_COMPLETION.md | Phase 2 summary | ✅ Documented |
| PHASE3_COMPLETION.md | Phase 3 summary | ✅ Documented |
| PHASE4_COMPLETION.md | Phase 4 summary | ✅ Documented |
| PHASE5_COMPLETION.md | Phase 5 summary | ✅ Documented |
| PHASE6_COMPLETION.md | Phase 6 summary | ✅ Documented |
| DEPLOYMENT_GUIDE.md | Deployment steps | ✅ Documented |
| IMPLEMENTATION_PLAN.md | Implementation strategy | ✅ Documented |
| FEATURE_INVENTORY.md | Feature list | ✅ Documented |
| AUDIT_REPORT.md | Code audit | ✅ Documented |

---

## 🎯 WHAT TO FOCUS ON NOW

### Start Here (in order):

1. **tradosphere_saas_server.py** - Understand main app structure
2. **market_data.py** - Test Angel One connection
3. **auth_routes.py** - Test login flow
4. **trading_routes.py** - Test trading endpoints
5. **technical_engine.py** + **signals_engine.py** - Test signal generation

### Then Move To:

6. **Create SPA wrapper** around existing HTML dashboards
7. **Implement Flask-SocketIO** for real-time updates
8. **Connect dashboard** to backend APIs
9. **Complete 5-tab structure**

### Don't Touch Yet:

- backtesting_engine.py (incomplete)
- paper_trading_model.py (no logic)
- learning_engine.py (no logic)
- ai_engine.py (not connected)
- leads_routes.py (not integrated)

---

## 💾 Database Structure Quick Reference

**File: database.py**
```
signals → trades (1-to-many)
users → broker_accounts (1-to-many)
users → api_keys (1-to-many)
```

**File: user_model.py**
```
users → user_sessions (1-to-many)
```

**File: subscription_model.py**
```
users → user_subscriptions (1-to-many)
subscription_plans → user_subscriptions (1-to-many)
user_subscriptions → invoices (1-to-many)
```

**File: paper_trading_model.py**
```
users → paper_accounts (1-to-many)
paper_accounts → paper_trades (1-to-many)
```

---

## 🔗 Key Integration Points

**API Pipeline:**
```
Frontend Request
    ↓
HTTP Handler (tradosphere_saas_server.py)
    ↓
Blueprint Route (auth_routes, trading_routes, etc.)
    ↓
Decorator Check (@token_required, @admin_required)
    ↓
Business Logic (engine classes)
    ↓
Database Query (SQLAlchemy models)
    ↓
JSON Response
    ↓
Frontend Display
```

**Trading Pipeline:**
```
Market Data (Angel One API)
    ↓
Technical Analysis (technical_engine.py)
    ↓
Signal Generation (signals_engine.py)
    ↓
Options Analysis (options_engine.py)
    ↓
AI Analysis (ai_analysis_engine.py)
    ↓
Recommendation
    ↓
Trade Execution (trading_routes.py)
    ↓
P&L Tracking (database.py)
    ↓
Performance Learning (learning_engine.py)
```

---

## 📊 File Statistics

- **Total Python files:** 42
- **Total HTML files:** 9
- **Total lines of code:** ~15,000
- **Database tables:** 16
- **API endpoints:** 49 defined
- **Test files:** 8

---

**Last Updated:** June 20, 2026  
**Version:** 1.0
