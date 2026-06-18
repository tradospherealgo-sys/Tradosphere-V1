# 🚀 DEPLOYMENT COMMANDS - COPY & PASTE

Complete step-by-step commands to deploy Tradosphere.

---

## PHASE 1: PREPARE GIT & PUSH TO GITHUB

Replace `YOUR_USERNAME` with your GitHub username.

### 1.1 Initialize and Commit (Already Done)
```bash
# Already completed - verify
cd /Users/anshhdodia/Desktop/Tradosphere
git status

# Should show:
# On branch main
# nothing to commit, working tree clean
```

### 1.2 Add GitHub Remote
```bash
cd /Users/anshhdodia/Desktop/Tradosphere

# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/tradosphere.git

# Verify
git remote -v
# Should show:
# origin  https://github.com/YOUR_USERNAME/tradosphere.git (fetch)
# origin  https://github.com/YOUR_USERNAME/tradosphere.git (push)
```

### 1.3 Push to GitHub
```bash
# Push code
git push -u origin main

# Push tags
git push --tags

# Verify at: https://github.com/YOUR_USERNAME/tradosphere
```

**Expected Output**: Code appears in GitHub repository

---

## PHASE 2: DEPLOY BACKEND TO RAILWAY

### 2.1 Create Railway Project
```
Manual Steps (in browser):
1. Go to https://railway.app
2. Click "New Project"
3. Click "Deploy from GitHub"
4. Select: YOUR_USERNAME/tradosphere
5. Click "Deploy"
6. Wait for build to complete (5-10 minutes)
```

### 2.2 Set Environment Variables (in Railway Dashboard)
```
Go to: Railway Dashboard → Variables Tab

Add these variables (get values from local .env file):

FLASK_ENV = production
FLASK_SECRET_KEY = (from .env file, or generate new: python -c "import secrets; print(secrets.token_hex(32))")
ANGEL_ONE_API_KEY = (from .env)
ANGEL_ONE_CLIENT_CODE = (from .env)
ANGEL_ONE_PIN = (from .env)
ANGEL_ONE_TOTP_SECRET = (from .env)
DATABASE_URL = sqlite:///tradosphere.db
```

### 2.3 Verify Backend is Running
```bash
# After Railway build completes, get your Railway URL
# Go to: Railway Dashboard → Click "View" or "Generate Domain"
# URL will be like: https://tradosphere-production.up.railway.app

# Test the backend
RAILWAY_URL="https://tradosphere-production.up.railway.app"

curl $RAILWAY_URL/api/status

# Expected response:
# {"status":"operational","service":"Tradosphere SaaS v3",...}
```

**Important**: Save your Railway URL - you'll need it for Vercel!

---

## PHASE 3: DEPLOY FRONTEND TO VERCEL

### 3.1 Create Vercel Project
```
Manual Steps (in browser):
1. Go to https://vercel.com
2. Click "Add New" → "Project"
3. Click "Import Git Repository"
4. Select: YOUR_USERNAME/tradosphere
5. Click "Import"
6. Configure environment variables (see step 3.2)
7. Click "Deploy"
8. Wait for build (2-3 minutes)
```

### 3.2 Set Vercel Environment Variables
```
In Vercel Dashboard → Settings → Environment Variables

Add this variable:

Name: VITE_API_URL
Value: https://tradosphere-production.up.railway.app
(Replace with your actual Railway URL from Phase 2)

Add for all environments: Development, Preview, Production
```

### 3.3 Verify Frontend is Running
```bash
# After Vercel build completes, get your Vercel URL
# Go to: Vercel Dashboard → Click "Visit"
# URL will be like: https://tradosphere.vercel.app

# Test the frontend
VERCEL_URL="https://tradosphere.vercel.app"

# Open in browser
# Should see login page or dashboard
open $VERCEL_URL

# Check console for errors
# Press F12 → Console tab
# Should see NO errors
```

**Important**: Save your Vercel URL - this is your public frontend!

---

## PHASE 4: TEST END-TO-END

### 4.1 Test Frontend → Backend Connection
```
In Vercel frontend:
1. Open browser DevTools (F12)
2. Go to Console tab
3. Run this command:

fetch('https://tradosphere-production.up.railway.app/api/status', {
  headers: { 'Authorization': 'Bearer test' }
})
.then(r => r.json())
.then(d => console.log('Backend Status:', d))
.catch(e => console.error('Error:', e));

Expected: Shows {"status":"operational",...}
```

### 4.2 Test Dashboard Features
```
In browser:
1. Go to https://tradosphere.vercel.app
2. Check all 8 tabs load:
   ✅ Overview
   ✅ Market
   ✅ Options
   ✅ Technical
   ✅ Signals
   ✅ AI Insights
   ✅ Paper Trading
   ✅ Backtesting

3. Check data is live:
   ✅ Market prices update
   ✅ Options chain visible
   ✅ Technical indicators show
```

### 4.3 Test Login (if needed)
```
1. Try login with test credentials
2. Should see dashboard with data
3. All API calls should work
```

---

## PHASE 5: ENABLE AUTO-DEPLOYMENT

### 5.1 Configure Automatic Deployment
```bash
# After code is on GitHub, deployments are automatic:

# To trigger new deployment:
git add .
git commit -m "Update: [description]"
git push origin main

# Both Railway and Vercel will auto-deploy
# No manual action needed!
```

---

## COMPLETE CHECKLIST

Copy and verify each step:

### GitHub Setup
- [ ] GitHub account created
- [ ] Repository created: https://github.com/YOUR_USERNAME/tradosphere
- [ ] Code pushed to GitHub
- [ ] Tags pushed: `git push --tags`
- [ ] Verify at GitHub: code visible, .env NOT in repo

### Railway Setup
- [ ] Railway account created
- [ ] Project imported from GitHub
- [ ] Build completed successfully
- [ ] Environment variables set (7 variables)
- [ ] Backend responding at: https://tradosphere-production.up.railway.app/api/status
- [ ] Railway URL saved

### Vercel Setup
- [ ] Vercel account created
- [ ] Project imported from GitHub
- [ ] Environment variable VITE_API_URL set to Railway URL
- [ ] Build completed successfully
- [ ] Frontend accessible: https://tradosphere.vercel.app
- [ ] No console errors in browser (F12)

### Testing
- [ ] Frontend loads successfully
- [ ] Dashboard shows all 8 tabs
- [ ] API calls to backend work
- [ ] Live data updating
- [ ] No errors in browser console

---

## IMPORTANT NOTES

### Never Commit Secrets
```bash
# Verify .env is NOT committed
git log --all --full-history -- .env

# Should show: No output (file not in git)
```

### Auto-Deployment
```
After first deployment:
- Every push to GitHub → auto-deploy Railway + Vercel
- No manual steps needed
- Takes 5-10 minutes total
```

### Monitor Deployments
```
Railway: https://railway.app → View Logs
Vercel: https://vercel.com → Deployments tab
```

---

## TROUBLESHOOTING COMMANDS

### Check Git Status
```bash
cd /Users/anshhdodia/Desktop/Tradosphere
git status
git log --oneline
git remote -v
```

### Check Railway Logs
```bash
# In Railway Dashboard → Logs tab
# Or via CLI:
railway shell
env | grep FLASK
env | grep ANGEL_ONE
```

### Check Vercel Build
```bash
# In Vercel Dashboard → Deployments tab
# Click latest deployment to see build logs
```

### Test API Directly
```bash
# Test from command line
curl -X GET "https://tradosphere-production.up.railway.app/api/status" \
  -H "Authorization: Bearer test" \
  -H "Content-Type: application/json"

# Should return JSON response
```

---

## QUICK REFERENCE

| Component | URL | Type |
|-----------|-----|------|
| Frontend | https://tradosphere.vercel.app | Vercel |
| Backend API | https://tradosphere-production.up.railway.app | Railway |
| GitHub | https://github.com/YOUR_USERNAME/tradosphere | Git |
| Railway Dashboard | https://railway.app | Control |
| Vercel Dashboard | https://vercel.com | Control |

---

## FINAL STEP

After all tests pass:

✅ Your Tradosphere is live!

Share this URL with users:
```
https://tradosphere.vercel.app
```

---

## NEED HELP?

For issues, check:
1. ENVIRONMENT_VARIABLES.md - Check all vars are set
2. RAILWAY_SETUP.md - Check backend logs
3. VERCEL_SETUP.md - Check frontend build
4. GITHUB_SETUP.md - Check repo setup
