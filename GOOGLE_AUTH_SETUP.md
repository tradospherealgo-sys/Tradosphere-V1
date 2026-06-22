# Google Authentication Setup Guide

## Overview

Tradosphere V1 uses Google Identity Services for secure, passwordless authentication.

## Frontend Setup

### Google Cloud Console Configuration

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create or select a project
3. Enable "Google Identity Services API"
4. Create OAuth 2.0 credentials (Web application)

**Authorized JavaScript origins:**
```
https://tradosphere-v3.vercel.app
https://tradosphere-v3.vercel.app/login
```

**Authorized redirect URIs:**
```
https://tradosphere-v3.vercel.app/dashboard
https://tradosphere-v3.vercel.app/
```

### Frontend Configuration (login_simple.html)

The `login_simple.html` requires:

```html
<div id="g_id_onload"
     data-client_id="YOUR_GOOGLE_CLIENT_ID"
     data-callback="handleCredentialResponse">
</div>
```

**You need to update the `data-client_id` with your Google Client ID.**

Current placeholder:
```html
<div id="g_id_onload"
     data-client_id=""
     data-callback="handleCredentialResponse">
</div>
```

Add your Client ID:
```html
<div id="g_id_onload"
     data-client_id="YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com"
     data-callback="handleCredentialResponse">
</div>
```

## Backend Setup (Railway)

### Environment Variables to Add

Add these to your Railway project environment variables:

| Variable | Value | Notes |
|----------|-------|-------|
| `GOOGLE_CLIENT_ID` | `YOUR_CLIENT_ID.apps.googleusercontent.com` | From Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | `YOUR_CLIENT_SECRET` | Optional, only needed for server-side auth |

### Getting Your Google Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to APIs & Services > Credentials
3. Click Create Credentials > OAuth 2.0 Client ID
4. Select "Web application"
5. Add authorized origins (see Frontend Setup above)
6. Create and copy your credentials

### Current Implementation

The backend (`/api/auth/google` endpoint) currently:

✓ Verifies Google JWT tokens using `google.auth.transport.requests`
✓ Extracts email, name, and profile picture from token
✓ Creates user automatically if not exists
✓ Generates Tradosphere JWT (30-day expiration)
✓ Returns JWT to frontend

**Note:** Currently uses `id_token.verify_oauth2_token()` which validates against Google's public keys.

## Database Schema Changes

The migration adds these columns to the `users` table:

```sql
-- New columns
ALTER TABLE users ADD COLUMN google_id VARCHAR(255) UNIQUE;
ALTER TABLE users ADD COLUMN picture_url VARCHAR(500);
ALTER TABLE users ADD COLUMN name VARCHAR(255);

-- Make password_hash optional
ALTER TABLE users ALTER COLUMN password_hash DROP NOT NULL;

-- Update is_verified for all users
UPDATE users SET is_verified = TRUE;
```

### Running Migration

**Local:**
```bash
python migration_google_auth.py
```

**Railway (via web console):**
```bash
python migration_google_auth.py
```

## JWT Token Details

### Token Structure

After Google authentication, users receive a Tradosphere JWT containing:

```python
{
    'user_id': 123,
    'email': 'user@example.com',
    'name': 'User Name'
}
```

### Token Expiration

- **Expiration:** 30 days
- **Stored in:** Browser localStorage as `access_token`
- **Sent with:** All authenticated API requests in Authorization header

```javascript
Authorization: Bearer <access_token>
```

## User Flow (Complete)

```
1. User visits https://tradosphere-v3.vercel.app/login
   ↓
2. Frontend loads login_simple.html with Google Identity Services
   ↓
3. User clicks "Sign in with Google"
   ↓
4. Google popup appears (Google handles authentication)
   ↓
5. User selects their Google account
   ↓
6. Google returns credential JWT to frontend
   ↓
7. Frontend sends credential to Railway: POST /api/auth/google
   ↓
8. Railway verifies token with Google
   ↓
9. Railway creates user if not exists
   ↓
10. Railway generates Tradosphere JWT
    ↓
11. Frontend stores JWT in localStorage
    ↓
12. Frontend redirects to /dashboard
    ↓
13. Dashboard loads with authenticated user
```

## Security Considerations

✓ Google handles actual authentication (secure)
✓ Backend verifies token with Google's public keys
✓ Passwords never stored or transmitted
✓ JWT expires in 30 days
✓ Token stored in localStorage (accessible to JavaScript)
✓ HTTPS enforced on production

## Troubleshooting

### "Google library not loaded"
- Check that Google Identity Services script is loaded: `<script src="https://accounts.google.com/gsi/client" async defer></script>`
- Verify internet connectivity

### "Invalid Google token"
- Check that Client ID matches between frontend and Google Cloud Console
- Verify token hasn't expired (tokens are short-lived)
- Check origin is in authorized JavaScript origins

### "Users table missing password_hash"
- Run migration: `python migration_google_auth.py`
- Or manually execute SQL from Database Schema Changes section

### User not created on first login
- Check Railway logs for errors
- Verify database connection and migration ran
- Check email field is not null in token response

## Testing

### Local Testing

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables:
   ```bash
   export GOOGLE_CLIENT_ID="YOUR_CLIENT_ID.apps.googleusercontent.com"
   ```

3. Run migration:
   ```bash
   python migration_google_auth.py
   ```

4. Start server:
   ```bash
   python tradosphere_saas_server.py
   ```

5. Visit `http://localhost:3000/login` (or your configured port)

### Production Testing (Railway)

1. Add environment variables to Railway project
2. Deploy code
3. Visit https://tradosphere-v3.vercel.app/login
4. Test Google login flow
5. Verify JWT in browser localStorage
6. Check user created in database

## Files Modified

- `login_simple.html` - Replaced with Google Identity Services
- `auth_routes.py` - Added `/api/auth/google` endpoint
- `user_model.py` - Added google_id, picture_url, name fields
- `requirements.txt` - Added google-auth libraries
- `migration_google_auth.py` - New migration script

## Next Steps

1. Update `data-client_id` in login_simple.html with your Google Client ID
2. Add environment variables to Railway
3. Run migration on production database
4. Deploy code
5. Test complete login flow
6. Monitor logs for any issues

## Support

If you encounter issues:

1. Check Railway logs: `railway logs`
2. Check browser console for errors (F12)
3. Verify Google Cloud Console configuration
4. Ensure all environment variables are set
5. Verify database migration completed

---

**Status:** Ready for deployment ✅
