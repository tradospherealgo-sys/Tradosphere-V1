# 🔐 ENVIRONMENT VARIABLES SETUP

## Overview
This document explains all environment variables required for Tradosphere deployment.

---

## Required Variables

### Flask Configuration
```
FLASK_ENV=production
FLASK_SECRET_KEY=<strong_random_key_min_32_chars>
```

### Angel One API Credentials
```
ANGEL_ONE_API_KEY=<your_api_key>
ANGEL_ONE_CLIENT_CODE=<your_client_code>
ANGEL_ONE_PIN=<your_pin>
ANGEL_ONE_TOTP_SECRET=<your_totp_secret>
```

### Database
```
DATABASE_URL=sqlite:///tradosphere.db
```

---

## Where to Set Variables

### Railway.app
1. Go to Railway project dashboard
2. Click "Variables" tab
3. Add each variable from the list above
4. Click "Deploy" to apply changes

### Vercel
1. Go to Vercel project settings
2. Click "Environment Variables"
3. Add API endpoint as environment variable
4. Redeploy project

---

## Variable Details

### FLASK_SECRET_KEY
- **Required**: YES
- **Type**: String (minimum 32 characters)
- **Purpose**: Encrypts session data
- **Generate**: Use Python: `python -c "import secrets; print(secrets.token_hex(32))"`
- **Current Value**: Keep from .env for consistency

### ANGEL_ONE_API_KEY
- **Required**: YES
- **Type**: String
- **Purpose**: Angel One SmartAPI authentication
- **Source**: Angel One broker account settings
- **Current Value**: From existing .env

### ANGEL_ONE_CLIENT_CODE
- **Required**: YES
- **Type**: String
- **Purpose**: Client identification at Angel One
- **Source**: Angel One broker account
- **Current Value**: From existing .env

### ANGEL_ONE_PIN
- **Required**: YES
- **Type**: String
- **Purpose**: PIN authentication for API calls
- **Source**: Angel One broker account
- **Current Value**: From existing .env

### ANGEL_ONE_TOTP_SECRET
- **Required**: YES
- **Type**: String (base32 encoded)
- **Purpose**: Two-factor authentication
- **Source**: Angel One broker account
- **Current Value**: From existing .env

### DATABASE_URL
- **Required**: YES
- **Type**: Connection string
- **Purpose**: Database connection
- **Current Value**: `sqlite:///tradosphere.db`
- **Note**: SQLite data is ephemeral on Railway. For persistence, use PostgreSQL.

---

## Setting Up Variables on Railway

### Method 1: Via Dashboard
```
1. Go to https://railway.app
2. Select "Tradosphere" project
3. Click on deployment
4. Go to "Variables" tab
5. Click "Add Variable"
6. Enter variable name and value
7. Click "Deploy" to apply
```

### Method 2: Via Railway CLI
```bash
# Install Railway CLI (if not installed)
npm install -g @railway/cli

# Login to Railway
railway login

# Set variables
railway variables set FLASK_ENV=production
railway variables set FLASK_SECRET_KEY=<your_secret>
railway variables set ANGEL_ONE_API_KEY=<your_key>
railway variables set ANGEL_ONE_CLIENT_CODE=<your_code>
railway variables set ANGEL_ONE_PIN=<your_pin>
railway variables set ANGEL_ONE_TOTP_SECRET=<your_secret>
railway variables set DATABASE_URL=sqlite:///tradosphere.db

# Deploy
railway deploy
```

---

## Setting Up Variables on Vercel

### Method 1: Via Dashboard
```
1. Go to https://vercel.com
2. Select "Tradosphere" project
3. Go to "Settings" → "Environment Variables"
4. Add variable: VITE_API_URL=https://your-railway-url.up.railway.app
5. Click "Save"
6. Redeploy
```

---

## Security Notes

### DO NOT
- ❌ Commit .env file to GitHub
- ❌ Share credentials in messages
- ❌ Use weak secret keys
- ❌ Hardcode API keys in code

### DO
- ✅ Use .gitignore to exclude .env
- ✅ Set variables in platform dashboards
- ✅ Generate strong FLASK_SECRET_KEY
- ✅ Rotate credentials regularly

---

## Testing Variables

After setting variables on Railway:

```bash
# SSH into Railway container
railway shell

# Check if variables are loaded
env | grep FLASK
env | grep ANGEL_ONE
env | grep DATABASE
```

---

## Variables Checklist

- [ ] FLASK_ENV set to "production"
- [ ] FLASK_SECRET_KEY is strong (32+ chars)
- [ ] ANGEL_ONE_API_KEY from broker
- [ ] ANGEL_ONE_CLIENT_CODE from broker
- [ ] ANGEL_ONE_PIN from broker
- [ ] ANGEL_ONE_TOTP_SECRET from broker
- [ ] DATABASE_URL configured
- [ ] Variables set on Railway dashboard
- [ ] Variables set on Vercel dashboard
- [ ] .env NOT committed to GitHub
