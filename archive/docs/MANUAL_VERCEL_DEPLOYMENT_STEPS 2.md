# MANUAL VERCEL DEPLOYMENT STEPS

**Status:** Automatic deployment not detecting GitHub push. Manual intervention required.

## Why This Is Needed

Vercel should auto-deploy on GitHub push, but it's not. The new code (config.js + routing fixes) is on GitHub but not on Vercel production.

**Evidence of problem:**
```bash
curl https://tradosphere-v1.vercel.app/config.js
# Returns: HTML (dashboard_live.html)
# Should return: JavaScript (config.js)

curl https://tradosphere-v1.vercel.app/ | grep "config.js"
# Returns: Nothing (not imported)
# Should return: <script src="config.js"></script>
```

## Solution: Manual Vercel Dashboard Actions

### STEP 1: Verify Vercel Connected to GitHub

1. Go to: https://vercel.com/projects
2. Click "tradosphere-v1" project
3. Settings tab → Git Connected?
4. Should show: "Connected to tradospherealgo-sys/Tradosphere-V1"
5. Branch: main

**If not connected:**
1. Click "Connect Repository"
2. Select: tradospherealgo-sys/Tradosphere-V1
3. Automatic deployments: Enable

### STEP 2: Manually Trigger Deployment

Go to: https://vercel.com/projects/tradosphere-v1

Look for "Deployments" tab → Click "Redeploy" on latest build

OR click "Deploy" button to trigger fresh build

### STEP 3: Set Environment Variables (OPTIONAL - Has Fallback)

Settings → Environment Variables → Add:

```
Name: NEXT_PUBLIC_API_URL
Value: https://tradosphere-v1-production.up.railway.app
Environments: Production, Preview, Development
```

Click "Save" and "Redeploy"

## What Should Happen After Redeployment

1. Vercel builds new code from GitHub
2. Includes config.js in build output
3. Includes updated HTML files with `<script src="config.js"></script>`
4. /config.js endpoint serves JavaScript (not HTML)
5. Dashboard loads and runs config.js
6. API_BASE_URL is set to Railway URL
7. All API calls route to Railway, not Vercel

## Verification Steps After Redeployment

### Check 1: config.js Is Available
```bash
curl https://tradosphere-v1.vercel.app/config.js | head -5
# Should show JavaScript starting with /**
```

### Check 2: Dashboard Imports config.js
```bash
curl https://tradosphere-v1.vercel.app/ | grep "config.js"
# Should show: <script src="config.js"></script>
```

### Check 3: API_BASE_URL Is Set
Open browser console (F12):
```javascript
console.log(API_BASE_URL)
// Should show: https://tradosphere-v1-production.up.railway.app
```

### Check 4: API Requests Go to Railway
F12 → Network tab → Click "Generate Trade Calls" button
Check network requests:
- Should show: POST https://tradosphere-v1-production.up.railway.app/api/generate
- Should NOT show: POST https://tradosphere-v1.vercel.app/api/generate

## Commits Ready to Deploy

```
2293fcb - TRIGGER: Force Vercel rebuild
f70c03d - FIX: Add explicit route for config.js
d6e8149 - PRODUCTION FIX: Deploy frontend → Railway routing
```

All committed to origin/main, ready for Vercel to deploy.

## If Manual Deployment Still Doesn't Work

1. Check Vercel build logs in Deployment tab
2. Look for errors in "Logs" section
3. Verify GitHub repository is public (Vercel can access it)
4. Check if main branch is protected by branch rules that block Vercel
5. Try disconnecting and reconnecting GitHub repo in Settings
