"""
Tradosphere Server - Flask API with Angel One SmartAPI Integration
Market Intelligence Backend with Technical & Options Analysis
"""

import os
from datetime import datetime
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from dotenv import load_dotenv

# Database imports
from database import (
    init_db, get_all_signals, get_pending_signals, get_metrics, get_all_trades,
    approve_signal, reject_signal, record_trade, get_daily_pnl, get_candles,
    get_latest_market_snapshot, get_latest_option_chain, get_db, Signal
)

# Market & Analysis imports
from market_data import AngelOneMarketData
from signal_writer import generate_on_demand
from technical_engine import TechnicalEngine
from options_engine import OptionsEngine
from greeks_calculator import BlackScholesGreeks, GreeksInjector
from reconciliation_engine import ReconciliationEngine

load_dotenv()

app = Flask(__name__)
CORS(app)
init_db()

# Global market data instance
market = None

def init_market_data():
    """Initialize market data with credentials from .env"""
    global market
    try:
        api_key = os.getenv("ANGEL_ONE_API_KEY", "")
        client_code = os.getenv("ANGEL_ONE_CLIENT_CODE", "")
        pin = os.getenv("ANGEL_ONE_PIN", "")
        totp_secret = os.getenv("ANGEL_ONE_TOTP_SECRET", "")

        if not api_key or not client_code or not pin:
            print("❌ Missing credentials in .env file")
            market = None
            return

        market = AngelOneMarketData(api_key, client_code, pin, totp_secret)
        print("✅ Market data initialized successfully")
    except Exception as e:
        print(f"⚠️  Failed to initialize market data: {str(e)}")
        market = None

# Initialize on startup
init_market_data()

# ===== HEALTH & STATUS =====
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Tradosphere API"
    }), 200

@app.route('/api/status', methods=['GET'])
def status():
    """Get system and broker connection status"""
    try:
        if market and market.is_authenticated():
            broker_status = market.get_status()
            connected = True
            message = f"Connected to {broker_status.get('account', 'Angel One')}"
        else:
            broker_status = {"connected": False}
            connected = False
            message = "Not connected to Angel One API"

        return jsonify({
            "status": "operational",
            "broker": "Angel One",
            "connected": connected,
            "message": message,
            "account": broker_status.get("account") if connected else None,
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

# ===== LIVE MARKET DATA =====
@app.route('/api/market/live', methods=['GET'])
def market_live():
    """Get live NIFTY and BANKNIFTY prices"""
    try:
        if not market or not market.is_authenticated():
            return jsonify({
                "status": "error",
                "message": "Not connected to Angel One API"
            }), 401

        nifty_data = market.get_nifty_price()
        banknifty_data = market.get_banknifty_price()

        return jsonify({
            "status": "success",
            "broker": "Angel One",
            "connected": True,
            "NIFTY": nifty_data.get("ltp") if nifty_data else None,
            "BANKNIFTY": banknifty_data.get("ltp") if banknifty_data else None,
            "NIFTY_data": nifty_data,
            "BANKNIFTY_data": banknifty_data,
            "timestamp": datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@app.route('/api/nifty/price', methods=['GET'])
def nifty_price():
    """Get NIFTY live price"""
    try:
        if not market or not market.is_authenticated():
            return jsonify({"status": "error", "message": "Not connected to Angel One API"}), 401

        price_data = market.get_nifty_price()

        if not price_data:
            return jsonify({"status": "error", "message": "Failed to fetch NIFTY price"}), 500

        return jsonify({
            "status": "success",
            "data": price_data,
            "timestamp": datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/banknifty/price', methods=['GET'])
def banknifty_price():
    """Get BANKNIFTY live price"""
    try:
        if not market or not market.is_authenticated():
            return jsonify({"status": "error", "message": "Not connected to Angel One API"}), 401

        price_data = market.get_banknifty_price()

        if not price_data:
            return jsonify({"status": "error", "message": "Failed to fetch BANKNIFTY price"}), 500

        return jsonify({
            "status": "success",
            "data": price_data,
            "timestamp": datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ===== CANDLE DATA =====
@app.route('/api/candles/update', methods=['GET'])
def update_candles():
    """Fetch and save historical candles for analysis"""
    try:
        if not market or not market.is_authenticated():
            return jsonify({"status": "error", "message": "Not connected to Angel One API"}), 401

        results = {}

        # Fetch and save NIFTY 15-minute candles
        print("\n📊 Fetching NIFTY 15-minute candles...")
        nifty_candles = market.get_historical_candles("NIFTY", "15", limit=100)
        if nifty_candles:
            market.save_candles_to_db("NIFTY", "15", nifty_candles)
            results["NIFTY_15min"] = len(nifty_candles)
        else:
            results["NIFTY_15min"] = 0

        # Fetch and save BANKNIFTY 15-minute candles
        print("\n📊 Fetching BANKNIFTY 15-minute candles...")
        bnf_candles = market.get_historical_candles("BANKNIFTY", "15", limit=100)
        if bnf_candles:
            market.save_candles_to_db("BANKNIFTY", "15", bnf_candles)
            results["BANKNIFTY_15min"] = len(bnf_candles)
        else:
            results["BANKNIFTY_15min"] = 0

        # Fetch and save daily candles
        print("\n📊 Fetching NIFTY daily candles...")
        nifty_daily = market.get_historical_candles("NIFTY", "daily", limit=100)
        if nifty_daily:
            market.save_candles_to_db("NIFTY", "daily", nifty_daily)
            results["NIFTY_daily"] = len(nifty_daily)
        else:
            results["NIFTY_daily"] = 0

        print("\n📊 Fetching BANKNIFTY daily candles...")
        bnf_daily = market.get_historical_candles("BANKNIFTY", "daily", limit=100)
        if bnf_daily:
            market.save_candles_to_db("BANKNIFTY", "daily", bnf_daily)
            results["BANKNIFTY_daily"] = len(bnf_daily)
        else:
            results["BANKNIFTY_daily"] = 0

        total_saved = sum(results.values())

        return jsonify({
            "status": "success",
            "message": f"Fetched and saved {total_saved} total candles",
            "NIFTY_15min_candles": results["NIFTY_15min"],
            "BANKNIFTY_15min_candles": results["BANKNIFTY_15min"],
            "NIFTY_daily_candles": results["NIFTY_daily"],
            "BANKNIFTY_daily_candles": results["BANKNIFTY_daily"],
            "total_candles": total_saved,
            "timestamp": datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        print(f"❌ Error updating candles: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

# ===== TECHNICAL ANALYSIS =====
@app.route('/api/analysis/technical', methods=['GET'])
def technical_analysis():
    """Get technical analysis for a symbol"""
    try:
        symbol = request.args.get('symbol', 'NIFTY')
        interval = request.args.get('interval', '15')
        limit = request.args.get('limit', 100, type=int)

        if not market or not market.is_authenticated():
            return jsonify({"status": "error", "message": "Not connected to Angel One API"}), 401

        # Get candles from database
        candles = get_candles(symbol, interval, limit)

        if not candles or len(candles) < 14:
            return jsonify({
                "status": "error",
                "message": f"Insufficient candle data for {symbol} ({len(candles) if candles else 0} candles, need 14+)"
            }), 400

        # Run technical analysis
        analysis = TechnicalEngine.analyze(candles)

        # Flatten response for frontend compatibility
        return jsonify({
            "status": "success",
            "symbol": symbol,
            "interval": interval,
            "candle_count": len(candles),
            "trend": analysis.get("trend", "NEUTRAL"),
            "momentum": analysis.get("momentum", "NEUTRAL"),
            "setup": analysis.get("setup", "RANGE_BOUND"),
            "indicators": analysis.get("indicators", {}),
            "price_vs_indicators": analysis.get("price_vs_indicators", {}),
            "breakout": analysis.get("breakout", {}),
            "data": analysis,
            "timestamp": datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ===== OPTIONS CHAIN =====
@app.route('/api/options/update', methods=['GET'])
def update_options_chain():
    """Fetch and save option chain data"""
    try:
        if not market or not market.is_authenticated():
            return jsonify({"status": "error", "message": "Not connected to Angel One API"}), 401

        results = {}

        # Fetch NIFTY options
        print("\n📊 Fetching NIFTY option chain...")
        nifty_options = market.get_option_chain("NIFTY")
        if nifty_options:
            market.save_option_chain_to_db(nifty_options)
            results["NIFTY"] = {
                "status": "success",
                "pcr": nifty_options.get("pcr", 0),
                "spot": nifty_options.get("spot_price", 0)
            }
        else:
            results["NIFTY"] = {"status": "error"}

        # Fetch BANKNIFTY options
        print("\n📊 Fetching BANKNIFTY option chain...")
        bnf_options = market.get_option_chain("BANKNIFTY")
        if bnf_options:
            market.save_option_chain_to_db(bnf_options)
            results["BANKNIFTY"] = {
                "status": "success",
                "pcr": bnf_options.get("pcr", 0),
                "spot": bnf_options.get("spot_price", 0)
            }
        else:
            results["BANKNIFTY"] = {"status": "error"}

        return jsonify({
            "status": "success",
            "message": "Option chains updated",
            "NIFTY": results["NIFTY"],
            "BANKNIFTY": results["BANKNIFTY"],
            "timestamp": datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        print(f"❌ Error updating options: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# ===== OPTIONS ANALYSIS =====
@app.route('/api/analysis/options', methods=['GET'])
def options_analysis():
    """Get real options market analysis for a symbol"""
    try:
        symbol = request.args.get('symbol', 'NIFTY')

        if not market or not market.is_authenticated():
            return jsonify({"status": "error", "message": "Not connected to Angel One API"}), 401

        # Get option chain data - fetch fresh or from database
        option_chain = market.get_option_chain(symbol)

        if not option_chain or option_chain.get("status") != "success":
            return jsonify({
                "status": "error",
                "message": f"Could not fetch option chain for {symbol}"
            }), 400

        # Run comprehensive options analysis
        analysis = OptionsEngine.analyze(option_chain)

        # Extract strikes from option_chain for frontend
        strikes = option_chain.get("strikes", [])
        spot_price = option_chain.get("spot_price", 0)

        return jsonify({
            "status": "success",
            "symbol": symbol,
            "PCR": analysis.get("pcr"),
            "pcr": analysis.get("pcr"),
            "support": analysis.get("support"),
            "resistance": analysis.get("resistance"),
            "max_pain": analysis.get("max_pain"),
            "bias": analysis.get("bias"),
            "oi_skew": analysis.get("oi_skew", "BALANCED"),
            "reason": analysis.get("summary", {}).get("reason"),
            "spot_price": spot_price,
            "full_analysis": {
                "strikes": strikes,
                "spot_price": spot_price,
                **analysis
            },
            "timestamp": datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ===== SIGNALS =====
@app.route('/api/signals/generate', methods=['POST'])
def generate_signals():
    try:
        if not market or not market.is_authenticated():
            return jsonify({"status": "error", "message": "Not connected to Angel One API"}), 401

        result = generate_on_demand()
        if result.get("status") == "error":
            return jsonify(result), 500
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/signals', methods=['GET'])
def get_signals():
    """Get latest generated signals"""
    try:
        limit = request.args.get('limit', 20, type=int)
        signals = get_pending_signals()[:limit]

        return jsonify({
            "status": "success",
            "count": len(signals),
            "data": signals,
            "timestamp": datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/signals/latest', methods=['GET'])
def get_latest_signals():
    try:
        signals = get_pending_signals()
        return jsonify({
            "status": "success",
            "count": len(signals),
            "data": signals,
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/signals/all', methods=['GET'])
def get_all_signals_endpoint():
    try:
        limit = request.args.get('limit', 50, type=int)
        signals = get_all_signals(limit)
        return jsonify({
            "status": "success",
            "count": len(signals),
            "data": signals,
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/signals/<int:signal_id>/approve', methods=['POST'])
def approve_signal_endpoint(signal_id):
    try:
        success = approve_signal(signal_id)
        if success:
            return jsonify({"status": "success", "message": f"Signal {signal_id} approved"}), 200
        return jsonify({"status": "error", "message": "Signal not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/signals/<int:signal_id>/reject', methods=['POST'])
def reject_signal_endpoint(signal_id):
    try:
        success = reject_signal(signal_id)
        if success:
            return jsonify({"status": "success", "message": f"Signal {signal_id} rejected"}), 200
        return jsonify({"status": "error", "message": "Signal not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ===== TRADES =====
@app.route('/api/trades/record', methods=['POST'])
def record_trade_endpoint():
    try:
        data = request.get_json()
        signal_id = data.get("signal_id")
        entry_price = data.get("entry_price")
        exit_price = data.get("exit_price")
        result = data.get("result")

        if not signal_id or not entry_price:
            return jsonify({"status": "error", "message": "Missing required fields"}), 400

        pnl = None
        if exit_price:
            pnl = exit_price - entry_price

        trade = record_trade(signal_id, entry_price, exit_price, pnl, result)
        return jsonify({"status": "success", "data": trade, "timestamp": datetime.utcnow().isoformat()}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/trades/history', methods=['GET'])
def trades_history():
    try:
        limit = request.args.get('limit', 100, type=int)
        trades = get_all_trades(limit)
        return jsonify({"status": "success", "count": len(trades), "data": trades, "timestamp": datetime.utcnow().isoformat()}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ===== PERFORMANCE =====
@app.route('/api/performance/metrics', methods=['GET'])
def performance_metrics():
    try:
        metrics = get_metrics()
        return jsonify({"status": "success", "data": metrics, "timestamp": datetime.utcnow().isoformat()}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/performance/daily-pnl', methods=['GET'])
def daily_pnl():
    try:
        days = request.args.get('days', 7, type=int)
        pnl = get_daily_pnl(days)
        return jsonify({"status": "success", "data": pnl, "timestamp": datetime.utcnow().isoformat()}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ===== AI INTELLIGENCE =====
@app.route('/api/ai/market-view', methods=['GET'])
def ai_market_view():
    """Get AI-generated market summary and analysis"""
    try:
        from ai_engine import AIEngine

        symbol = request.args.get('symbol', 'NIFTY')

        # Get technical and options analysis
        tech_data = None
        opt_data = None

        try:
            tech_candles = get_candles(symbol, interval="15", limit=100)
            if tech_candles and len(tech_candles) >= 14:
                tech_data = TechnicalEngine.analyze(tech_candles)
        except:
            pass

        try:
            opt_chain = get_latest_option_chain(symbol)
            if opt_chain:
                opt_input = {
                    "call_oi": opt_chain.get("total_call_oi", 0),
                    "put_oi": opt_chain.get("total_put_oi", 0),
                    "call_volume": opt_chain.get("total_call_oi", 0) // 100,
                    "put_volume": opt_chain.get("total_put_oi", 0) // 100,
                    "spot_price": opt_chain.get("spot_price", 0),
                    "previous_total_oi": opt_chain.get("total_call_oi", 0) + opt_chain.get("total_put_oi", 0)
                }
                opt_data = OptionsEngine.analyze(opt_input)
        except:
            pass

        if not tech_data or not opt_data:
            return jsonify({
                "status": "error",
                "message": "Insufficient data for AI analysis"
            }), 400

        summary = AIEngine.generate_market_summary(tech_data, opt_data)
        return jsonify(summary), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/ai/signal-explanation', methods=['GET'])
def ai_signal_explanation():
    """Get AI explanation for a specific signal"""
    try:
        from ai_engine import AIEngine

        signal_id = request.args.get('signal_id', type=int)
        if not signal_id:
            return jsonify({"status": "error", "message": "signal_id required"}), 400

        db = get_db()
        signal = db.query(Signal).filter(Signal.id == signal_id).first()
        db.close()

        if not signal:
            return jsonify({"status": "error", "message": "Signal not found"}), 404

        # Get supporting analysis
        tech_data = None
        opt_data = None

        try:
            tech_candles = get_candles(signal.symbol, interval="15", limit=100)
            if tech_candles and len(tech_candles) >= 14:
                tech_data = TechnicalEngine.analyze(tech_candles)
        except:
            pass

        try:
            opt_chain = get_latest_option_chain(signal.symbol)
            if opt_chain:
                opt_input = {
                    "call_oi": opt_chain.get("total_call_oi", 0),
                    "put_oi": opt_chain.get("total_put_oi", 0),
                    "call_volume": opt_chain.get("total_call_oi", 0) // 100,
                    "put_volume": opt_chain.get("total_put_oi", 0) // 100,
                    "spot_price": opt_chain.get("spot_price", 0),
                    "previous_total_oi": opt_chain.get("total_call_oi", 0) + opt_chain.get("total_put_oi", 0)
                }
                opt_data = OptionsEngine.analyze(opt_input)
        except:
            pass

        signal_data = signal.to_dict()
        explanation = AIEngine.generate_signal_explanation(signal_data, tech_data, opt_data)
        return jsonify(explanation), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/ai/risk-assessment', methods=['GET'])
def ai_risk_assessment():
    """Get AI risk assessment for current market"""
    try:
        from ai_engine import AIEngine

        symbol = request.args.get('symbol', 'NIFTY')

        tech_data = None
        opt_data = None

        try:
            tech_candles = get_candles(symbol, interval="15", limit=100)
            if tech_candles and len(tech_candles) >= 14:
                tech_data = TechnicalEngine.analyze(tech_candles)
        except:
            pass

        try:
            opt_chain = get_latest_option_chain(symbol)
            if opt_chain:
                opt_input = {
                    "call_oi": opt_chain.get("total_call_oi", 0),
                    "put_oi": opt_chain.get("total_put_oi", 0),
                    "call_volume": opt_chain.get("total_call_oi", 0) // 100,
                    "put_volume": opt_chain.get("total_put_oi", 0) // 100,
                    "spot_price": opt_chain.get("spot_price", 0),
                    "previous_total_oi": opt_chain.get("total_call_oi", 0) + opt_chain.get("total_put_oi", 0)
                }
                opt_data = OptionsEngine.analyze(opt_input)
        except:
            pass

        if not tech_data or not opt_data:
            return jsonify({
                "status": "error",
                "message": "Insufficient data for risk assessment"
            }), 400

        risk = AIEngine.generate_risk_warning(tech_data, opt_data)
        return jsonify(risk), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ===== LEARNING SYSTEM =====
@app.route('/api/learning/performance', methods=['GET'])
def learning_performance():
    """Get signal performance metrics and learning insights"""
    try:
        from learning_engine import LearningEngine

        symbol = request.args.get('symbol')
        days = request.args.get('days', 30, type=int)

        performance = LearningEngine.calculate_signal_performance(symbol, days)
        return jsonify(performance), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/learning/insights', methods=['GET'])
def learning_insights():
    """Get AI learning insights and recommendations"""
    try:
        from learning_engine import LearningEngine

        insights = LearningEngine.get_learning_insights()
        return jsonify(insights), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/learning/setup-analysis', methods=['GET'])
def learning_setup_analysis():
    """Get analysis by setup type"""
    try:
        from learning_engine import LearningEngine

        analysis = LearningEngine.get_setup_analysis()
        return jsonify(analysis), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/learning/monthly', methods=['GET'])
def learning_monthly():
    """Get monthly performance breakdown"""
    try:
        from learning_engine import LearningEngine

        monthly = LearningEngine.get_monthly_performance()
        return jsonify(monthly), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ===== GREEKS CALCULATION =====
@app.route('/api/analysis/greeks', methods=['GET'])
def analyze_greeks():
    """Get synthetic Greeks (Delta, Gamma) for option chain"""
    try:
        symbol = request.args.get('symbol', 'NIFTY')

        if not market or not market.is_authenticated():
            return jsonify({"status": "error", "message": "Not connected to Angel One API"}), 401

        # Get option chain data
        option_chain = market.get_option_chain(symbol)

        if not option_chain or option_chain.get("status") != "success":
            return jsonify({
                "status": "error",
                "message": f"Could not fetch option chain for {symbol}"
            }), 400

        # Extract Greeks from strikes if already calculated
        strikes = option_chain.get("strikes", [])

        return jsonify({
            "status": "success",
            "symbol": symbol,
            "spot_price": option_chain.get("spot_price"),
            "with_greeks": option_chain.get("with_greeks", False),
            "strikes": strikes,
            "timestamp": datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/analysis/greeks/<symbol>/<float:strike>', methods=['GET'])
def greeks_for_strike(symbol, strike):
    """Get Greeks for specific strike"""
    try:
        from greeks_calculator import BlackScholesGreeks

        if not market or not market.is_authenticated():
            return jsonify({"status": "error", "message": "Not connected to Angel One API"}), 401

        # Get current price
        if symbol == "NIFTY":
            price_data = market.get_nifty_price()
        elif symbol == "BANKNIFTY":
            price_data = market.get_banknifty_price()
        else:
            return jsonify({"status": "error", "message": "Invalid symbol"}), 400

        if not price_data:
            return jsonify({"status": "error", "message": "Could not fetch price"}), 500

        spot_price = price_data.get("ltp", 0)

        # Get option chain to estimate IV
        option_chain = market.get_option_chain(symbol)
        if not option_chain:
            iv = 0.25  # Default IV
        else:
            atm_chain = option_chain.get("strikes", [])
            atm_call = None
            atm_put = None

            for s in atm_chain:
                if s['strike'] == int(spot_price / (50 if symbol == "NIFTY" else 100)) * (50 if symbol == "NIFTY" else 100):
                    atm_call = s['ce']['ltp']
                    atm_put = s['pe']['ltp']
                    break

            if atm_call and atm_put:
                iv = BlackScholesGreeks.estimate_iv_from_atm_straddle(spot_price, atm_call, atm_put)
            else:
                iv = 0.25

        time_to_expiry = 1 / 365.0

        return jsonify({
            "status": "success",
            "symbol": symbol,
            "spot_price": spot_price,
            "strike": strike,
            "estimated_iv": round(iv * 100, 2),
            "greeks": {
                "call": {
                    "delta": BlackScholesGreeks.calculate_call_delta(spot_price, strike, time_to_expiry, iv),
                    "gamma": BlackScholesGreeks.calculate_gamma(spot_price, strike, time_to_expiry, iv),
                    "vega": BlackScholesGreeks.calculate_vega(spot_price, strike, time_to_expiry, iv),
                    "theta": BlackScholesGreeks.calculate_theta(spot_price, strike, time_to_expiry, iv, is_call=True)
                },
                "put": {
                    "delta": BlackScholesGreeks.calculate_put_delta(spot_price, strike, time_to_expiry, iv),
                    "gamma": BlackScholesGreeks.calculate_gamma(spot_price, strike, time_to_expiry, iv),
                    "vega": BlackScholesGreeks.calculate_vega(spot_price, strike, time_to_expiry, iv),
                    "theta": BlackScholesGreeks.calculate_theta(spot_price, strike, time_to_expiry, iv, is_call=False)
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ===== RECONCILIATION =====
@app.route('/api/reconciliation/reconcile', methods=['POST'])
def reconcile_signals():
    """Execute post-market reconciliation of all pending signals"""
    try:
        from reconciliation_engine import ReconciliationEngine

        # Check if it's time for reconciliation
        if not ReconciliationEngine.is_reconciliation_time():
            return jsonify({
                "status": "warning",
                "message": "Reconciliation only runs between 3:45 PM - 4:00 PM IST"
            }), 400

        result = ReconciliationEngine.reconcile_all_pending()
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/reconciliation/manual/<symbol>', methods=['POST'])
def manual_reconciliation(symbol):
    """Manually reconcile signals for a specific symbol"""
    try:
        from reconciliation_engine import ReconciliationEngine

        days = request.args.get('days', 1, type=int)

        db = get_db()
        from datetime import datetime, timedelta

        # Get signals from last N days
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        signals = db.query(Signal).filter(
            Signal.symbol == symbol,
            Signal.timestamp >= cutoff_date,
            Signal.status == "PENDING"
        ).all()

        db.close()

        if not signals:
            return jsonify({
                "status": "info",
                "message": f"No pending signals found for {symbol} in last {days} days"
            }), 200

        results = []
        for signal in signals:
            reconciliation = ReconciliationEngine.reconcile_signal(signal)
            results.append(reconciliation)

        return jsonify({
            "status": "success",
            "symbol": symbol,
            "signals_reconciled": len(results),
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/reconciliation/insights', methods=['GET'])
def reconciliation_insights():
    """Get reconciliation-based learning insights and accuracy metrics"""
    try:
        from reconciliation_engine import ReconciliationEngine

        insights = ReconciliationEngine.generate_reconciliation_insights()
        return jsonify(insights), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/reconciliation/status', methods=['GET'])
def reconciliation_status():
    """Check reconciliation system status and next run time"""
    try:
        from reconciliation_engine import ReconciliationEngine
        import pytz
        from datetime import datetime, time

        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)

        is_time = ReconciliationEngine.is_reconciliation_time()
        next_run = datetime.combine(now.date() + __import__('datetime').timedelta(days=1), time(15, 45))

        return jsonify({
            "status": "success",
            "is_reconciliation_time": is_time,
            "current_time": now.isoformat(),
            "reconciliation_window": "3:45 PM - 4:00 PM IST",
            "next_scheduled_run": next_run.isoformat() if not is_time else now.isoformat(),
            "market_close_time": "3:30 PM IST"
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ===== DASHBOARD =====
@app.route('/')
def dashboard():
    try:
        return send_file('tradosphere_dashboard_final.html', mimetype='text/html')
    except Exception as e:
        return f"Error serving dashboard: {e}", 500

@app.route('/dashboard')
def dashboard_alt():
    return dashboard()

# ===== ERROR HANDLERS =====
@app.errorhandler(404)
def not_found(e):
    return jsonify({"status": "error", "message": "Endpoint not found", "path": request.path}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"status": "error", "message": "Internal server error"}), 500

if __name__ == '__main__':
    print("\n" + "="*70)
    print("⚡ TRADOSPHERE - Advanced Market Intelligence Backend v2")
    print("="*70)
    print("🚀 Server starting on http://localhost:8000")
    print("📊 Dashboard: http://localhost:8000/")
    print("\n📈 CORE API ENDPOINTS:")
    print("   - Live prices: /api/market/live")
    print("   - Technical: /api/analysis/technical?symbol=NIFTY")
    print("   - Options: /api/analysis/options?symbol=NIFTY")
    print("   - Signals: /api/signals | /api/signals/generate (POST)")
    print("\n🧮 NEW: GREEKS CALCULATION:")
    print("   - Greeks data: /api/analysis/greeks?symbol=NIFTY")
    print("   - Strike Greeks: /api/analysis/greeks/NIFTY/23200")
    print("   (Synthetic Black-Scholes Delta, Gamma, Vega, Theta)")
    print("\n📊 NEW: POST-MARKET RECONCILIATION:")
    print("   - Reconcile signals: /api/reconciliation/reconcile (POST)")
    print("   - Manual reconcile: /api/reconciliation/manual/NIFTY?days=1")
    print("   - Insights: /api/reconciliation/insights")
    print("   - Status: /api/reconciliation/status")
    print("   (Runs 3:45 PM - 4:00 PM IST, validates targets vs actual prices)")
    print("\n✨ FEATURES:")
    print("   ✓ Real-time Chart.js visualization (Price, EMA20, VWAP)")
    print("   ✓ Signal copy-to-clipboard (📋 Copy button)")
    print("   ✓ Synthetic Greeks via Black-Scholes")
    print("   ✓ Smart option chain fallback (20 strikes per side)")
    print("   ✓ Automated signal reconciliation & accuracy tracking")
    print("="*70 + "\n")
    app.run(host='0.0.0.0', port=8000, debug=False, use_reloader=False)
