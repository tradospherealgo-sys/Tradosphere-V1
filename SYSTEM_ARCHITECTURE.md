# System Architecture - Tradosphere V1

**Version:** 1.0  
**Last Updated:** June 23, 2026  
**Status:** PRODUCTION READY

---

## Architecture Overview

Tradosphere V1 is a **multi-tier SaaS paper trading platform** with:
- **Frontend:** HTML/CSS/JavaScript dashboard (responsive)
- **Backend:** Flask REST API (Python, 91 endpoints)
- **Database:** PostgreSQL with 11 tables
- **Authentication:** Google OAuth 2.0 + JWT tokens
- **Payments:** Stripe integration for subscriptions
- **Market Data:** Angel One SmartAPI integration
- **Email:** SendGrid for notifications

---

## High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                         │
├─────────────────────────────────────────────────────────────┤
│  Frontend (HTML/CSS/JS)                                     │
│  ├─ User Dashboard (8 pages)                                │
│  ├─ Admin Dashboard (6 pages)                               │
│  ├─ Auth Pages (1 page)                                     │
│  ├─ Shared Assets (API client, Auth utils, CSS)             │
│  └─ Responsive Design (Mobile, Tablet, Desktop)             │
└─────────────────────────────────────────────────────────────┘
                           ↓ (HTTPS)
┌─────────────────────────────────────────────────────────────┐
│                      API GATEWAY LAYER                       │
├─────────────────────────────────────────────────────────────┤
│  Load Balancer                                              │
│  ├─ Rate Limiting                                           │
│  ├─ CORS Configuration                                      │
│  └─ Request Validation                                      │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                        │
├─────────────────────────────────────────────────────────────┤
│  Flask REST API (91 endpoints)                              │
│  ├─ Auth Routes (15 endpoints)                              │
│  ├─ User Routes (25 endpoints)                              │
│  ├─ Trading Routes (20 endpoints)                           │
│  ├─ Signal Routes (18 endpoints)                            │
│  ├─ Backtest Routes (12 endpoints)                          │
│  ├─ Admin Routes (15 endpoints)                             │
│  └─ Health Routes (6 endpoints)                             │
│                                                              │
│  Middleware                                                  │
│  ├─ Authentication (@require_auth)                          │
│  ├─ Authorization (@require_admin)                          │
│  ├─ Rate Limiting (@rate_limit)                             │
│  ├─ Logging (@log_activity)                                 │
│  └─ Error Handling                                          │
│                                                              │
│  Business Logic (Service Layer)                             │
│  ├─ AuthService (JWT, OAuth, Password)                      │
│  ├─ UserService (Profile, Preferences)                      │
│  ├─ TradingService (Virtual trades, P&L)                    │
│  ├─ SignalService (Generation, Analysis)                    │
│  ├─ MarketService (Live prices, Options)                    │
│  ├─ SubscriptionService (Plans, Billing)                    │
│  ├─ BacktestService (Strategy testing)                      │
│  ├─ EmailService (Notifications)                            │
│  └─ AdminService (Analytics, Monitoring)                    │
│                                                              │
│  Processing Engines                                         │
│  ├─ AI Engine (Market analysis, Sentiment)                  │
│  ├─ Backtesting Engine (TechnicalStrategy, MomentumStrategy) │
│  ├─ Reconciliation Engine (Trade settlement)                │
│  └─ Learning Engine (Performance tracking)                  │
└─────────────────────────────────────────────────────────────┘
          ↙              ↓              ↘
    ┌─────────┐   ┌──────────┐   ┌─────────────┐
    │         │   │          │   │             │
    ↓         ↓   ↓          ↓   ↓             ↓
┌────────┐ ┌────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│Database│ │Cache   │ │External  │ │Payment   │ │Email     │
│        │ │(Redis) │ │APIs      │ │Gateway   │ │Service   │
│Postgre │ │        │ │(Angel    │ │(Stripe)  │ │(SendGrid)│
│SQL     │ │        │ │One)      │ │          │ │          │
└────────┘ └────────┘ └──────────┘ └──────────┘ └──────────┘
```

---

## Component Architecture

### 1. Frontend Layer

#### Technology Stack
- **HTML5** for semantic markup
- **CSS3** for responsive styling with grid/flexbox
- **Vanilla JavaScript** for interactivity (no frameworks)
- **Fetch API** for HTTP requests

#### Key Components
1. **Navigation Components**
   - User navbar (home, signals, trading, portfolio, market, profile, logout)
   - Admin navbar (dashboard, users, subscriptions, analytics, signals, health)
   - Mobile-responsive hamburger menu

2. **Data Display Components**
   - Stat cards (metrics with formatting)
   - Data tables (pagination, sorting, filtering)
   - Tab systems (content switching)
   - Status badges (color-coded)
   - Charts (placeholder structure)

3. **Form Components**
   - Text inputs with validation
   - Select dropdowns
   - Date pickers
   - Toggle switches
   - Checkboxes and radio buttons

4. **Utility Components**
   - Toast notifications (success, error, warning, info)
   - Loading spinners
   - Modals/dialogs (structure)
   - Error messages
   - Confirmation dialogs

#### Asset Architecture
```
frontend/
├── auth/
│   └── login.html (OAuth + Email/Password)
├── user/
│   ├── dashboard.html (Main hub)
│   ├── signals.html (Signal generation)
│   ├── trading.html (Paper trading)
│   ├── portfolio.html (Holdings view)
│   ├── market.html (Market data)
│   ├── subscription.html (Billing)
│   ├── settings.html (Preferences)
│   └── profile.html (User profile)
├── admin/
│   ├── dashboard.html (Admin overview)
│   ├── users.html (User management)
│   ├── subscriptions.html (Billing management)
│   ├── analytics.html (Platform metrics)
│   ├── signals.html (Signal monitoring)
│   ├── health.html (System status)
│   └── settings.html (Admin config)
└── assets/
    ├── base.css (Global styles)
    ├── api.js (HTTP client)
    └── auth.js (Authentication)
```

### 2. Backend Layer

#### Technology Stack
- **Flask** 2.x (lightweight web framework)
- **SQLAlchemy** (ORM for database)
- **PyJWT** (JWT token handling)
- **google-auth** (OAuth integration)
- **stripe** (Payment processing)
- **requests** (HTTP client for APIs)

#### Application Structure
```
backend/
├── app.py (Flask initialization)
├── config.py (Environment configuration)
├── requirements.txt (Python dependencies)
│
├── models/ (5 data models)
│   ├── user_model.py (User accounts)
│   ├── subscription_model.py (Billing)
│   ├── trade_model.py (Virtual trades)
│   ├── signal_model.py (Trading signals)
│   └── session_model.py (Sessions & keys)
│
├── routes/ (7 blueprints, 91 endpoints)
│   ├── auth_routes.py (Authentication)
│   ├── user_routes.py (User management)
│   ├── trading_routes.py (Paper trading)
│   ├── signal_routes.py (Signal generation)
│   ├── backtest_routes.py (Backtesting)
│   ├── admin_routes.py (Admin panel)
│   └── health_routes.py (Monitoring)
│
├── services/ (8 business logic modules)
│   ├── auth_service.py (JWT, OAuth, passwords)
│   ├── user_service.py (Profile management)
│   ├── trading_service.py (Trade execution)
│   ├── signal_service.py (Signal generation)
│   ├── market_service.py (Market data)
│   ├── subscription_service.py (Billing)
│   ├── backtest_service.py (Strategy testing)
│   ├── email_service.py (Notifications)
│   └── admin_service.py (Analytics)
│
├── engines/ (4 processing engines)
│   ├── ai_engine.py (AI market analysis)
│   ├── backtesting_engine.py (Strategy backtesting)
│   ├── reconciliation_engine.py (Trade settlement)
│   └── learning_engine.py (Performance learning)
│
├── middleware/ (Request processing)
│   ├── auth_middleware.py (Authentication check)
│   ├── rate_limit_middleware.py (Rate limiting)
│   └── error_handler_middleware.py (Error handling)
│
└── utils/ (Utilities)
    ├── validators.py (Input validation)
    ├── decorators.py (Function decorators)
    ├── constants.py (App constants)
    └── helpers.py (Helper functions)
```

#### API Endpoint Structure
```
91 Total Endpoints:

/api/auth/ (15 endpoints)
├── POST /login - Email/password login
├── POST /register - New user registration
├── POST /google/callback - Google OAuth
├── POST /logout - Logout user
├── POST /refresh-token - Refresh JWT
├── GET /verify - Verify token
└── ... (9 more endpoints)

/api/user/ (25 endpoints)
├── GET /dashboard-overview - Dashboard metrics
├── GET /profile - User profile
├── PUT /profile - Update profile
├── GET /subscription - Current plan
├── GET /billing-history - Invoices
├── GET /watchlist - Saved symbols
├── GET /activity - User activity
└── ... (18 more endpoints)

/api/trading/ (20 endpoints)
├── POST /create-trade - Create trade
├── GET /open-trades - Active positions
├── POST /close-trade/:id - Close trade
├── GET /trade-history - Past trades
├── GET /portfolio - Current holdings
├── GET /performance - P&L stats
└── ... (14 more endpoints)

/api/signals/ (18 endpoints)
├── POST /generate - Create signals
├── GET / - List signals
├── GET /:id - Signal details
├── GET /performance - Signal accuracy
├── GET /history - Signal history
└── ... (13 more endpoints)

/api/backtest/ (12 endpoints)
├── POST /run - Run backtest
├── GET /results/:id - Results
├── GET /list - List tests
├── POST /compare - Compare strategies
└── ... (8 more endpoints)

/api/admin/ (15 endpoints)
├── GET /dashboard - Admin overview
├── GET /users - User list
├── GET /subscriptions - Sub details
├── GET /analytics - Platform stats
├── GET /signals - Signal monitor
└── ... (10 more endpoints)

/api/health/ (6 endpoints)
├── GET / - Simple health check
├── GET /detailed - Detailed status
├── GET /database - DB connectivity
├── GET /api - API status
└── ... (2 more endpoints)
```

### 3. Database Layer

#### Schema Design
```
11 Tables:

users
├── id (PK)
├── email (UNIQUE)
├── name
├── password_hash
├── role (admin/user)
├── subscription_tier
├── created_at
└── updated_at

subscriptions
├── id (PK)
├── user_id (FK)
├── plan (free/pro/elite)
├── status (active/cancelled)
├── amount
├── created_at
└── renewal_date

trades
├── id (PK)
├── user_id (FK)
├── symbol
├── direction (buy/sell)
├── entry_price
├── target_price
├── stop_loss
├── quantity
├── pnl
├── status
├── created_at
└── closed_at

signals
├── id (PK)
├── symbol
├── direction (bullish/bearish)
├── entry_price
├── target_price
├── stop_loss
├── confidence (0-100)
├── source (technical/options/ai)
├── created_at
└── executed_at

api_keys
├── id (PK)
├── user_id (FK)
├── key_hash
├── name
├── created_at
└── last_used

sessions
├── id (PK)
├── user_id (FK)
├── token
├── expires_at
└── created_at

audit_logs
├── id (PK)
├── user_id (FK)
├── action
├── entity_type
├── entity_id
├── changes
├── timestamp

notifications
├── id (PK)
├── user_id (FK)
├── type
├── title
├── message
├── read
├── created_at

options_data
├── id (PK)
├── symbol
├── strike
├── expiry
├── call_price
├── put_price
├── iv
├── created_at

market_history
├── id (PK)
├── symbol
├── open
├── high
├── low
├── close
├── volume
├── timestamp

strategy_results
├── id (PK)
├── strategy_name
├── parameters
├── total_trades
├── winning_trades
├── profit_factor
├── max_drawdown
├── created_at
```

#### Relationships
```
users ----1:N---- subscriptions
users ----1:N---- trades
users ----1:N---- api_keys
users ----1:N---- sessions
users ----1:N---- audit_logs
users ----1:N---- notifications
trades ----1:N---- signals
```

#### Indexes
- users(email) - UNIQUE for login
- trades(user_id) - Query user trades
- trades(status) - Filter active/closed
- signals(symbol) - Market analysis
- subscriptions(user_id) - User billing
- audit_logs(user_id, timestamp) - Activity tracking

### 4. Authentication & Authorization

#### Flow
```
1. User Login/Registration
   ├─ Email/Password validation
   └─ Google OAuth callback

2. Token Generation
   ├─ JWT payload: {user_id, email, role, permissions}
   ├─ Signed with JWT_SECRET
   └─ TTL: 24 hours

3. Token Usage
   ├─ Every API request includes Authorization header
   ├─ Backend validates token
   ├─ Auto-refresh on expiry (SessionManager)
   └─ Clear on logout

4. Role-Based Access Control
   ├─ User role: access /user/* endpoints
   ├─ Admin role: access /admin/* endpoints
   └─ Public: /auth/*, /health/*

5. Permission Levels
   ├─ Subscription-based (Free/Pro/Elite)
   ├─ Feature toggles (admin configurable)
   └─ Rate limiting per user
```

#### Security Measures
- Passwords hashed with bcrypt
- JWTs signed and verified
- OAuth 2.0 flow validation
- SQL injection prevention (SQLAlchemy ORM)
- XSS protection (Jinja2 templates)
- CSRF tokens for state-changing operations
- HTTPS enforcement
- Secure cookie flags
- Rate limiting on auth endpoints

### 5. Data Flow

#### User Trade Flow
```
Frontend                Backend                Database
   │                      │                       │
   ├─ Create Trade ──────→ trading_routes.py      │
   │                      ├─ Validate input       │
   │                      ├─ Check subscription   │
   │                      ├─ Calculate PnL        │
   │                      └─ Save trade ──────────→ trades table
   │                      │                       │
   ├─ Get Open Trades ───→ trading_routes.py      │
   │                      ├─ Query trades ───────→ Select * from trades
   │                      └─ Format response      │
   │←────── [200 + trades]                        │
   │
   ├─ Close Trade ───────→ trading_routes.py      │
   │                      ├─ Verify ownership     │
   │                      ├─ Calculate final P&L  │
   │                      └─ Update trade ───────→ Update trades
   │←────── [200 success]                         │
```

#### Signal Generation Flow
```
Frontend                Backend                External
   │                      │                       │
   ├─ Generate Signal ───→ signal_routes.py       │
   │                      ├─ signal_service.py    │
   │                      │  ├─ Fetch prices ────→ Angel One API
   │                      │  ├─ Technical analysis│ ←─ [OHLC data]
   │                      │  ├─ Options analysis  │
   │                      │  ├─ AI insights       │
   │                      │  └─ Generate signal   │
   │                      └─ Save signal ────────→ signals table
   │←────── [200 + signal]                        │
```

#### Subscription Flow
```
User                 Frontend            Backend              Stripe
 │                      │                  │                   │
 ├─ Select Plan ───────→ Settings page     │                   │
 │                      ├─ Submit upgrade ─→ subscription_routes.py
 │                      │                  ├─ Create charge ───→ Create Payment Intent
 │                      │                  │                   │
 │←──────────────────────────────────────────← [Redirect to Stripe]
 │
 ├─ Complete Payment ──────────────────────────────────────────→ Stripe
 │                                                              │
 │←─────── [Webhook: payment.success] ──────────────────────────┤
 │                                         ↓                    │
 │                      ← Update subscription ────── [Success]
 │
 │←───── [Redirect to dashboard]
```

### 6. External Integrations

#### Angel One SmartAPI
```
Purpose: Live market data, options chain, historical candles
Usage: 
├─ Fetch NIFTY/BANKNIFTY prices
├─ Get options chain for Greeks
├─ Historical data for backtesting
└─ Graceful fallback to simulator if unavailable

Data Points:
├─ Symbol: NSE:NIFTY50, NSE:BANKNIFTY
├─ Price, High, Low, Volume
├─ Bid-Ask, Greeks (IV, Theta, etc)
└─ Expiry dates for options
```

#### Stripe Integration
```
Purpose: Payment processing for subscriptions
Usage:
├─ Create payment intents
├─ Handle webhooks (charge.succeeded)
├─ Issue invoices
├─ Manage customer subscriptions
└─ Handle refunds

Flow:
1. User selects plan
2. Backend creates PaymentIntent
3. Frontend redirects to Stripe Checkout
4. Stripe sends webhook on success
5. Backend updates subscription
6. User redirected to dashboard
```

#### SendGrid Email Service
```
Purpose: Transactional and notification emails
Templates:
├─ Welcome email (new user)
├─ Password reset
├─ Trade confirmation
├─ Signal notification
├─ Invoice/receipt
├─ Subscription renewal reminder
└─ Security alerts

Schedule:
├─ Real-time (trade/signal)
├─ Scheduled (daily summary)
└─ Triggered (account events)
```

---

## Performance & Scalability

### Database Optimization
- Indexes on frequently queried columns
- Connection pooling (SQLAlchemy)
- Read replicas for analytics
- Caching layer (Redis)
- Query optimization

### API Optimization
- Rate limiting (per user/IP)
- Response compression (gzip)
- Pagination for large datasets
- Async processing for heavy tasks
- CDN for static assets

### Frontend Optimization
- Lazy loading of images
- Minified CSS/JS
- Browser caching headers
- Code splitting (if bundled)
- Responsive design reduces data transfer

### Load Handling
```
Expected Traffic:
├─ Users: 10K (year 1)
├─ Daily Active: 2K
├─ Concurrent: 100
├─ API calls/day: 1M+
└─ Database queries/day: 5M+

Scaling Strategy:
├─ Load balancer (horizontal scaling)
├─ API server replicas (Gunicorn workers)
├─ Database replication
├─ Cache layer (Redis)
├─ Message queue (async tasks)
└─ CDN for static content
```

---

## Monitoring & Logging

### Health Checks
```
/api/health/
├─ API Server status
├─ Database connectivity
├─ Cache (Redis) status
├─ External services (Angel One, Stripe, SendGrid)
├─ Uptime metrics
└─ Response time averages
```

### Logging Strategy
```
Levels:
├─ ERROR: Failed operations, exceptions
├─ WARNING: Retry attempts, resource limits
├─ INFO: Normal operations, logins
└─ DEBUG: Detailed trace data

Destinations:
├─ Application logs (stdout/stderr)
├─ Audit logs (database)
├─ Error tracking (Sentry, optional)
└─ Analytics (metrics)

Retention:
├─ Application: 7 days
├─ Audit: 90 days (compliance)
└─ Metrics: 30 days
```

### Monitoring Metrics
```
Application:
├─ Request count
├─ Response time (p50, p95, p99)
├─ Error rate
├─ Cache hit rate
└─ Database query time

Business:
├─ Active users
├─ Revenue
├─ Churn rate
├─ Trade volume
└─ Signal accuracy
```

---

## Deployment Architecture

### Development
```
Local Machine
├─ Python venv
├─ SQLite database
├─ .env with test credentials
└─ Flask development server
```

### Staging
```
Railway (staging environment)
├─ PostgreSQL database (staging)
├─ Environment variables
├─ Gunicorn 2 workers
└─ Health checks enabled
```

### Production
```
Railway (production backend)
├─ PostgreSQL database (production)
├─ Gunicorn 4 workers
├─ Environment variables (secrets)
├─ Auto-scaling enabled
└─ Health checks + monitoring

Vercel (production frontend)
├─ Static site hosting
├─ CDN distribution
├─ API proxy to Railway
├─ Environment variables
└─ CI/CD on git push
```

---

## Security Architecture

### Application Security
```
Input Validation
├─ Email format
├─ Password strength
├─ Trade parameters
└─ Signal validation

Data Protection
├─ Encryption at rest (DB)
├─ Encryption in transit (HTTPS)
├─ Hashed passwords (bcrypt)
└─ No hardcoded secrets

Access Control
├─ JWT token verification
├─ Role-based endpoint protection
├─ Subscription-based feature gating
└─ Rate limiting
```

### API Security
```
Authentication
├─ OAuth 2.0 (Google)
├─ JWT tokens
└─ API key pairs

Authorization
├─ Role checking (@require_admin)
├─ Subscription checking (@require_subscription)
├─ User ownership validation
└─ Rate limiting per endpoint
```

---

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | HTML5/CSS3/JS | User interface |
| **Backend** | Flask + Python | API server |
| **Database** | PostgreSQL | Data persistence |
| **Auth** | JWT + Google OAuth | User authentication |
| **Payments** | Stripe API | Subscription billing |
| **Email** | SendGrid API | Email notifications |
| **Market Data** | Angel One SmartAPI | Live prices |
| **Deployment** | Railway + Vercel | Cloud hosting |
| **Monitoring** | Health endpoints | System status |

---

**Architecture Document Complete**  
**Last Updated:** June 23, 2026  
**Status:** PRODUCTION READY
