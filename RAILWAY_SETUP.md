# 🚂 RAILWAY DEPLOYMENT GUIDE

## Overview
Deploy Tradosphere backend to Railway.app - the Flask REST API server.

---

## PREREQUISITES

✅ GitHub repository set up (see GITHUB_SETUP.md)  
✅ Environment variables prepared (see ENVIRONMENT_VARIABLES.md)  
✅ Procfile configured (fixed)  
✅ requirements.txt present

---

## STEP 1: Create Railway Account & Project

### 1.1 Sign Up
1. Go to https://railway.app
2. Click "Sign in with GitHub"
3. Authorize Railway
4. Complete profile setup

### 1.2 Create New Project
1. Click "New Project"
2. Click "Deploy from GitHub"
3. Select repository: `tradosphere`
4. Click "Deploy"

---

## STEP 2: Configure Environment Variables

Railway will detect Procfile and gunicorn automatically.

Add variables manually:

### Via Dashboard
1. Go to project → "Variables" tab
2. Add each variable:

| Variable | Value |
|----------|-------|
| FLASK_ENV | production |
| FLASK_SECRET_KEY | (generate strong key) |
| ANGEL_ONE_API_KEY | (from .env) |
| ANGEL_ONE_CLIENT_CODE | (from .env) |
| ANGEL_ONE_PIN | (from .env) |
| ANGEL_ONE_TOTP_SECRET | (from .env) |
| DATABASE_URL | sqlite:///tradosphere.db |

---

## STEP 3: Deploy

### Automatic Deployment (Recommended)
1. Push code to GitHub (main branch)
2. Railway auto-detects changes
3. Automatically builds and deploys
4. No manual action needed

### Manual Deploy
1. In Railway dashboard
2. Click "Deploy" button
3. Select "Redeploy"

---

## STEP 4: Wait for Build

Railway will:
1. ✅ Clone GitHub repository
2. ✅ Install Python dependencies (from requirements.txt)
3. ✅ Build application
4. ✅ Start gunicorn server
5. ✅ Assign public URL

### Check Build Status
- In Railway dashboard, watch "Logs" tab
- Should see: `Gunicorn workers ready`
- Should see: `127.0.0.1 - - [date] "GET /api/status"...`

---

## STEP 5: Get Public URL

After deployment:
1. In Railway dashboard
2. Click "View" or "Generate URL"
3. Copy URL (e.g., `https://tradosphere-production.up.railway.app`)

This is your **API_URL** for Vercel frontend.

---

## STEP 6: Test API Endpoints

```bash
# Get deployment URL from Railway dashboard
API_URL="https://tradosphere-production.up.railway.app"

# Test health endpoint
curl $API_URL/api/status

# Should return:
# {"status":"operational","service":"Tradosphere SaaS v3",...}
```

---

## STEP 7: View Logs

In Railway dashboard:
1. Click "Logs" tab
2. Watch real-time server logs
3. Check for errors

Common issues:
- ❌ ModuleNotFoundError → Missing in requirements.txt
- ❌ ANGEL_ONE API error → Check credentials
- ❌ Port already in use → Railway handles this

---

## STEP 8: Configure Domain (Optional)

For custom domain:
1. Go to Railway project settings
2. Click "Custom Domain"
3. Add domain (e.g., `api.tradosphere.app`)
4. Update Vercel with new API_URL

---

## Important Notes

### Database
- Current: SQLite (`tradosphere.db`)
- **Note**: Data will be lost when Railway container restarts
- This is OK for demo/testing
- For production: Migrate to PostgreSQL

### Monitoring
- Railway provides logs and metrics
- Monitor in dashboard
- Set up alerts for failures

### Scaling
- For higher traffic: Increase worker count in Procfile
- Current: 4 workers
- Increase if needed: `gunicorn --workers 8 ...`

---

## Deployment Checklist

- [ ] Railway account created
- [ ] GitHub connected to Railway
- [ ] Tradosphere repository imported
- [ ] Environment variables set:
  - [ ] FLASK_ENV
  - [ ] FLASK_SECRET_KEY
  - [ ] ANGEL_ONE_API_KEY
  - [ ] ANGEL_ONE_CLIENT_CODE
  - [ ] ANGEL_ONE_PIN
  - [ ] ANGEL_ONE_TOTP_SECRET
  - [ ] DATABASE_URL
- [ ] Build completed successfully
- [ ] API responding to requests
- [ ] Logs show no errors
- [ ] Public URL obtained

---

## Troubleshooting

### Build Fails
```
Error: ModuleNotFoundError: No module named 'XXX'

Solution: Add to requirements.txt
git add requirements.txt
git commit -m "Add missing dependency"
git push
(Auto-deploy will retry)
```

### API Returning 500 Errors
```
Solution:
1. Check logs in Railway dashboard
2. Verify environment variables
3. Check Angel One credentials
4. Restart deployment
```

### Slow Response Times
```
Solution:
1. Check Railway metrics
2. Increase worker count
3. Check database queries
4. Monitor API logs
```

---

## Getting API URL for Frontend

After successful deployment:

```
Your API URL: https://tradosphere-production.up.railway.app

Use this for:
- VITE_API_URL in Vercel
- Frontend API calls in dashboard_live.html
```

Example in frontend:
```javascript
const API = "https://tradosphere-production.up.railway.app";
```

---

## Next Steps

1. ✅ Backend deployed on Railway
2. ⏳ Update Vercel with API URL
3. ⏳ Deploy frontend to Vercel
4. ⏳ Test end-to-end integration
