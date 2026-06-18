"""
Tradosphere Server - Simple Flask Backend
Mock API endpoints returning sample data
No real business logic yet - UI ready for integration
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import json

app = Flask(__name__)
CORS(app)

# ═══════════════════════════════════════════════════════════════════════════
# MOCK DATA GENERATORS
# ═══════════════════════════════════════════════════════════════════════════

def get_mock_signals():
    """Generate mock signal data"""
    return {
        "status": "success",
        "count": 3,
        "data": [
            {
                "id": 1,
                "symbol": "BANKNIFTY",
                "verdict": "BUY",
                "entry": 54250,
                "target": 55000,
                "sl": 54000,
                "confidence": 78,
                "ema_signal": "BUY",
                "timestamp": datetime.now().isoformat(),
                "status": "PENDING"
            },
            {
                "id": 2,
                "symbol": "NIFTY",
                "verdict": "BUY",
                "entry": 23450,
                "target": 23800,
                "sl": 23000,
                "confidence": 72,
                "ema_signal": "BUY",
                "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat(),
                "status": "PENDING"
            },
            {
                "id": 3,
                "symbol": "FINNIFTY",
                "verdict": "HOLD",
                "entry": 21500,
                "target": 21850,
                "sl": 21200,
                "confidence": 65,
                "ema_signal": "HOLD",
                "timestamp": (datetime.now() - timedelta(minutes=15)).isoformat(),
                "status": "APPROVED"
            }
        ]
    }

def get_mock_trades():
    """Generate mock trade history"""
    return {
        "status": "success",
        "count": 4,
        "data": [
            {
                "id": 1,
                "symbol": "NIFTY",
                "entry_price": 23450,
                "exit_price": 23600,
                "pnl": 150,
                "result": "WIN",
                "date": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "id": 2,
                "symbol": "BANKNIFTY",
                "entry_price": 54100,
                "exit_price": 54300,
                "pnl": 200,
                "result": "WIN",
                "date": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "id": 3,
                "symbol": "NIFTY",
                "entry_price": 23400,
                "exit_price": 23250,
                "pnl": -150,
                "result": "LOSS",
                "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            },
            {
                "id": 4,
                "symbol": "FINNIFTY",
                "entry_price": 21500,
                "exit_price": 21650,
                "pnl": 150,
                "result": "WIN",
                "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            }
        ]
    }

def get_mock_metrics():
    """Generate mock performance metrics"""
    return {
        "status": "success",
        "data": {
            "win_rate": 82.5,
            "total_pnl": 45230,
            "total_signals": 52,
            "total_trades": 30,
            "wins": 25,
            "losses": 5,
            "profit_factor": 3.2,
            "sharpe_ratio": 1.85,
            "max_drawdown": -2.5
        }
    }

def get_mock_prices():
    """Generate mock price data"""
    return {
        "status": "success",
        "data": {
            "NIFTY": {
                "current": 23450.25,
                "change": 234,
                "change_percent": 1.03,
                "bid": 23449.50,
                "ask": 23450.75
            },
            "BANKNIFTY": {
                "current": 54600.50,
                "change": 512,
                "change_percent": 0.95,
                "bid": 54599.75,
                "ask": 54601.25
            },
            "FINNIFTY": {
                "current": 21786.40,
                "change": 198,
                "change_percent": 0.92,
                "bid": 21785.90,
                "ask": 21786.90
            }
        }
    }

def get_mock_option_chain(symbol):
    """Generate mock option chain data"""
    return {
        "status": "success",
        "symbol": symbol,
        "data": {
            "pcr": 1.07,
            "support": 23000 if symbol == "NIFTY" else 54000,
            "resistance": 23500 if symbol == "NIFTY" else 55000,
            "options": [
                {"strike": 22700, "call_oi": 120000, "call_ltp": 245, "put_ltp": 98, "put_oi": 150000},
                {"strike": 22800, "call_oi": 100000, "call_ltp": 182, "put_ltp": 128, "put_oi": 130000},
                {"strike": 22900, "call_oi": 96000, "call_ltp": 128, "put_ltp": 166, "put_oi": 110000},
            ]
        }
    }

# ═══════════════════════════════════════════════════════════════════════════
# ROUTES - SERVING DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    """Serve dashboard"""
    try:
        with open('tradosphere_dashboard_final.html', 'r') as f:
            return f.read()
    except:
        return "Dashboard not found", 404

@app.route('/dashboard')
def dashboard():
    """Serve dashboard (alternative route)"""
    try:
        with open('tradosphere_dashboard_final.html', 'r') as f:
            return f.read()
    except:
        return "Dashboard not found", 404

# ═══════════════════════════════════════════════════════════════════════════
# API ROUTES - MOCK DATA ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/api/signals/latest')
def api_signals_latest():
    """Get latest signals"""
    return jsonify(get_mock_signals())

@app.route('/api/signals/approve/<int:signal_id>', methods=['POST'])
def api_approve_signal(signal_id):
    """Approve a signal"""
    return jsonify({
        "status": "success",
        "message": f"Signal {signal_id} approved",
        "signal_id": signal_id
    })

@app.route('/api/signals/reject/<int:signal_id>', methods=['POST'])
def api_reject_signal(signal_id):
    """Reject a signal"""
    return jsonify({
        "status": "success",
        "message": f"Signal {signal_id} rejected",
        "signal_id": signal_id
    })

@app.route('/api/prices')
def api_prices():
    """Get current prices"""
    return jsonify(get_mock_prices())

@app.route('/api/prices/<symbol>')
def api_price_symbol(symbol):
    """Get price for specific symbol"""
    prices = get_mock_prices()
    if symbol in prices['data']:
        return jsonify({
            "status": "success",
            "symbol": symbol,
            "data": prices['data'][symbol]
        })
    return jsonify({"status": "error", "message": "Symbol not found"}), 404

@app.route('/api/option-chain/<symbol>')
def api_option_chain(symbol):
    """Get option chain for symbol"""
    return jsonify(get_mock_option_chain(symbol))

@app.route('/api/trades/history')
def api_trades_history():
    """Get trade history"""
    return jsonify(get_mock_trades())

@app.route('/api/trades', methods=['POST'])
def api_add_trade():
    """Add new trade"""
    data = request.get_json()
    return jsonify({
        "status": "success",
        "message": "Trade recorded",
        "trade_id": 5,
        "pnl": data.get('exit_price', 0) - data.get('entry_price', 0)
    })

@app.route('/api/metrics')
def api_metrics():
    """Get performance metrics"""
    return jsonify(get_mock_metrics())

@app.route('/api/performance/chart')
def api_performance_chart():
    """Get performance chart data"""
    return jsonify({
        "status": "success",
        "daily_pnl": {
            "2024-06-04": 2000,
            "2024-06-05": 3500,
            "2024-06-06": -1500,
            "2024-06-07": 4200,
            "2024-06-08": 2800,
            "2024-06-09": 3500,
            "2024-06-10": 1230
        }
    })

@app.route('/api/chat/message', methods=['POST'])
def api_chat_message():
    """Chat bot response"""
    data = request.get_json()
    user_message = data.get('message', '')

    responses = {
        "signal": "NIFTY is showing a strong BUY signal with 78% confidence based on EMA crossover.",
        "banknifty": "BANKNIFTY has the best performance this week with 85% win rate.",
        "performance": "Your overall win rate is 82.5% with a total P&L of +₹45,230.",
        "default": "I can help with signal analysis, trading strategies, and performance metrics. What would you like to know?"
    }

    message_lower = user_message.lower()
    response = responses.get("default")
    for key, value in responses.items():
        if key in message_lower:
            response = value
            break

    return jsonify({
        "status": "success",
        "message": response,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/users')
def api_users():
    """Get user list (admin only)"""
    return jsonify({
        "status": "success",
        "count": 127,
        "active_today": 89,
        "data": [
            {"id": "U001", "email": "user@example.com", "status": "Active", "trades": 24},
            {"id": "U002", "email": "trader@example.com", "status": "Active", "trades": 18},
            {"id": "U003", "email": "test@example.com", "status": "Inactive", "trades": 5}
        ]
    })

@app.route('/api/system/status')
def api_system_status():
    """Get system status"""
    return jsonify({
        "status": "success",
        "database": "Connected",
        "signal_writer": "Running",
        "api_server": "Running",
        "last_backup": datetime.now().isoformat(),
        "total_records": 45230,
        "db_size_mb": 125
    })

@app.route('/api/health')
def api_health():
    """Health check"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })

# ═══════════════════════════════════════════════════════════════════════════
# ERROR HANDLERS
# ═══════════════════════════════════════════════════════════════════════════

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500

# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("⚡ TRADOSPHERE - Professional Trading Dashboard")
    print("=" * 70)
    print(f"🌐 Dashboard: http://localhost:8000")
    print(f"📊 API: http://localhost:8000/api/*")
    print("=" * 70 + "\n")

    app.run(host='0.0.0.0', port=8000, debug=False)
