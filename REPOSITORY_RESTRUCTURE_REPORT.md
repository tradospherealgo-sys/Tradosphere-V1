# REPOSITORY RESTRUCTURE REPORT
## Tradosphere V1 - Production Preparation

**Date:** June 23, 2026  
**Phase:** Complete Repository Restructuring  
**Status:** PLANNING & ANALYSIS

---

## CURRENT STATE ANALYSIS

### File Inventory
```
Total Files: 38 (non-archive)
  - Python modules: 32
  - HTML templates: 3
  - JSON configs: 3

Total Size: ~10MB (mostly database + logs)
```

### Current Structure (Unorganized)

```
/tradosphere_github/
├── PYTHON MODULES (root, not organized)
│   ├── Core: tradosphere_saas_server.py
│   ├── Routes: auth_routes.py, user_routes.py, billing_routes.py, etc.
│   ├── Models: database.py, user_model.py, subscription_model.py, etc.
│   ├── Engines: signal_writer.py, technical_engine.py, market_data.py, etc.
│   └── [NO FOLDER ORGANIZATION]
│
├── HTML TEMPLATES (root, not organized)
│   ├── login_simple.html
│   ├── saas_auth_pages.html
│   ├── dashboard_live.html
│   └── [MISSING: 5 dashboard variants]
│
├── CONFIGS (root)
│   ├── requirements.txt
│   ├── railway.json
│   ├── vercel.json
│   ├── Procfile
│   ├── runtime.txt
│   └── .env
│
├── DATA
│   ├── tradosphere.db
│   └── tradosphere_saas.db
│
├── LOGS
│   └── (logs)
│
└── ARCHIVE/ (well organized but not in production)
    ├── development/
    ├── tests/
    ├── legacy/
    ├── dashboards/
    ├── docs/
    └── ...
```

**Problem:** Everything is in root directory. Not scalable, unprofessional, hard to navigate.

---

## REQUIRED PRODUCTION STRUCTURE

### Target Architecture

```
/tradosphere_github/
│
├── README.md                                    (Project overview)
├── DEPLOYMENT_GUIDE.md                         (For operators)
├── ARCHITECTURE.md                             (For developers)
│
├── /config/                                    (Configuration)
│   ├── requirements.txt                        (Python dependencies)
│   ├── .env.example                            (Template)
│   ├── .env.production                         (Secrets management)
│   ├── gunicorn.conf.py                        (Gunicorn config)
│   ├── railway.json                            (Railway config)
│   ├── vercel.json                             (Vercel config)
│   ├── Procfile                                (Process file)
│   └── runtime.txt                             (Python version)
│
├── /backend/                                   (Flask application)
│   ├── __init__.py                             (Package init)
│   ├── app.py                                  (Flask app factory)
│   │
│   ├── /routes/                                (API endpoints)
│   │   ├── auth.py                             (Authentication)
│   │   ├── user.py                             (User management)
│   │   ├── admin.py                            (Admin endpoints)
│   │   ├── trading.py                          (Trading operations)
│   │   ├── signals.py                          (Signal generation)
│   │   ├── market.py                           (Market data)
│   │   ├── billing.py                          (Subscriptions)
│   │   ├── backtest.py                         (Backtesting)
│   │   ├── leads.py                            (Lead management)
│   │   └── health.py                           (Health checks)
│   │
│   ├── /models/                                (Database ORM)
│   │   ├── user.py                             (User model)
│   │   ├── signal.py                           (Signal model)
│   │   ├── trade.py                            (Trade model)
│   │   ├── subscription.py                     (Subscription model)
│   │   ├── lead.py                             (Lead model)
│   │   ├── session.py                          (Session model)
│   │   └── __init__.py                         (Init DB)
│   │
│   ├── /services/                              (Business logic)
│   │   ├── auth_service.py                     (Auth logic)
│   │   ├── signal_service.py                   (Signal generation wrapper)
│   │   ├── market_service.py                   (Market data wrapper)
│   │   ├── trading_service.py                  (Paper trading logic)
│   │   ├── subscription_service.py             (Billing logic)
│   │   ├── email_service.py                    (Email notifications)
│   │   ├── backtest_service.py                 (Backtesting service)
│   │   └── admin_service.py                    (Admin operations)
│   │
│   ├── /engines/                               (Analysis engines)
│   │   ├── signal_engine.py                    (System B signals)
│   │   ├── technical_engine.py                 (Technical analysis)
│   │   ├── options_engine.py                   (Options analysis)
│   │   ├── ai_engine.py                        (AI analysis)
│   │   ├── backtest_engine.py                  (Backtesting)
│   │   ├── market_data.py                      (Angel One integration)
│   │   └── market_simulator.py                 (Fallback simulator)
│   │
│   ├── /middleware/                            (Request handling)
│   │   ├── auth.py                             (Auth middleware)
│   │   ├── multi_tenant.py                     (Multi-tenancy)
│   │   ├── error_handler.py                    (Error handling)
│   │   ├── cors.py                             (CORS config)
│   │   └── logging.py                          (Request logging)
│   │
│   ├── /utils/                                 (Utilities)
│   │   ├── validators.py                       (Input validation)
│   │   ├── helpers.py                          (Helper functions)
│   │   ├── constants.py                        (Constants)
│   │   ├── decorators.py                       (Custom decorators)
│   │   └── cache.py                            (Caching)
│   │
│   └── /legacy/                                (Protected algo trading bot)
│       ├── algo_trader/                        (DO NOT MODIFY)
│       ├── bot_monitor.py                      (DO NOT MODIFY)
│       ├── signal_writer.py                    (Original, preserve)
│       └── [All original files preserved]
│
├── /frontend/                                  (Web UI)
│   ├── /public/                                (Static assets)
│   │   ├── index.html                          (Entry point)
│   │   ├── /css/                               (Stylesheets)
│   │   ├── /js/                                (JavaScript)
│   │   └── /img/                               (Images)
│   │
│   ├── /user/                                  (User platform)
│   │   ├── dashboard.html                      (Main dashboard)
│   │   ├── signals.html                        (Signal display)
│   │   ├── trading.html                        (Paper trading)
│   │   ├── portfolio.html                      (Portfolio view)
│   │   ├── market.html                         (Market data)
│   │   ├── subscription.html                   (Subscription mgmt)
│   │   ├── settings.html                       (User settings)
│   │   ├── profile.html                        (User profile)
│   │   └── /css/, /js/                         (UI assets)
│   │
│   ├── /admin/                                 (Admin platform)
│   │   ├── dashboard.html                      (Admin overview)
│   │   ├── users.html                          (User management)
│   │   ├── subscriptions.html                  (Subscription mgmt)
│   │   ├── analytics.html                      (Analytics)
│   │   ├── signals.html                        (Signal monitoring)
│   │   ├── health.html                         (System health)
│   │   ├── settings.html                       (Admin settings)
│   │   └── /css/, /js/                         (UI assets)
│   │
│   ├── /auth/                                  (Auth pages)
│   │   ├── login.html                          (Login page)
│   │   ├── signup.html                         (Signup page)
│   │   └── /css/, /js/                         (Auth assets)
│   │
│   ├── /components/                            (Reusable UI)
│   │   ├── navbar.html                         (Navigation)
│   │   ├── charts.html                         (Charting)
│   │   ├── tables.html                         (Data tables)
│   │   ├── forms.html                          (Form elements)
│   │   └── modals.html                         (Modal dialogs)
│   │
│   ├── /assets/                                (Shared assets)
│   │   ├── /css/base.css                       (Base styles)
│   │   ├── /css/responsive.css                 (Responsive design)
│   │   ├── /js/api.js                          (API client)
│   │   ├── /js/utils.js                        (Utilities)
│   │   ├── /js/auth.js                         (Auth handling)
│   │   └── /fonts/, /icons/                    (Resources)
│   │
│   └── vercel.json                             (Vercel config)
│
├── /database/                                  (Database)
│   ├── migrations/                             (DB migrations)
│   │   ├── 001_init_schema.sql                 (Initial schema)
│   │   ├── 002_add_roles.sql                   (Add roles)
│   │   └── 003_add_indexes.sql                 (Add indexes)
│   │
│   ├── seeds/                                  (Test data)
│   │   ├── users.sql                           (Sample users)
│   │   ├── signals.sql                         (Sample signals)
│   │   └── subscriptions.sql                   (Sample subscriptions)
│   │
│   ├── *.db                                    (SQLite files)
│   └── backups/                                (Database backups)
│
├── /tests/                                     (Test suite)
│   ├── unit/                                   (Unit tests)
│   │   ├── test_auth.py
│   │   ├── test_trading.py
│   │   └── ...
│   │
│   ├── integration/                            (Integration tests)
│   │   ├── test_api.py
│   │   ├── test_workflows.py
│   │   └── ...
│   │
│   └── e2e/                                    (End-to-end tests)
│       ├── test_user_flow.py
│       ├── test_admin_flow.py
│       └── ...
│
├── /scripts/                                   (Utility scripts)
│   ├── setup.py                                (Initial setup)
│   ├── migrate.py                              (Run migrations)
│   ├── seed.py                                 (Seed test data)
│   ├── deploy.py                               (Deployment script)
│   └── backup.py                               (Backup script)
│
├── /docs/                                      (Documentation)
│   ├── API.md                                  (API documentation)
│   ├── SETUP.md                                (Setup guide)
│   ├── ARCHITECTURE.md                         (Architecture)
│   ├── DEPLOYMENT.md                           (Deployment guide)
│   ├── USER_GUIDE.md                           (User guide)
│   └── ADMIN_GUIDE.md                          (Admin guide)
│
├── /logs/                                      (Application logs)
│   ├── app.log
│   ├── error.log
│   └── access.log
│
├── /legacy_archive/                            (Protected archive)
│   └── [Original algo trading bot files]
│
├── .env                                        (Development env)
├── .env.example                                (Template)
├── .gitignore                                  (Git ignore)
├── docker-compose.yml                          (Docker config)
├── Dockerfile                                  (Docker image)
├── docker-build.sh                             (Docker build script)
├── README.md                                   (Project overview)
├── LICENSE                                     (License)
└── git log                                     (Clean git history)
```

---

## RESTRUCTURING PLAN

### Phase 1: Create Folder Structure
- [ ] Create /backend/ directory
- [ ] Create /frontend/ directory
- [ ] Create /database/ directory
- [ ] Create /config/ directory
- [ ] Create /tests/ directory
- [ ] Create /scripts/ directory
- [ ] Create /docs/ directory
- [ ] Create /legacy_archive/ for protected files

### Phase 2: Move Backend Files
- [ ] Move all routes to /backend/routes/
- [ ] Move all models to /backend/models/
- [ ] Move all engines to /backend/engines/
- [ ] Move all services to /backend/services/
- [ ] Move middleware to /backend/middleware/
- [ ] Move utils to /backend/utils/
- [ ] Create /backend/legacy/ for algo trading bot (protected)
- [ ] Update all imports to reflect new paths

### Phase 3: Create Frontend Structure
- [ ] Create /frontend/user/ dashboards
- [ ] Create /frontend/admin/ dashboards
- [ ] Create /frontend/auth/ pages
- [ ] Create /frontend/components/ library
- [ ] Create /frontend/assets/ (CSS, JS, fonts)
- [ ] Create /frontend/public/ entry point

### Phase 4: Create Missing Files

#### User Dashboard Files (7 files)
- [ ] /frontend/user/dashboard.html
- [ ] /frontend/user/signals.html
- [ ] /frontend/user/trading.html
- [ ] /frontend/user/portfolio.html
- [ ] /frontend/user/market.html
- [ ] /frontend/user/subscription.html
- [ ] /frontend/user/profile.html

#### Admin Dashboard Files (7 files)
- [ ] /frontend/admin/dashboard.html
- [ ] /frontend/admin/users.html
- [ ] /frontend/admin/subscriptions.html
- [ ] /frontend/admin/analytics.html
- [ ] /frontend/admin/signals.html
- [ ] /frontend/admin/health.html
- [ ] /frontend/admin/settings.html

#### Auth Pages (2 files)
- [ ] /frontend/auth/login.html
- [ ] /frontend/auth/signup.html

#### Components (5 files)
- [ ] /frontend/components/navbar.html
- [ ] /frontend/components/charts.html
- [ ] /frontend/components/tables.html
- [ ] /frontend/components/forms.html
- [ ] /frontend/components/modals.html

#### Backend Services (8 files)
- [ ] /backend/services/signal_service.py
- [ ] /backend/services/market_service.py
- [ ] /backend/services/trading_service.py
- [ ] /backend/services/subscription_service.py
- [ ] /backend/services/email_service.py
- [ ] /backend/services/backtest_service.py
- [ ] /backend/services/admin_service.py
- [ ] /backend/services/auth_service.py

#### Backend Routes (10 files)
- [ ] /backend/routes/__init__.py
- [ ] /backend/routes/auth.py
- [ ] /backend/routes/user.py
- [ ] /backend/routes/admin.py
- [ ] /backend/routes/trading.py
- [ ] /backend/routes/signals.py
- [ ] /backend/routes/market.py
- [ ] /backend/routes/billing.py
- [ ] /backend/routes/backtest.py
- [ ] /backend/routes/health.py

#### Backend Models (7 files)
- [ ] /backend/models/__init__.py
- [ ] /backend/models/user.py
- [ ] /backend/models/signal.py
- [ ] /backend/models/trade.py
- [ ] /backend/models/subscription.py
- [ ] /backend/models/lead.py
- [ ] /backend/models/session.py

#### Backend Utilities (5 files)
- [ ] /backend/utils/validators.py
- [ ] /backend/utils/decorators.py
- [ ] /backend/utils/constants.py
- [ ] /backend/utils/helpers.py
- [ ] /backend/utils/cache.py

#### Frontend Assets (6 files)
- [ ] /frontend/assets/css/base.css
- [ ] /frontend/assets/css/responsive.css
- [ ] /frontend/assets/js/api.js
- [ ] /frontend/assets/js/auth.js
- [ ] /frontend/assets/js/utils.js
- [ ] /frontend/assets/js/charts.js

#### Configuration Files (4 files)
- [ ] /config/.env.production
- [ ] /config/gunicorn.conf.py
- [ ] Database migrations in /database/migrations/

#### Documentation (6 files)
- [ ] /docs/API.md
- [ ] /docs/SETUP.md
- [ ] /docs/ARCHITECTURE.md
- [ ] /docs/DEPLOYMENT.md
- [ ] /docs/USER_GUIDE.md
- [ ] /docs/ADMIN_GUIDE.md

#### Scripts (4 files)
- [ ] /scripts/setup.py
- [ ] /scripts/migrate.py
- [ ] /scripts/seed.py
- [ ] /scripts/deploy.py

---

## FILE ORIGIN MATRIX

### Files to Keep (Root)
- tradosphere_saas_server.py → /backend/app.py (refactor)
- requirements.txt → /config/requirements.txt
- .env → /config/.env
- .gitignore → ./.gitignore

### Files to Move to /backend/
- All route files (32 files)
- All engine files (8 files)
- All model files (7 files)
- All middleware files (5 files)
- All service files (8 files)
- All utility files (5 files)

### Files to Move to /frontend/
- login_simple.html → /frontend/auth/login.html
- saas_auth_pages.html → /frontend/auth/signup.html
- dashboard_live.html → /frontend/user/dashboard.html

### Files to Create (40+ new files)
- User dashboards (7)
- Admin dashboards (7)
- Components (5)
- Frontend assets (6)
- Backend services (8)
- Backend routes (10)
- Backend models (7)
- Utilities (5)
- Configuration (4)
- Documentation (6)
- Scripts (4)

### Files to Archive (Protected)
- All algo trading bot original files
- Original signal_writer.py
- All /algo_trader/ directory
- Move to /legacy_archive/

---

## IMPORT REMAPPING REQUIRED

Current:
```python
from database import init_db, User
from auth_routes import auth_bp
from signal_writer import generate_signals
```

New:
```python
from backend.models import init_db, User
from backend.routes.auth import auth_bp
from backend.services.signal_service import generate_signals
from backend.engines.signal_engine import SignalGenerator
```

---

## PROTECTED FILES (DO NOT MODIFY)

These files must remain untouched:
- /legacy_archive/signal_writer.py
- /legacy_archive/algo_trader/*
- /legacy_archive/bot_monitor.py
- /legacy_archive/trade_recorder.py

Create wrapper services instead:
- /backend/services/signal_service.py (wraps signal_writer)
- /backend/engines/signal_adapter.py (adapts signals for dashboard)

---

## SUMMARY

### Deliverables
- [ ] REPOSITORY_RESTRUCTURE_REPORT.md ← This document
- [ ] PRODUCTION_FILE_MAP.md (File catalog)
- [ ] MISSING_FILES_CREATED.md (Created files log)
- [ ] SYSTEM_ARCHITECTURE.md (Architecture overview)
- [ ] LAUNCH_CHECKLIST.md (Pre-launch verification)

### Total Files to Handle
- Move: 40+ files
- Create: 50+ files
- Organize: 8 directories
- Update: 100+ imports
- Preserve: 15+ algo files

### Estimated Effort
- Restructuring: 2 hours
- File creation: 4 hours
- Import updates: 1 hour
- Testing: 1 hour
- Documentation: 1 hour
- **Total: 9 hours**

---

**Status:** PLANNING COMPLETE  
**Next:** Create folder structure and implement file organization  
**Timeline:** Start immediately after approval

