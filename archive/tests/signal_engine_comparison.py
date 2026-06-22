"""
Signal Engine Comparative Analysis
Quantitative Research Auditor Framework
Compares signals_engine.py (System A) vs signal_writer.py (System B)
"""

import sys
import math
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import json

# Add project to path
sys.path.insert(0, '/Users/anshhdodia/Desktop/tradosphere_github')

from signals_engine import SignalsEngine
from signal_writer import SignalGenerator
from technical_engine import TechnicalEngine
from options_engine import OptionsEngine


class MarketSnapshot:
    """Represents a market snapshot for testing"""

    def __init__(self, symbol: str, price: float, rsi: float, ema9: float, ema50: float,
                 macd_hist: float, vwap: float, trend: str, momentum: str,
                 pcr: float, support: float, resistance: float, oi_skew: str = "BALANCED"):
        self.symbol = symbol
        self.price = price
        self.rsi = rsi
        self.ema9 = ema9
        self.ema50 = ema50
        self.macd_hist = macd_hist
        self.vwap = vwap
        self.trend = trend
        self.momentum = momentum
        self.pcr = pcr
        self.support = support
        self.resistance = resistance
        self.oi_skew = oi_skew

    def to_market_data(self) -> Dict:
        """Convert to market_data format for System A"""
        return {
            'current_price': self.price,
            'change_percent': 0
        }

    def to_technical_data(self) -> Dict:
        """Convert to technical_data format"""
        return {
            'status': 'success',
            'indicators': {
                'rsi': self.rsi,
                'ema_9': self.ema9,
                'ema_20': self.ema50,  # Simplified
                'ema_50': self.ema50,
                'vwap': self.vwap
            },
            'macd': {
                'histogram': self.macd_hist
            },
            'bollinger_bands': {
                'upper_band': self.price + 100,
                'lower_band': self.price - 100
            },
            'trend': self.trend,
            'momentum': self.momentum,
            'setup': 'BREAKOUT' if abs(self.price - self.resistance) < 200 else 'RANGE_BOUND',
            'price_vs_indicators': {
                'price_vs_vwap': 'above' if self.price > self.vwap else 'below'
            }
        }

    def to_options_data(self) -> Dict:
        """Convert to options_data format"""
        return {
            'pcr': self.pcr,
            'max_pain': self.price,
            'status': 'success',
            'bias': 'BULLISH' if self.pcr < 0.8 else ('BEARISH' if self.pcr > 1.2 else 'NEUTRAL'),
            'oi_skew': self.oi_skew,
            'support': self.support,
            'resistance': self.resistance
        }


class SignalComparison:
    """Framework for comparing two signal engines"""

    def __init__(self):
        self.results = []
        self.system_a_trades = []
        self.system_b_trades = []
        self.snapshots_tested = 0

    def test_snapshot(self, snapshot: MarketSnapshot) -> Dict:
        """Test both engines on identical market snapshot"""
        self.snapshots_tested += 1

        # Get data formats
        market_data = snapshot.to_market_data()
        technical_data = snapshot.to_technical_data()
        options_data = snapshot.to_options_data()

        # System A: SignalsEngine
        system_a_result = self._test_system_a(market_data, technical_data, options_data, snapshot.symbol)

        # System B: SignalGenerator (would need market data instance, skip for now)
        system_b_result = self._test_system_b_manual(snapshot)

        comparison = {
            'snapshot': snapshot,
            'system_a': system_a_result,
            'system_b': system_b_result,
            'divergence': self._calculate_divergence(system_a_result, system_b_result)
        }

        self.results.append(comparison)
        return comparison

    def _test_system_a(self, market_data: Dict, technical_data: Dict,
                       options_data: Dict, symbol: str) -> Dict:
        """Test System A (SignalsEngine)"""
        try:
            signals = SignalsEngine.generate_signals(market_data, options_data, technical_data, symbol)

            if not signals:
                return {'status': 'no_signal', 'confidence': 0}

            # Take first signal if multiple
            signal = signals[0]

            return {
                'status': 'generated',
                'direction': signal.get('direction', 'UNKNOWN'),
                'type': signal.get('type', 'UNKNOWN'),
                'confidence': signal.get('confidence', 0),
                'entry': signal.get('entry', 0),
                'target': signal.get('target', 0),
                'stop_loss': signal.get('stop_loss', 0),
                'strike': signal.get('strike', 0),
                'risk_reward': signal.get('risk_reward', 0),
                'reasoning': signal.get('reasoning', '')[:100]  # Truncate
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)[:100]}

    def _test_system_b_manual(self, snapshot: MarketSnapshot) -> Dict:
        """Test System B (SignalGenerator) using manual calculation"""
        try:
            # Manual calculation of System B logic based on signal_writer.py
            technical_score = self._calc_technical_score_b(snapshot)
            options_score = self._calc_options_score_b(snapshot)
            market_score = self._calc_market_score_b(snapshot)

            total_score = technical_score + options_score + market_score
            confidence = min((total_score / 100 * 100), 99) if total_score > 0 else 0

            # Direction logic
            bullish_score = self._calc_bullish_score_b(snapshot)
            bearish_score = self._calc_bearish_score_b(snapshot)

            if bullish_score > bearish_score and confidence >= 50:
                direction = "BUY"
            elif bearish_score > bullish_score and confidence >= 50:
                direction = "SELL"
            else:
                direction = "WAIT"

            # Entry, Target, SL
            if snapshot.symbol == "NIFTY":
                atr_equiv = 200
                entry_offset = 50
            else:
                atr_equiv = 300
                entry_offset = 100

            if direction == "BUY":
                entry = round((snapshot.price - entry_offset + snapshot.price + entry_offset) / 2)
                target = round(snapshot.resistance if snapshot.resistance > snapshot.price else snapshot.price + atr_equiv * 1.5)
                sl = round(snapshot.support if snapshot.support < snapshot.price else snapshot.price - atr_equiv)
            elif direction == "SELL":
                entry = round((snapshot.price - entry_offset + snapshot.price + entry_offset) / 2)
                target = round(snapshot.support if snapshot.support < snapshot.price else snapshot.price - atr_equiv * 1.5)
                sl = round(snapshot.resistance if snapshot.resistance > snapshot.price else snapshot.price + atr_equiv)
            else:
                entry = target = sl = 0

            # Risk/Reward
            if direction != "WAIT" and sl != entry:
                risk = abs(sl - entry)
                reward = abs(target - entry)
                risk_reward = reward / risk if risk > 0 else 0
            else:
                risk_reward = 0

            return {
                'status': 'generated' if direction != "WAIT" else 'no_signal',
                'direction': direction,
                'confidence': round(confidence, 1),
                'entry': entry,
                'target': target,
                'stop_loss': sl,
                'risk_reward': round(risk_reward, 2),
                'technical_score': technical_score,
                'options_score': options_score,
                'market_score': market_score,
                'bullish_score': bullish_score,
                'bearish_score': bearish_score
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)[:100]}

    def _calc_technical_score_b(self, snap: MarketSnapshot) -> int:
        """Calculate technical score for System B"""
        score = 0

        # Trend (10 pts)
        if snap.trend in ["BULLISH", "BEARISH"]:
            score += 10
        elif snap.trend == "NEUTRAL":
            score += 5

        # Momentum (10 pts)
        if "STRONG" in snap.momentum:
            score += 10
        elif snap.momentum != "NEUTRAL":
            score += 7
        elif 30 < snap.rsi < 70:
            score += 5

        # Setup (10 pts)
        if "BREAKOUT" in snap.trend:
            score += 10
        else:
            score += 6

        # VWAP (10 pts)
        if snap.price > snap.vwap:
            score += 10

        return min(score, 40)

    def _calc_options_score_b(self, snap: MarketSnapshot) -> int:
        """Calculate options score for System B"""
        score = 0

        # PCR (15 pts)
        if snap.pcr > 1.2:
            score += 15
        elif snap.pcr > 1.0:
            score += 12
        elif snap.pcr < 0.8:
            score += 10
        elif snap.pcr < 1.0:
            score += 8
        else:
            score += 5

        # OI Skew (15 pts)
        if snap.oi_skew != "BALANCED":
            score += 15
        else:
            score += 8

        # Bias (10 pts)
        bias = "BULLISH" if snap.pcr < 0.8 else ("BEARISH" if snap.pcr > 1.2 else "NEUTRAL")
        if bias in ["BULLISH", "BEARISH"]:
            score += 10
        else:
            score += 5

        return min(score, 40)

    def _calc_market_score_b(self, snap: MarketSnapshot) -> int:
        """Calculate market score for System B"""
        score = 0

        # Trend strength (10 pts)
        if snap.trend in ["BULLISH", "BEARISH"] and "STRONG" in snap.momentum:
            score += 10
        elif snap.trend in ["BULLISH", "BEARISH"]:
            score += 7
        else:
            score += 3

        # Setup alignment (10 pts)
        if snap.trend != "NEUTRAL" and snap.oi_skew != "BALANCED":
            score += 10
        elif snap.trend != "NEUTRAL" or snap.oi_skew != "BALANCED":
            score += 7
        else:
            score += 3

        return min(score, 20)

    def _calc_bullish_score_b(self, snap: MarketSnapshot) -> int:
        """Manual bullish score calculation (System B logic)"""
        score = 0

        # Trend
        if snap.trend == "BULLISH":
            score += 15
        elif "BULLISH" in snap.trend:
            score += 10

        # Momentum
        if "STRONG BULLISH" in snap.momentum:
            score += 10
        elif snap.momentum == "BULLISH":
            score += 5

        # Price vs VWAP
        if snap.price > snap.vwap:
            score += 10

        # PCR
        if snap.pcr > 1.2:
            score += 10

        return min(score, 50)

    def _calc_bearish_score_b(self, snap: MarketSnapshot) -> int:
        """Manual bearish score calculation (System B logic)"""
        score = 0

        # Trend
        if snap.trend == "BEARISH":
            score += 15
        elif "BEARISH" in snap.trend:
            score += 10

        # Momentum
        if "STRONG BEARISH" in snap.momentum:
            score += 10
        elif snap.momentum == "BEARISH":
            score += 5

        # Price vs VWAP
        if snap.price < snap.vwap:
            score += 10

        # PCR
        if snap.pcr < 0.8:
            score += 10

        return min(score, 50)

    def _calculate_divergence(self, system_a: Dict, system_b: Dict) -> Dict:
        """Calculate divergence between systems"""
        if system_a.get('status') == 'error' or system_b.get('status') == 'error':
            return {'error': True}

        if system_a.get('status') == 'no_signal' or system_b.get('status') == 'no_signal':
            return {'no_signal': True, 'system_a_signal': system_a.get('status') != 'no_signal',
                    'system_b_signal': system_b.get('status') != 'no_signal'}

        divergence = {
            'direction_agree': system_a.get('direction') == system_b.get('direction'),
            'confidence_diff': abs(system_a.get('confidence', 0) - system_b.get('confidence', 0)),
            'entry_diff': abs(system_a.get('entry', 0) - system_b.get('entry', 0)),
            'target_diff': abs(system_a.get('target', 0) - system_b.get('target', 0)),
            'sl_diff': abs(system_a.get('stop_loss', 0) - system_b.get('stop_loss', 0)),
            'rr_diff': abs(system_a.get('risk_reward', 0) - system_b.get('risk_reward', 0))
        }

        return divergence

    def generate_report(self) -> Dict:
        """Generate comprehensive comparison report"""
        report = {
            'test_summary': {
                'snapshots_tested': self.snapshots_tested,
                'total_comparisons': len(self.results)
            },
            'system_a_stats': self._calculate_system_stats('system_a'),
            'system_b_stats': self._calculate_system_stats('system_b'),
            'divergence_analysis': self._analyze_divergences(),
            'signal_agreement': self._analyze_signal_agreement()
        }
        return report

    def _calculate_system_stats(self, system_key: str) -> Dict:
        """Calculate statistics for a system"""
        signals = [r[system_key] for r in self.results if r[system_key].get('status') != 'error']
        generated = [s for s in signals if s.get('status') == 'generated']

        bullish = [s for s in generated if s.get('direction') == 'BUY']
        bearish = [s for s in generated if s.get('direction') == 'SELL']

        confidences = [s.get('confidence', 0) for s in generated]
        entries = [s.get('entry', 0) for s in generated if s.get('entry', 0) > 0]
        risk_rewards = [s.get('risk_reward', 0) for s in generated if s.get('risk_reward', 0) > 0]

        return {
            'total_snapshots': len(signals),
            'signals_generated': len(generated),
            'no_signal': len(signals) - len(generated),
            'bullish_signals': len(bullish),
            'bearish_signals': len(bearish),
            'avg_confidence': round(sum(confidences) / len(confidences), 2) if confidences else 0,
            'min_confidence': round(min(confidences), 2) if confidences else 0,
            'max_confidence': round(max(confidences), 2) if confidences else 0,
            'avg_entry': round(sum(entries) / len(entries), 2) if entries else 0,
            'avg_risk_reward': round(sum(risk_rewards) / len(risk_rewards), 2) if risk_rewards else 0
        }

    def _analyze_divergences(self) -> Dict:
        """Analyze where systems diverge"""
        divergences = [r['divergence'] for r in self.results if 'error' not in r['divergence']]

        if not divergences:
            return {'error': 'No valid divergences to analyze'}

        direction_divergence = sum(1 for d in divergences if not d.get('direction_agree', False))
        avg_confidence_diff = sum(d.get('confidence_diff', 0) for d in divergences) / len(divergences)
        avg_entry_diff = sum(d.get('entry_diff', 0) for d in divergences) / len(divergences)

        return {
            'total_comparisons': len(divergences),
            'direction_divergence_count': direction_divergence,
            'direction_divergence_pct': round(direction_divergence / len(divergences) * 100, 2) if divergences else 0,
            'avg_confidence_diff': round(avg_confidence_diff, 2),
            'avg_entry_diff': round(avg_entry_diff, 2),
            'avg_target_diff': round(sum(d.get('target_diff', 0) for d in divergences) / len(divergences), 2),
            'avg_sl_diff': round(sum(d.get('sl_diff', 0) for d in divergences) / len(divergences), 2)
        }

    def _analyze_signal_agreement(self) -> Dict:
        """Analyze how often systems agree"""
        agreements = {
            'both_generated': 0,
            'both_no_signal': 0,
            'system_a_only': 0,
            'system_b_only': 0,
            'direction_match': 0
        }

        for result in self.results:
            a_sig = result['system_a'].get('status') == 'generated'
            b_sig = result['system_b'].get('status') == 'generated'

            if a_sig and b_sig:
                agreements['both_generated'] += 1
                if result['system_a'].get('direction') == result['system_b'].get('direction'):
                    agreements['direction_match'] += 1
            elif not a_sig and not b_sig:
                agreements['both_no_signal'] += 1
            elif a_sig:
                agreements['system_a_only'] += 1
            else:
                agreements['system_b_only'] += 1

        total = sum(agreements.values())

        return {
            'total_comparisons': total,
            'both_generated': agreements['both_generated'],
            'both_generated_pct': round(agreements['both_generated'] / total * 100, 2) if total else 0,
            'both_no_signal': agreements['both_no_signal'],
            'system_a_only': agreements['system_a_only'],
            'system_b_only': agreements['system_b_only'],
            'direction_match_when_both': agreements['direction_match'],
            'direction_match_pct': round(agreements['direction_match'] / agreements['both_generated'] * 100, 2)
                                        if agreements['both_generated'] > 0 else 0
        }


def generate_test_scenarios() -> List[MarketSnapshot]:
    """Generate diverse market scenarios for testing"""
    scenarios = []

    # Scenario 1: Strong Bullish (RSI oversold, EMA golden cross, price > VWAP)
    scenarios.append(MarketSnapshot(
        symbol='NIFTY',
        price=20000,
        rsi=35,
        ema9=20100,
        ema50=20000,
        macd_hist=50,
        vwap=19900,
        trend='BULLISH',
        momentum='STRONG BULLISH',
        pcr=0.9,
        support=19800,
        resistance=20200,
        oi_skew='BALANCED'
    ))

    # Scenario 2: Strong Bearish (RSI overbought, death cross, price < VWAP)
    scenarios.append(MarketSnapshot(
        symbol='NIFTY',
        price=20000,
        rsi=75,
        ema9=19900,
        ema50=20000,
        macd_hist=-50,
        vwap=20100,
        trend='BEARISH',
        momentum='STRONG BEARISH',
        pcr=1.3,
        support=19800,
        resistance=20200,
        oi_skew='BALANCED'
    ))

    # Scenario 3: Moderate Bullish
    scenarios.append(MarketSnapshot(
        symbol='NIFTY',
        price=20000,
        rsi=45,
        ema9=20050,
        ema50=20000,
        macd_hist=20,
        vwap=19950,
        trend='BULLISH',
        momentum='BULLISH',
        pcr=1.0,
        support=19800,
        resistance=20200,
        oi_skew='BALANCED'
    ))

    # Scenario 4: Neutral/Choppy
    scenarios.append(MarketSnapshot(
        symbol='NIFTY',
        price=20000,
        rsi=50,
        ema9=20000,
        ema50=20000,
        macd_hist=0,
        vwap=20000,
        trend='NEUTRAL',
        momentum='NEUTRAL',
        pcr=1.1,
        support=19900,
        resistance=20100,
        oi_skew='BALANCED'
    ))

    # Scenario 5: BANKNIFTY Strong Bullish
    scenarios.append(MarketSnapshot(
        symbol='BANKNIFTY',
        price=51000,
        rsi=30,
        ema9=51200,
        ema50=51000,
        macd_hist=100,
        vwap=50900,
        trend='BULLISH',
        momentum='STRONG BULLISH',
        pcr=0.85,
        support=50800,
        resistance=51200,
        oi_skew='BALANCED'
    ))

    # Scenario 6: BANKNIFTY Strong Bearish
    scenarios.append(MarketSnapshot(
        symbol='BANKNIFTY',
        price=51000,
        rsi=78,
        ema9=50800,
        ema50=51000,
        macd_hist=-100,
        vwap=51100,
        trend='BEARISH',
        momentum='STRONG BEARISH',
        pcr=1.4,
        support=50800,
        resistance=51200,
        oi_skew='BALANCED'
    ))

    # Scenario 7: FINNIFTY Bullish with high PCR
    scenarios.append(MarketSnapshot(
        symbol='FINNIFTY',
        price=23500,
        rsi=40,
        ema9=23600,
        ema50=23500,
        macd_hist=30,
        vwap=23450,
        trend='BULLISH',
        momentum='BULLISH',
        pcr=1.25,
        support=23300,
        resistance=23700,
        oi_skew='PUT_HEAVY'
    ))

    # Scenario 8: FINNIFTY Bearish
    scenarios.append(MarketSnapshot(
        symbol='FINNIFTY',
        price=23500,
        rsi=68,
        ema9=23400,
        ema50=23500,
        macd_hist=-25,
        vwap=23550,
        trend='BEARISH',
        momentum='BEARISH',
        pcr=0.75,
        support=23300,
        resistance=23700,
        oi_skew='CALL_HEAVY'
    ))

    # Scenario 9: Extreme RSI oversold (potential bounce)
    scenarios.append(MarketSnapshot(
        symbol='NIFTY',
        price=19500,
        rsi=15,
        ema9=19400,
        ema50=19500,
        macd_hist=10,
        vwap=19450,
        trend='BEARISH',
        momentum='STRONG BEARISH',
        pcr=1.5,
        support=19300,
        resistance=19700,
        oi_skew='BALANCED'
    ))

    # Scenario 10: Extreme RSI overbought (potential pullback)
    scenarios.append(MarketSnapshot(
        symbol='NIFTY',
        price=20500,
        rsi=88,
        ema9=20600,
        ema50=20500,
        macd_hist=80,
        vwap=20550,
        trend='BULLISH',
        momentum='STRONG BULLISH',
        pcr=0.7,
        support=20300,
        resistance=20700,
        oi_skew='BALANCED'
    ))

    return scenarios


def main():
    print("="*80)
    print("SIGNAL ENGINE COMPARATIVE ANALYSIS")
    print("Quantitative Research Auditor Framework")
    print("="*80)

    # Create comparison framework
    comparison = SignalComparison()

    # Generate test scenarios
    scenarios = generate_test_scenarios()
    print(f"\n📊 Generated {len(scenarios)} test market scenarios")
    print("-" * 80)

    # Test each scenario
    for i, scenario in enumerate(scenarios, 1):
        result = comparison.test_snapshot(scenario)

        print(f"\n[Scenario {i}] {scenario.symbol} @ {scenario.price}")
        print(f"  Market: RSI={scenario.rsi:.0f}, Trend={scenario.trend}, Momentum={scenario.momentum}")

        a = result['system_a']
        b = result['system_b']

        print(f"  System A: {a.get('direction', 'ERROR')} | Conf={a.get('confidence', 0):.0f} | Entry={a.get('entry', 0):.0f}")
        print(f"  System B: {b.get('direction', 'ERROR')} | Conf={b.get('confidence', 0):.0f} | Entry={b.get('entry', 0):.0f}")

        div = result['divergence']
        if 'error' not in div and 'no_signal' not in div:
            print(f"  Divergence: Dir={div.get('direction_agree')}, ConfDiff={div.get('confidence_diff', 0):.0f}, EntryDiff={div.get('entry_diff', 0):.0f}")

    # Generate report
    print("\n" + "="*80)
    print("COMPREHENSIVE ANALYSIS REPORT")
    print("="*80)

    report = comparison.generate_report()

    # Print detailed report
    print("\n1. TEST SUMMARY")
    print(f"   Snapshots Tested: {report['test_summary']['snapshots_tested']}")
    print(f"   Total Comparisons: {report['test_summary']['total_comparisons']}")

    print("\n2. SYSTEM A (SignalsEngine) STATISTICS")
    stats_a = report['system_a_stats']
    print(f"   Total Snapshots Processed: {stats_a['total_snapshots']}")
    print(f"   Signals Generated: {stats_a['signals_generated']}")
    print(f"   No Signal: {stats_a['no_signal']}")
    print(f"   Bullish Signals: {stats_a['bullish_signals']}")
    print(f"   Bearish Signals: {stats_a['bearish_signals']}")
    print(f"   Average Confidence: {stats_a['avg_confidence']:.2f}")
    print(f"   Confidence Range: {stats_a['min_confidence']:.2f} - {stats_a['max_confidence']:.2f}")
    print(f"   Average Risk/Reward: {stats_a['avg_risk_reward']:.2f}")

    print("\n3. SYSTEM B (SignalGenerator) STATISTICS")
    stats_b = report['system_b_stats']
    print(f"   Total Snapshots Processed: {stats_b['total_snapshots']}")
    print(f"   Signals Generated: {stats_b['signals_generated']}")
    print(f"   No Signal: {stats_b['no_signal']}")
    print(f"   Bullish Signals: {stats_b['bullish_signals']}")
    print(f"   Bearish Signals: {stats_b['bearish_signals']}")
    print(f"   Average Confidence: {stats_b['avg_confidence']:.2f}")
    print(f"   Confidence Range: {stats_b['min_confidence']:.2f} - {stats_b['max_confidence']:.2f}")
    print(f"   Average Risk/Reward: {stats_b['avg_risk_reward']:.2f}")

    print("\n4. DIVERGENCE ANALYSIS")
    div_analysis = report['divergence_analysis']
    if 'error' not in div_analysis:
        print(f"   Total Comparisons: {div_analysis['total_comparisons']}")
        print(f"   Direction Divergences: {div_analysis['direction_divergence_count']} ({div_analysis['direction_divergence_pct']:.1f}%)")
        print(f"   Avg Confidence Difference: {div_analysis['avg_confidence_diff']:.2f} points")
        print(f"   Avg Entry Difference: {div_analysis['avg_entry_diff']:.2f} points")
        print(f"   Avg Target Difference: {div_analysis['avg_target_diff']:.2f} points")
        print(f"   Avg Stop Loss Difference: {div_analysis['avg_sl_diff']:.2f} points")

    print("\n5. SIGNAL AGREEMENT")
    agreement = report['signal_agreement']
    print(f"   Both Systems Generated Signal: {agreement['both_generated']} ({agreement['both_generated_pct']:.1f}%)")
    print(f"   Both Systems No Signal: {agreement['both_no_signal']}")
    print(f"   System A Only: {agreement['system_a_only']}")
    print(f"   System B Only: {agreement['system_b_only']}")
    print(f"   Direction Match (when both generate): {agreement['direction_match_when_both']} ({agreement['direction_match_pct']:.1f}%)")

    print("\n" + "="*80)
    print("EVIDENCE SUMMARY")
    print("="*80)

    # Determine findings
    findings = {
        'system_a_more_aggressive': stats_a['signals_generated'] > stats_b['signals_generated'],
        'system_b_more_selective': stats_b['signals_generated'] < stats_a['signals_generated'],
        'confidence_gap': abs(stats_a['avg_confidence'] - stats_b['avg_confidence']),
        'frequent_divergence': div_analysis.get('direction_divergence_pct', 0) > 10 if 'error' not in div_analysis else False,
        'entry_gap': div_analysis.get('avg_entry_diff', 0),
        'direction_agreement_rate': agreement['direction_match_pct']
    }

    print(f"\n✓ System A is more aggressive: {findings['system_a_more_aggressive']}")
    print(f"  (Generates {stats_a['signals_generated']} vs {stats_b['signals_generated']} signals)")

    print(f"\n✓ Average confidence gap: {findings['confidence_gap']:.2f} points")
    print(f"  System A: {stats_a['avg_confidence']:.2f} vs System B: {stats_b['avg_confidence']:.2f}")

    print(f"\n✓ Direction divergence rate: {div_analysis.get('direction_divergence_pct', 0):.1f}%")
    print(f"  (Systems disagree on direction {div_analysis.get('direction_divergence_count', 0)} times)")

    print(f"\n✓ Average entry price difference: {findings['entry_gap']:.2f} points")
    print(f"  (When generating signals, systems recommend different entries)")

    print(f"\n✓ Direction agreement rate: {findings['direction_agreement_rate']:.1f}%")
    print(f"  (When both generate signals, they agree {agreement['direction_match_when_both']} times)")

    # Save report to JSON
    with open('/Users/anshhdodia/Desktop/tradosphere_github/engine_comparison_report.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)

    print("\n✓ Report saved to: engine_comparison_report.json")
    print("="*80)


if __name__ == "__main__":
    main()
