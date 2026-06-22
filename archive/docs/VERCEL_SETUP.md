# 📦 VERCEL DEPLOYMENT GUIDE

## Overview
Deploy Tradosphere frontend to Vercel - the dashboard HTML interface.

---

## PREREQUISITES

✅ Railway backend deployed (see RAILWAY_SETUP.md)  
✅ GitHub repository set up (see GITHUB_SETUP.md)  
✅ Railway public URL obtained  
✅ vercel.json configured

---

## STEP 1: Create Vercel Account & Project

### 1.1 Sign Up
1. Go to https://vercel.com
2. Click "Sign up with GitHub"
3. Authorize Vercel
4. Complete setup

### 1.2 Import Project
1. Go to Vercel dashboard
2. Click "Add New..." → "Project"
3. Click "Import Git Repository"
4. Select: `YOUR_USERNAME/tradosphere`
5. Click "Import"

---

## STEP 2: Configure Build Settings

Vercel auto-detects settings, but verify:

### Build Settings
```
Framework: Other
Root Directory: (leave empty)
Build Command: (leave empty)
Output Directory: (leave empty)
```

### Environment Variables
Add Railway API URL:

1. Go to project → "Settings" → "Environment Variables"
2. Add variable:
   - Name: `VITE_API_URL`
   - Value: `https://tradosphere-production.up.railway.app`
   - Click "Add"

Replace with your actual Railway URL from previous step.

---

## STEP 3: Deploy

### Automatic Deploy
1. Push to GitHub main branch
2. Vercel auto-builds
3. Auto-deploys when build succeeds
4. No manual action needed

### Manual Deploy
1. In Vercel dashboard
2. Click "Redeploy"
3. Select latest commit
4. Click "Deploy"

---

## STEP 4: Wait for Build

Vercel will:
1. ✅ Clone GitHub repository
2. ✅ Analyze project (detects static HTML)
3. ✅ Deploy files
4. ✅ Assign public URL
5. ✅ Configure routing

Check build status in Vercel dashboard.

---

## STEP 5: Get Public URL

After deployment:
1. In Vercel dashboard
2. Click "Visit"
3. Copy URL (e.g., `https://tradosphere.vercel.app`)

This is your **public frontend URL**.

---

## STEP 6: Test Frontend

Open in browser:
```
https://tradosphere.vercel.app
```

Should see:
- ✅ Login page OR Dashboard (if logged in)
- ✅ All 8 tabs visible
- ✅ No console errors

Test API connection:
1. Open Browser DevTools (F12)
2. Go to Console tab
3. Should see no connection errors
4. Check Network tab - API calls to Railway should work

---

## STEP 7: Verify API Connection

Test in browser console:

```javascript
// Get the API URL
const API = window.location.origin;

// Test health endpoint
fetch(API + '/api/status', {
  headers: { 'Authorization': 'Bearer test' }
})
.then(r => r.json())
.then(d => console.log('API Status:', d))
.catch(e => console.error('API Error:', e));
```

Should return:
```json
{
  "status": "operational",
  "service": "Tradosphere SaaS v3"
}
```

---

## STEP 8: Update Frontend Dashboard

If API URL changed, the frontend needs to know:

The frontend uses:
```javascript
const API = window.location.origin;
```

This reads from environment at runtime. Make sure Vercel environment variables are set.

---

## Important Notes

### Static Files
- dashboard_live.html is served as static file
- All JavaScript runs in browser
- No backend build required on Vercel

### CORS
- vercel.json includes CORS headers for API calls
- Allows frontend to call Railway backend
- Cross-origin requests should work

### Content Delivery
- Vercel auto-caches static files
- Edge nodes distribute globally
- Fast load times worldwide

---

## Deployment Checklist

- [ ] Vercel account created
- [ ] GitHub connected to Vercel
- [ ] Tradosphere project imported
- [ ] Build settings verified
- [ ] Environment variable set:
  - [ ] VITE_API_URL = Railway URL
- [ ] Deployment completed
- [ ] Dashboard loads without errors
- [ ] API calls connect to Railway
- [ ] Public URL working

---

## Troubleshooting

### Build Fails
```
Error: Build step failed

Solution:
1. Check build logs in Vercel dashboard
2. Common cause: Missing files
3. Verify dashboard_live.html exists
4. Push fix to GitHub (auto-redeploy)
```

### API Calls Failing
```
Error: CORS error or 404

Solution:
1. Verify VITE_API_URL in Vercel env vars
2. Check Railway backend is running
3. Test Railway API directly: curl https://railway-url/api/status
4. Check vercel.json CORS settings
```

### Dashboard Not Loading
```
Error: Blank page or 404

Solution:
1. Check build completed in Vercel dashboard
2. Verify deployment shows "Ready"
3. Clear browser cache (Ctrl+Shift+R)
4. Check console for JavaScript errors
```

---

## Performance Tips

### Caching
- Static assets cached globally
- Dashboard HTML served from edge
- Fast load from anywhere

### Monitor
- Vercel Analytics shows page load times
- Monitor in Vercel dashboard
- Optimize if needed

---

## Getting Frontend URL for Users

After successful deployment:

```
Your Frontend URL: https://tradosphere.vercel.app

Share this with users:
- Share URL in browser
- Users can access dashboard
- Login with credentials
- Use trading features
```

---

## Connecting Frontend to Backend

The frontend uses this pattern:

```javascript
// In dashboard_live.html
const API = window.location.origin;  // Get current domain

// API calls automatically use environment variable if set
fetch(API + '/api/market/live', {
  headers: { 'Authorization': `Bearer ${TOKEN}` }
});
```

Since Vercel serves on different domain than Railway:
- Frontend: https://tradosphere.vercel.app
- Backend: https://tradosphere.up.railway.app
- CORS headers in vercel.json allow cross-domain calls

---

## Next Steps

1. ✅ Backend deployed on Railway
2. ✅ Frontend deployed on Vercel
3. ⏳ Test complete end-to-end
4. ⏳ Share with users
