# 📚 GITHUB SETUP GUIDE

## Overview
Instructions to push Tradosphere to GitHub and connect to Railway/Vercel deployments.

---

## STEP 1: Create GitHub Repository

### Via GitHub Web
1. Go to https://github.com/new
2. Repository name: `tradosphere`
3. Description: "Real-time trading platform with AI intelligence"
4. Visibility: **Public** (for Railway/Vercel integration)
5. Click "Create repository"

### Get Repository URL
```
https://github.com/YOUR_USERNAME/tradosphere.git
```

---

## STEP 2: Push Code to GitHub

Run these commands:

```bash
# Navigate to project directory
cd /Users/anshhdodia/Desktop/Tradosphere

# Add remote origin
git remote add origin https://github.com/YOUR_USERNAME/tradosphere.git

# Rename main branch to main (if needed)
git branch -M main

# Push code to GitHub
git push -u origin main

# Push tags
git push --tags
```

**Verify**: Go to https://github.com/YOUR_USERNAME/tradosphere and confirm code is there.

---

## STEP 3: Verify .gitignore

Check that sensitive files are NOT in GitHub:

```bash
git status

# These should NOT appear in git:
# ❌ .env
# ❌ *.db
# ❌ api_credentials.json
```

If any sensitive files appear:
```bash
# Remove from git (but keep locally)
git rm --cached .env
git rm --cached *.db
git commit -m "Remove sensitive files from git"
git push
```

---

## STEP 4: GitHub Branch Protection (Optional)

For production safety:

1. Go to GitHub repo → "Settings"
2. Click "Branches"
3. Add rule for "main" branch
4. Enable:
   - ✅ Require pull request reviews
   - ✅ Dismiss stale reviews
   - ✅ Require status checks

---

## STEP 5: Configure Secrets for CI/CD (Optional)

For automated deployments:

1. Go to repo → "Settings" → "Secrets and variables"
2. Click "New repository secret"
3. Add secrets:
   - Name: `RAILWAY_TOKEN`
   - Value: Get from Railway dashboard
   - Name: `VERCEL_TOKEN`
   - Value: Get from Vercel dashboard

---

## Complete Push Commands

Copy and paste these (replace YOUR_USERNAME):

```bash
#!/bin/bash
cd /Users/anshhdodia/Desktop/Tradosphere

# Configure git
git config user.email "deploy@tradosphere.ai"
git config user.name "Tradosphere Deployment"

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/tradosphere.git

# Push to GitHub
git push -u origin main
git push --tags

echo "✅ Code pushed to GitHub!"
echo "Repository: https://github.com/YOUR_USERNAME/tradosphere"
```

---

## Files Tracked in GitHub

### Included (Code & Config)
- ✅ tradosphere_saas_server.py
- ✅ dashboard_live.html
- ✅ database.py
- ✅ market_data.py
- ✅ technical_engine.py
- ✅ signals_engine.py
- ✅ ai_analysis_engine.py
- ✅ requirements.txt
- ✅ Procfile
- ✅ runtime.txt
- ✅ railway.json
- ✅ vercel.json
- ✅ .gitignore
- ✅ .env.example (non-secret template)
- ✅ Documentation files

### Excluded (Sensitive)
- ❌ .env (actual secrets)
- ❌ *.db (database files)
- ❌ api_credentials.json
- ❌ __pycache__/ (compiled Python)
- ❌ *.log (log files)
- ❌ venv/ (virtual environment)

---

## Verify GitHub Setup

After pushing:

```bash
# Check remote is configured
git remote -v

# Should show:
# origin  https://github.com/YOUR_USERNAME/tradosphere.git (fetch)
# origin  https://github.com/YOUR_USERNAME/tradosphere.git (push)

# Check tags are pushed
git tag -l

# Should show:
# phase6-stable
```

---

## GitHub URL Reference

After setup, use this URL for Railway/Vercel:

```
https://github.com/YOUR_USERNAME/tradosphere.git
```

For Railway deployment:
```
Platform: GitHub
Owner: YOUR_USERNAME
Repo: tradosphere
Branch: main
```

For Vercel deployment:
```
Framework: Other
Root Directory: (leave empty)
Build Command: (leave empty)
Output Directory: (leave empty)
```

---

## Troubleshooting

### Remote already exists
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/tradosphere.git
```

### Permission denied
```bash
# Use SSH instead (if SSH key configured)
git remote set-url origin git@github.com:YOUR_USERNAME/tradosphere.git
```

### Push failed
```bash
# Pull latest and retry
git pull origin main
git push -u origin main
```

---

## Next Steps

Once GitHub is set up:
1. Go to RAILWAY_SETUP.md for backend deployment
2. Go to VERCEL_SETUP.md for frontend deployment
