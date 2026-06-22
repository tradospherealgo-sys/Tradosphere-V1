"""
Backtesting Engine - Test trading strategies against historical data
Simulates paper trading with historical market data and generates performance reports
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import get_candles
from technical_engine import TechnicalEngine
from options_engine import OptionsEngine

class BacktestResults:
    """Container for backtest results and metrics"""

    def __init__(self, symbol: str, start_date: datetime, end_date: datetime, initial_capital: float):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.trades: List[Dict] = []
        self.equity_curve: List[Dict] = []

    def add_trade(self, entry_date: datetime, entry_price: float, exit_date: Optional[datetime],
                  exit_price: Optional[float], quantity: int, trade_type: str, pnl: float, pnl_pct: float):
        """Add a trade to backtest results"""
        self.trades.append({
            "entry_date": entry_date.isoformat(),
            "entry_price": round(entry_price, 2),
            "exit_date": exit_date.isoformat() if exit_date else None,
            "exit_price": round(exit_price, 2) if exit_price else None,
            "quantity": quantity,
            "type": trade_type,
            "pnl": round(pnl, 2),
            "pnl_pct": round(pnl_pct, 2)
        })

    def add_equity_point(self, date: datetime, equity: float):
        """Add an equity curve data point"""
        self.equity_curve.append({
            "date": date.isoformat(),
            "equity": round(equity, 2)
        })

    def to_dict(self) -> Dict:
        """Convert results to dictionary"""
        total_trades = len(self.trades)
        winning_trades = [t for t in self.trades if t['pnl'] > 0]
        losing_trades = [t for t in self.trades if t['pnl'] < 0]

        total_pnl = sum(t['pnl'] for t in self.trades)
        total_pnl_pct = (total_pnl / self.initial_capital * 100) if self.initial_capital > 0 else 0

        avg_win = sum(t['pnl'] for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = abs(sum(t['pnl'] for t in losing_trades) / len(losing_trades)) if losing_trades else 0

        profit_factor = avg_win / avg_loss if avg_loss > 0 else 0
        win_rate = len(winning_trades) / total_trades * 100 if total_trades > 0 else 0

        # Calculate max drawdown
        max_equity = self.initial_capital
        max_drawdown = 0
        for point in self.equity_curve:
            equity = point['equity']
            if equity > max_equity:
                max_equity = equity
            drawdown = (max_equity - equity) / max_equity * 100 if max_equity > 0 else 0
            if drawdown > max_drawdown:
                max_drawdown = drawdown

        return {
            "symbol": self.symbol,
            "period": {
                "start": self.start_date.isoformat(),
                "end": self.end_date.isoformat()
            },
            "initial_capital": round(self.initial_capital, 2),
            "final_equity": round(self.equity_curve[-1]['equity'], 2) if self.equity_curve else self.initial_capital,
            "total_pnl": round(total_pnl, 2),
            "total_pnl_percent": round(total_pnl_pct, 2),
            "trades": {
                "total": total_trades,
                "winning": len(winning_trades),
                "losing": len(losing_trades),
                "win_rate": round(win_rate, 2)
            },
            "metrics": {
                "avg_win": round(avg_win, 2),
                "avg_loss": round(avg_loss, 2),
                "profit_factor": round(profit_factor, 2),
                "max_drawdown": round(max_drawdown, 2)
            },
            "trades_list": self.trades,
            "equity_curve": self.equity_curve
        }


class BacktestStrategy:
    """Base class for backtest strategies"""

    def __init__(self, name: str):
        self.name = name
        self.position = None  # None, BUY, or SELL
        self.entry_price = 0
        self.entry_date = None

    def should_buy(self, candles: List[Dict], index: int) -> bool:
        """Override: return True if should buy"""
        return False

    def should_sell(self, candles: List[Dict], index: int) -> bool:
        """Override: return True if should sell"""
        return False

    def get_entry_price(self, candles: List[Dict], index: int) -> float:
        """Get entry price (usually current close)"""
        return candles[index]['close']


class TechnicalStrategy(BacktestStrategy):
    """Strategy based on technical indicators"""

    def __init__(self):
        super().__init__("Technical-Based Strategy")

    def should_buy(self, candles: List[Dict], index: int) -> bool:
        """Buy when RSI < 30 and EMA 9 crosses above EMA 50"""
        if index < 50:
            return False

        recent_candles = candles[max(0, index-50):index+1]
        closes = [c['close'] for c in recent_candles]

        rsi = TechnicalEngine.calculate_rsi(closes, 14)
        ema9 = TechnicalEngine.calculate_ema(closes, 9)
        ema50 = TechnicalEngine.calculate_ema(closes, 50)

        if rsi and ema9 and ema50:
            # Buy on oversold + EMA positive crossover
            return rsi < 30 and ema9 > ema50

        return False

    def should_sell(self, candles: List[Dict], index: int) -> bool:
        """Sell when RSI > 70 or EMA 9 crosses below EMA 50"""
        if index < 50 or not self.position or self.position != "BUY":
            return False

        recent_candles = candles[max(0, index-50):index+1]
        closes = [c['close'] for c in recent_candles]

        rsi = TechnicalEngine.calculate_rsi(closes, 14)
        ema9 = TechnicalEngine.calculate_ema(closes, 9)
        ema50 = TechnicalEngine.calculate_ema(closes, 50)

        if rsi and ema9 and ema50:
            # Sell on overbought or EMA downtrend
            return rsi > 70 or ema9 < ema50

        return False


class MomentumStrategy(BacktestStrategy):
    """Strategy based on momentum (RSI)"""

    def __init__(self):
        super().__init__("Momentum-Based Strategy")

    def should_buy(self, candles: List[Dict], index: int) -> bool:
        """Buy when RSI < 30 (oversold)"""
        if index < 14:
            return False

        closes = [c['close'] for c in candles[:index+1]]
        rsi = TechnicalEngine.calculate_rsi(closes, 14)

        return rsi is not None and rsi < 30

    def should_sell(self, candles: List[Dict], index: int) -> bool:
        """Sell when RSI > 70 (overbought) or 5% profit"""
        if index < 14 or not self.position or self.position != "BUY":
            return False

        closes = [c['close'] for c in candles[:index+1]]
        rsi = TechnicalEngine.calculate_rsi(closes, 14)
        current_price = candles[index]['close']
        pnl_pct = (current_price - self.entry_price) / self.entry_price * 100

        return (rsi is not None and rsi > 70) or pnl_pct >= 5


class Backtest:
    """Main backtesting engine"""

    @staticmethod
    def run(symbol: str, strategy: BacktestStrategy, interval: str = "15",
            days_back: int = 30, initial_capital: float = 100000) -> Optional[Dict]:
        """
        Run backtest on historical data

        Args:
            symbol: Trading symbol (NIFTY, BANKNIFTY)
            strategy: Trading strategy to test
            interval: Candle interval (15, 60, daily)
            days_back: Days of historical data to test
            initial_capital: Initial capital for backtest

        Returns:
            Backtest results dictionary
        """
        try:
            # Calculate candles needed based on interval
            if interval == "15":
                limit = days_back * 24 * 4  # 4 candles per hour
            elif interval == "60":
                limit = days_back * 24  # 1 candle per hour
            else:  # daily
                limit = days_back

            # Get historical candles
            candles = get_candles(symbol, interval, min(limit, 500))

            if not candles or len(candles) < 50:
                return {
                    "status": "error",
                    "message": f"Insufficient historical data for {symbol} ({len(candles) if candles else 0} candles)"
                }

            # Initialize results
            results = BacktestResults(
                symbol=symbol,
                start_date=datetime.fromisoformat(candles[0]['time']),
                end_date=datetime.fromisoformat(candles[-1]['time']),
                initial_capital=initial_capital
            )

            # Backtest state
            current_equity = initial_capital
            position = None
            entry_price = 0
            entry_date = None

            # Add initial equity point
            results.add_equity_point(results.start_date, current_equity)

            # Process each candle
            for i in range(len(candles)):
                candle = candles[i]
                candle_date = datetime.fromisoformat(candle['time'])
                current_price = candle['close']

                # Check exit conditions if in position
                if position == "BUY" and strategy.should_sell(candles, i):
                    # Close trade
                    pnl = (current_price - entry_price) * 1  # 1 lot
                    pnl_pct = (pnl / entry_price) * 100
                    current_equity += pnl

                    results.add_trade(
                        entry_date=entry_date,
                        entry_price=entry_price,
                        exit_date=candle_date,
                        exit_price=current_price,
                        quantity=1,
                        trade_type="BUY",
                        pnl=pnl,
                        pnl_pct=pnl_pct
                    )

                    position = None
                    entry_price = 0
                    entry_date = None

                # Check entry conditions if not in position
                if position is None and strategy.should_buy(candles, i):
                    # Open trade
                    entry_price = current_price
                    entry_date = candle_date
                    position = "BUY"
                    strategy.position = "BUY"
                    strategy.entry_price = entry_price
                    strategy.entry_date = entry_date

                # Add equity point
                if position == "BUY":
                    unrealized_pnl = (current_price - entry_price) * 1
                    results.add_equity_point(candle_date, current_equity + unrealized_pnl)
                else:
                    results.add_equity_point(candle_date, current_equity)

            # Close any open position at end
            if position == "BUY":
                final_price = candles[-1]['close']
                pnl = (final_price - entry_price) * 1
                pnl_pct = (pnl / entry_price) * 100
                current_equity += pnl

                results.add_trade(
                    entry_date=entry_date,
                    entry_price=entry_price,
                    exit_date=results.end_date,
                    exit_price=final_price,
                    quantity=1,
                    trade_type="BUY",
                    pnl=pnl,
                    pnl_pct=pnl_pct
                )

            return {
                "status": "success",
                "strategy": strategy.name,
                "data": results.to_dict()
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    @staticmethod
    def compare_strategies(symbol: str, interval: str = "15",
                          days_back: int = 30, initial_capital: float = 100000) -> Dict:
        """
        Compare multiple strategies on same data

        Returns:
            Dictionary with results for each strategy
        """
        strategies = [
            TechnicalStrategy(),
            MomentumStrategy()
        ]

        results = {
            "symbol": symbol,
            "period": {
                "interval": interval,
                "days": days_back
            },
            "initial_capital": initial_capital,
            "strategies": {}
        }

        for strategy in strategies:
            result = Backtest.run(symbol, strategy, interval, days_back, initial_capital)
            if result.get("status") == "success":
                results["strategies"][strategy.name] = result["data"]
            else:
                results["strategies"][strategy.name] = result

        return results
