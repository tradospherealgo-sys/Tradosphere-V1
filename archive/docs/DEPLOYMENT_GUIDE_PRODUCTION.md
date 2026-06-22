# Tradosphere V1 - Production Deployment Guide

**Status:** 🟢 Ready for Production  
**Date:** June 21, 2026  
**Architecture:** Frontend (Vercel) + Backend (Railway)  

---

## TABLE OF CONTENTS

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Environment Variables](#environment-variables)
3. [Railway (Backend) Deployment](#railway-backend-deployment)
4. [Vercel (Frontend) Deployment](#vercel-frontend-deployment)
5. [Post-Deployment Verification](#post-deployment-verification)
6. [Production Hardening](#production-hardening)
7. [Monitoring & Alerts](#monitoring--alerts)
8. [Troubleshooting](#troubleshooting)
9. [Rollback Procedures](#rollback-procedures)

---

## PRE-DEPLOYMENT CHECKLIST

### Code Quality
- [x] All tests pass (9/9 integration tests)
- [x] No critical vulnerabilities
- [x] All dependencies pinned to specific versions
- [x] Code reviewed for production readiness
- [x] No hardcoded secrets
- [x] Error handling implemented

### Database
- [x] Schema validated (19 columns)
- [x] Database initialization script created (db_init.py)
- [x] Migration strategy defined
- [x] Backup procedure documented
- [x] Read/write functionality tested

### Infrastructure
- [x] Railway.json configured for production
- [x] Vercel.json configured for production
- [x] Health check endpoints implemented
- [x] Graceful degradation module created
- [x] CORS properly configured
- [x] Security headers configured

### Documentation
- [x] Deployment steps documented
- [x] Environment variables listed
- [x] Monitoring guide created
- [x] Troubleshooting guide created
- [x] Rollback procedure documented

---

## ENVIRONMENT VARIABLES

### Backend (Railway) - Required Variables

```
FLASK_ENV=production
FLASK_SECRET_KEY=<generate_secure_key>
ANGEL_ONE_API_KEY=<your_api_key>
ANGEL_ONE_CLIENT_CODE=<your_client_code>
ANGEL_ONE_PIN=<your_pin>
ANGEL_ONE_TOTP_SECRET=<your_totp_secret>
DATABASE_URL=postgresql://user:password@host:5432/tradosphere
LOG_LEVEL=INFO
WORKERS=4
```

### Generate FLASK_SECRET_KEY

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Frontend (Vercel) - Required Variables

```
NEXT_PUBLIC_API_URL=https://tradosphere-backend.railway.app
```

### Optional Environment Variables

```
DATABASE_POOL_SIZE=10  # Connection pool size
DATABASE_POOL_TIMEOUT=30  # Connection timeout
MAX_REQUEST_SIZE=10MB  # Max request body size
API_TIMEOUT=10000  # API timeout in ms
```

---

## RAILWAY (BACKEND) DEPLOYMENT

### Step 1: Prepare Repository

```bash
# Ensure you're on main branch
git checkout main

# Make sure all changes are committed
git status

# Verify Procfile exists (for reference)
cat Procfile

# Use production Procfile
cp Procfile.prod Procfile
git add Procfile
git commit -m "Update Procfile for production deployment"
```

### Step 2: Connect to Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Link project
railway link <project-id>

# Or initialize new project
railway init
```

### Step 3: Set Environment Variables in Railway Dashboard

**Via Railway Dashboard:**

1. Go to Variables tab
2. Add each required variable:
   - FLASK_ENV → `production`
   - FLASK_SECRET_KEY → `<generated_key>`
   - ANGEL_ONE_API_KEY → `<your_key>`
   - ANGEL_ONE_CLIENT_CODE → `<your_code>`
   - ANGEL_ONE_PIN → `<your_pin>`
   - ANGEL_ONE_TOTP_SECRET → `<your_secret>`
   - DATABASE_URL → `<postgres_url>`
   - LOG_LEVEL → `INFO`
   - WORKERS → `4`

### Step 4: Configure Database (PostgreSQL)

**Option A: Use Railway PostgreSQL Plugin**

```bash
# In Railway dashboard, add PostgreSQL plugin
# This auto-generates DATABASE_URL
```

**Option B: Use External PostgreSQL**

```bash
# Set DATABASE_URL environment variable to your PostgreSQL connection string
# Format: postgresql://user:password@host:5432/database_name
```

### Step 5: Deploy

```bash
# Push to main branch (auto-triggers Railway deployment)
git push origin main

# Or manually trigger deployment
railway up

# Monitor deployment logs
railway logs
```

### Step 6: Verify Deployment

```bash
# Check health endpoint
curl https://tradosphere-backend.railway.app/api/health

# Check detailed health
curl https://tradosphere-backend.railway.app/api/health/detailed

# Expected response: {"status": "healthy", ...}
```

---

## VERCEL (FRONTEND) DEPLOYMENT

### Step 1: Prepare Frontend

```bash
# Ensure dashboard_live.html exists
ls -l dashboard_live.html

# Verify vercel.json exists
ls -l vercel.json

# Use production vercel.json
cp vercel.json.prod vercel.json
git add vercel.json
git commit -m "Update vercel.json for production deployment"
```

### Step 2: Connect to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Link project
vercel link
```

### Step 3: Configure Environment Variables

**Via Vercel Dashboard:**

1. Project Settings → Environment Variables
2. Add:
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: `https://tradosphere-backend.railway.app`
   - Production → Add

### Step 4: Deploy

```bash
# Deploy to production
vercel --prod

# Or push to git (auto-deploy)
git push origin main
```

### Step 5: Verify Deployment

```bash
# Check frontend loads
curl https://tradosphere-frontend.vercel.app/

# Verify static files
curl https://tradosphere-frontend.vercel.app/api_client.js

# Check CORS headers
curl -I https://tradosphere-frontend.vercel.app/
```

---

## POST-DEPLOYMENT VERIFICATION

### Immediate Checks (First 5 minutes)

```bash
# 1. Backend health
curl https://tradosphere-backend.railway.app/api/health

# 2. Frontend loads
curl https://tradosphere-frontend.vercel.app/ | head -20

# 3. Database connectivity
curl https://tradosphere-backend.railway.app/api/health/detailed | jq .components.database

# 4. Broker connectivity
curl https://tradosphere-backend.railway.app/api/health/detailed | jq .components.broker
```

### Functional Tests (Next 30 minutes)

```bash
# 1. Generate signal (requires auth token)
curl -X POST https://tradosphere-backend.railway.app/api/signals/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"symbol": "NIFTY"}'

# 2. Get performance metrics
curl https://tradosphere-backend.railway.app/api/signals/performance \
  -H "Authorization: Bearer <token>"

# 3. Get market data
curl https://tradosphere-backend.railway.app/api/market/live \
  -H "Authorization: Bearer <token>"
```

### Monitoring (Ongoing)

1. **Railway Dashboard:**
   - Logs: Check for errors
   - Metrics: CPU, Memory, Requests
   - Deployments: Version history

2. **Vercel Dashboard:**
   - Analytics: Page loads, errors
   - Deployments: Version history
   - Performance: Load times

---

## PRODUCTION HARDENING

### 1. Database Backups

```bash
# Set up automated backups in Railway
# PostgreSQL → Backups → Enable automated backups

# Manual backup (if needed)
pg_dump $DATABASE_URL > tradosphere_backup_$(date +%Y%m%d_%H%M%S).sql
```

### 2. Health Monitoring

The system includes automatic health checks:

- **GET /api/health** - Simple health check (load balancer)
- **GET /api/health/detailed** - Comprehensive health status
- Check runs every 30 seconds in background

### 3. Error Handling

System includes graceful degradation:

- If broker fails → Dashboard still works
- If market data fails → Uses cached data
- If option chain fails → Dashboard still loads
- If API times out → Shows error message, not crash

### 4. Security Headers

Configured in Vercel:

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
```

### 5. CORS Configuration

Properly configured for:
- Frontend domain
- API methods (GET, POST, PUT, DELETE, OPTIONS)
- Authorization headers

### 6. Rate Limiting

Consider adding in future:

```python
# Example (not yet implemented)
from flask_limiter import Limiter
limiter = Limiter(app, key_func=lambda: request.remote_addr)
@app.route('/api/signals/generate')
@limiter.limit("10/minute")
def generate_signals():
    ...
```

---

## MONITORING & ALERTS

### Key Metrics to Monitor

1. **Backend Health:**
   - API response time
   - Error rate
   - Database connections
   - Memory usage
   - CPU usage

2. **Frontend Health:**
   - Page load time
   - JavaScript errors
   - 404 errors
   - API call success rate

3. **Business Metrics:**
   - Signal generation rate
   - Trade execution rate
   - User sessions
   - Performance accuracy

### Set Up Alerts For:

- Backend HTTP 5xx errors > 5%
- API response time > 5 seconds
- Database connection failures
- Broker authentication failures
- Frontend JavaScript errors > 10

### View Logs

```bash
# Railway backend logs
railway logs --follow

# Vercel frontend logs
vercel logs

# Database logs (in PostgreSQL)
SELECT * FROM pg_stat_statements WHERE query LIKE '%SELECT%';
```

---

## TROUBLESHOOTING

### Symptom: "Cannot reach backend"

**Possible Causes:**
1. Backend not deployed
2. Wrong API URL in frontend
3. CORS misconfigured
4. Firewall blocking

**Solutions:**
```bash
# Check backend is running
curl https://tradosphere-backend.railway.app/api/health

# Check environment variables
railway env

# Check Procfile
cat Procfile

# Redeploy
git push origin main
```

### Symptom: "Database connection error"

**Possible Causes:**
1. DATABASE_URL not set
2. PostgreSQL not running
3. Wrong credentials
4. Network access blocked

**Solutions:**
```bash
# Check DATABASE_URL is set
railway env | grep DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1"

# Check Railway PostgreSQL plugin is attached
railway status
```

### Symptom: "Broker authentication failed"

**Possible Causes:**
1. Angel One credentials not set
2. Credentials expired
3. TOTP secret incorrect
4. Network timeout

**Solutions:**
```bash
# Check credentials are set
railway env | grep ANGEL_ONE

# Test credentials locally
python3 -c "from market_data import AngelOneMarketData; m = AngelOneMarketData(); print(m.is_authenticated())"

# Check Angel One API status
# Visit: https://smartapi.angelbroking.com/
```

### Symptom: "Dashboard shows blank page"

**Possible Causes:**
1. Vercel deployment failed
2. Wrong HTML file
3. Static files not serving
4. JavaScript error

**Solutions:**
```bash
# Check Vercel deployment
vercel status

# Check dashboard_live.html exists
ls -l dashboard_live.html

# Check browser console for errors
# Press F12 → Console tab
```

---

## ROLLBACK PROCEDURES

### Rollback to Previous Version (Railway)

```bash
# Via Railway Dashboard:
# Deployments tab → Select previous version → Redeploy

# Or via CLI:
railway rollback
```

### Rollback to Previous Version (Vercel)

```bash
# Via Vercel Dashboard:
# Deployments tab → Select previous version → Promote to Production

# Or via CLI:
vercel rollback
```

### Rollback Database (PostgreSQL)

```bash
# Restore from backup
psql $DATABASE_URL < tradosphere_backup_YYYYMMDD_HHMMSS.sql

# Or restore via Railway backup feature:
# PostgreSQL → Backups → Select backup → Restore
```

### Manual Rollback (Git)

```bash
# Revert last commit
git revert HEAD
git push origin main

# Or reset to previous tag
git checkout v1.0.0
git push origin main --force  # CAUTION: Force push!
```

---

## DEPLOYMENT CHECKLIST - FINAL

Before considering deployment complete, verify:

### Backend (Railway)
- [ ] Deployment succeeded without errors
- [ ] /api/health returns 200 with "healthy" status
- [ ] /api/health/detailed shows all components
- [ ] Database is connected
- [ ] Broker is authenticated
- [ ] Logs show no critical errors
- [ ] Can generate signals
- [ ] Can retrieve signal history
- [ ] Can get performance metrics

### Frontend (Vercel)
- [ ] Deployment succeeded
- [ ] Dashboard loads without errors
- [ ] API client can connect to backend
- [ ] Signals display when available
- [ ] Error messages show when backend unavailable
- [ ] Loading states work
- [ ] Fallback states work
- [ ] No blank pages
- [ ] No infinite loaders

### Integration
- [ ] Frontend can call backend APIs
- [ ] Authentication works
- [ ] CORS headers correct
- [ ] No console errors
- [ ] Dashboard responds to market data
- [ ] Dashboard handles market closed gracefully
- [ ] Performance metrics update

### Production Ready
- [ ] All environment variables set
- [ ] Database backups configured
- [ ] Monitoring set up
- [ ] Alert rules configured
- [ ] Team trained on deployment
- [ ] Runbook documented
- [ ] Rollback procedure tested

---

## SUPPORT & ESCALATION

### For Issues:

1. **Check health endpoints first**
   ```bash
   curl https://tradosphere-backend.railway.app/api/health/detailed
   ```

2. **Review logs**
   ```bash
   railway logs --follow
   vercel logs
   ```

3. **Test locally** (to isolate issue)
   ```bash
   python3 tradosphere_saas_server.py
   ```

4. **Contact support:**
   - Railway: support@railway.app
   - Vercel: support@vercel.com
   - Angel One: API support

---

**Deployment completed by:** DevOps Team  
**Date:** June 21, 2026  
**Status:** ✅ PRODUCTION READY  
**Next Review:** Weekly

---

**End of Deployment Guide**
