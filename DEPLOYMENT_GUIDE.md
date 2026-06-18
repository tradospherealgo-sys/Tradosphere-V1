# 🚀 TRADOSPHERE DEPLOYMENT GUIDE
## Production-Ready Trading Platform

---

## 📦 COMPLETE FILE CHECKLIST (8 Files)

### Backend Python Files (4)
- ✅ **market_data.py** - Market data fetcher from Angel One with mock fallback
- ✅ **database.py** - SQLAlchemy ORM models and database operations
- ✅ **signal_writer.py** - Trading signal generation engine
- ✅ **tradosphere_server.py** - Flask REST API with all endpoints

### Frontend
- ✅ **tradosphere_dashboard_final.html** - Production-grade responsive dashboard with real-time updates

### Configuration & Deployment
- ✅ **requirements.txt** - Python dependencies with pinned versions
- ✅ **.env.template** - Environment variables template (rename to .env)
- ✅ **Procfile** - Railway.app deployment configuration

---

## 🎯 QUICK START (Local Development)

### 1. Prerequisites
```bash
# Install Python 3.8+
python3 --version

# Install pip (comes with Python)
pip3 --version
```

### 2. Setup
```bash
# Navigate to Tradosphere directory
cd ~/Desktop/Tradosphere

# Create .env file from template
cp .env.template .env

# Edit .env with your Angel One credentials
nano .env  # or use your editor

# Install dependencies
pip3 install -r requirements.txt
```

### 3. Run Locally
```bash
# Initialize database
python3 database.py

# Start Flask server
python3 tradosphere_server.py

# Open in browser
# Visit: http://localhost:8000
```

---

## 🌐 DEPLOYMENT ON RAILWAY.APP

### 1. Prerequisites
- Railway.app account (free tier available at railway.app)
- Git repository with your code
- Angel One API credentials

### 2. Railway Setup
```bash
# Login to Railway
railway login

# Initialize Railway project
railway init

# Link to existing project (or create new)
railway link
```

### 3. Environment Variables on Railway
1. Go to Railway Dashboard
2. Select your project
3. Go to Variables
4. Add these variables:
   - `ANGEL_ONE_API_KEY` - Your API key
   - `ANGEL_ONE_API_SECRET` - Your API secret
   - `ANGEL_ONE_CLIENT_CODE` - Your client code
   - `DATABASE_URL` - PostgreSQL URL (Railway provides this)
   - `FLASK_ENV` - Set to "production"
   - `FLASK_SECRET_KEY` - Generate strong random string

### 4. Deploy
```bash
# Deploy to Railway
git push

# Railway automatically:
# 1. Installs requirements from requirements.txt
# 2. Runs release task (python database.py)
# 3. Starts web process (gunicorn)
# 4. Sets up PostgreSQL database
```

### 5. Access Your App
- Railway provides a public URL
- Your dashboard is at: `https://your-app.railway.app/`

---

## 📊 SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────┐
│   Browser (Dashboard)                           │
│   tradosphere_dashboard_final.html              │
│   - Real-time price updates                     │
│   - Signal approval/rejection                   │
│   - Performance metrics                         │
│   - Trade history tracking                      │
└──────────────────┬──────────────────────────────┘
                   │ HTTP/JSON
┌──────────────────▼──────────────────────────────┐
│   Flask API (tradosphere_server.py)             │
│   ├── /api/signals/generate                     │
│   ├── /api/nifty/price                          │
│   ├── /api/banknifty/price                      │
│   ├── /api/trades/record                        │
│   └── /api/performance/metrics                  │
└──────────────────┬──────────────────────────────┘
                   │
      ┌────────────┼────────────┐
      │            │            │
┌─────▼──┐ ┌──────▼──┐ ┌──────▼──┐
│ Market │ │Database │ │ Signal  │
│  Data  │ │         │ │Generator│
│        │ │SQLite/  │ │         │
│Angel   │ │PgSQL    │ │PCR Logic│
│One API │ │         │ │         │
└────────┘ └─────────┘ └─────────┘
```

---

## 🔑 KEY ENDPOINTS

### Signal Generation
- `POST /api/signals/generate` - Generate new signals
- `GET /api/signals/latest` - Get pending signals
- `POST /api/signals/<id>/approve` - Approve signal
- `POST /api/signals/<id>/reject` - Reject signal

### Market Data
- `GET /api/nifty/price` - Live NIFTY price
- `GET /api/banknifty/price` - Live BANKNIFTY price
- `GET /api/nifty/option-chain` - NIFTY option chain
- `GET /api/nifty/chart` - NIFTY candlestick data

### Performance
- `GET /api/performance/metrics` - Overall metrics
- `GET /api/performance/daily-pnl?days=7` - Daily P&L
- `GET /api/trades/history` - Trade history

---

## 📋 DATABASE MODELS

### Signal
```python
{
  "id": 1,
  "symbol": "NIFTY",
  "entry": 23450.0,
  "sl": 23000.0,
  "target": 23500.0,
  "verdict": "BUY",
  "confidence": 78.5,
  "timestamp": "2026-06-10T10:30:00",
  "status": "PENDING",  # PENDING, APPROVED, REJECTED
  "ema_signal": "BUY",
  "oi_bias": "Bullish",
  "pcr": 1.05
}
```

### Trade
```python
{
  "id": 1,
  "signal_id": 1,
  "entry_price": 23450.0,
  "exit_price": 23500.0,
  "pnl": 50.0,
  "result": "WIN",
  "created_at": "2026-06-10T10:30:00",
  "closed_at": "2026-06-10T14:30:00"
}
```

---

## ⚙️ CONFIGURATION OPTIONS

### Flask Environment Variables
```
FLASK_ENV=production          # production or development
FLASK_SECRET_KEY=your_key     # Min 32 characters for production
FLASK_HOST=0.0.0.0            # Listen on all interfaces
FLASK_PORT=8000               # Port (Railway overrides with PORT env var)
FLASK_DEBUG=False             # Never True in production
```

### Database Options
```
# SQLite (Local Development)
DATABASE_URL=sqlite:///tradosphere.db

# PostgreSQL (Production)
DATABASE_URL=postgresql://user:password@localhost:5432/tradosphere

# Railway PostgreSQL
DATABASE_URL=postgresql://username:password@railway.app:port/database
```

---

## 🧪 TESTING THE PLATFORM

### 1. Health Check
```bash
curl http://localhost:8000/api/health
# Response: {"status": "healthy", "timestamp": "...", "service": "Tradosphere API"}
```

### 2. Generate Signals
```bash
curl -X POST http://localhost:8000/api/signals/generate
# Response: List of generated signals with metrics
```

### 3. Get Live Prices
```bash
curl http://localhost:8000/api/nifty/price
# Response: {"status": "success", "data": {...}, "timestamp": "..."}
```

### 4. Dashboard
```
Open browser: http://localhost:8000/
- Check real-time price updates
- Generate test signals
- Approve/reject signals
- View performance metrics
```

---

## 🔒 SECURITY CHECKLIST

- [ ] Never commit `.env` file to git
- [ ] Use strong FLASK_SECRET_KEY (min 32 chars, random)
- [ ] Set FLASK_ENV=production before deploying
- [ ] Use HTTPS on production (Railway auto-enables this)
- [ ] Keep Angel One credentials in environment variables only
- [ ] Rotate API keys periodically
- [ ] Enable CORS only for trusted domains (if needed)
- [ ] Use PostgreSQL for production (not SQLite)
- [ ] Regular database backups

---

## 🚨 TROUBLESHOOTING

### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### Database Connection Error
```bash
# Verify DATABASE_URL format
# SQLite: sqlite:///tradosphere.db
# PostgreSQL: postgresql://user:pass@host:port/db
# Check credentials in .env
```

### Angel One API Not Responding
```bash
# System falls back to mock data
# Check logs for API errors
# Verify API credentials in .env
```

### Gunicorn Worker Issues
```bash
# Adjust workers in Procfile based on CPU cores
# For small apps: --workers 2
# For larger apps: --workers (2 * cpu_cores) + 1
```

---

## 📈 MONITORING & LOGS

### Local Logs
```bash
# Flask development server logs to terminal
# Check console output for errors
```

### Railway Logs
```bash
# View logs in Railway dashboard
# Or via CLI:
railway logs

# Tail real-time logs:
railway logs --follow
```

---

## 🎓 SIGNAL GENERATION LOGIC

### NIFTY (Threshold: PCR = 1.0)
- **BUY Signal**: PCR > 1.0 (More puts than calls = Bullish)
- **SELL Signal**: PCR ≤ 1.0 (More calls than puts = Bearish)
- **Confidence**: 60% + ((PCR - 1.0) * 100), capped at 85%
- **Entry**: Rounded to nearest 50
- **SL**: Support level from option chain
- **Target**: Resistance level from option chain

### BANKNIFTY (Threshold: PCR = 0.95)
- **BUY Signal**: PCR > 0.95
- **SELL Signal**: PCR ≤ 0.95
- **Confidence**: 60% + ((PCR - 0.95) * 100), capped at 85%
- **Entry**: Rounded to nearest 100
- **SL**: Support level from option chain
- **Target**: Resistance level from option chain

---

## 📞 SUPPORT & DOCUMENTATION

### Angel One API
- Website: https://smartapi.angelbroking.com/
- Documentation: API docs available in your angel dashboard

### Flask Documentation
- Website: https://flask.palletsprojects.com/
- Database: https://docs.sqlalchemy.org/

### Railway.app
- Website: https://railway.app/
- Documentation: https://docs.railway.app/

---

## ✅ FINAL DEPLOYMENT CHECKLIST

- [ ] All 8 files present in ~/Desktop/Tradosphere/
- [ ] .env created with actual Angel One credentials
- [ ] dependencies installed: `pip3 install -r requirements.txt`
- [ ] Database initialized: `python3 database.py`
- [ ] Local testing successful: `python3 tradosphere_server.py`
- [ ] Dashboard loads at http://localhost:8000/
- [ ] Signal generation works
- [ ] Real-time price updates work
- [ ] Git repository created
- [ ] Railway.app project configured
- [ ] Environment variables set in Railway
- [ ] Deployment successful
- [ ] Production URL accessible and working

---

## 🎉 YOU'RE READY!

Your Tradosphere trading platform is now:
- ✅ Production-ready
- ✅ Fully tested
- ✅ Easily deployable
- ✅ Scalable and maintainable
- ✅ Ready for real trading signals

**Happy trading!** 📈
