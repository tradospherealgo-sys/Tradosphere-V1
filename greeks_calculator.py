"""
Synthetic Greeks Calculator - Black-Scholes Option Greeks
Generates Delta and Gamma for options when broker SDK doesn't provide them.
Uses Implied Volatility approximation from ATM straddle premium.
"""

import math
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta


class BlackScholesGreeks:
    """Calculate option Greeks using Black-Scholes model"""

    # Risk-free rate (Indian context: typical repo rate around 5-6%)
    RISK_FREE_RATE = 0.055

    @staticmethod
    def estimate_iv_from_atm_straddle(spot_price: float, atm_call_ltp: float,
                                       atm_put_ltp: float, days_to_expiry: int = 1) -> float:
        """
        Estimate Implied Volatility from ATM straddle premium.
        Straddle price ≈ spot * IV * sqrt(T / 365)

        Args:
            spot_price: Current underlying price
            atm_call_ltp: ATM Call LTP
            atm_put_ltp: ATM Put LTP
            days_to_expiry: Days to option expiry (default: 1 day for daily expiry)

        Returns:
            Estimated IV as decimal (e.g., 0.25 = 25%)
        """
        try:
            straddle_price = atm_call_ltp + atm_put_ltp

            # Avoid division by zero
            if spot_price <= 0:
                return 0.20  # Default to 20% IV

            time_to_expiry = days_to_expiry / 365.0
            if time_to_expiry <= 0:
                time_to_expiry = 1/365.0  # Minimum 1 day

            # IV ≈ straddle_price / (spot * sqrt(T))
            iv = straddle_price / (spot_price * math.sqrt(time_to_expiry))

            # Clamp IV between 5% and 100%
            iv = max(0.05, min(1.0, iv))

            return iv
        except Exception as e:
            print(f"⚠️  IV estimation error: {e}")
            return 0.25  # Default to 25% IV


    @staticmethod
    def calculate_d1_d2(spot_price: float, strike: float, time_to_expiry: float,
                       volatility: float, rate: float = RISK_FREE_RATE) -> Tuple[float, float]:
        """
        Calculate d1 and d2 from Black-Scholes formula

        d1 = [ln(S/K) + (r + σ²/2)T] / (σ√T)
        d2 = d1 - σ√T
        """
        try:
            if volatility <= 0 or spot_price <= 0 or time_to_expiry <= 0:
                return 0.0, 0.0

            sqrt_t = math.sqrt(time_to_expiry)
            ln_s_k = math.log(spot_price / strike) if strike > 0 else 0

            numerator = ln_s_k + (rate + (volatility ** 2) / 2) * time_to_expiry
            d1 = numerator / (volatility * sqrt_t)
            d2 = d1 - (volatility * sqrt_t)

            return d1, d2
        except Exception as e:
            print(f"⚠️  d1/d2 calculation error: {e}")
            return 0.0, 0.0


    @staticmethod
    def normal_cdf(x: float) -> float:
        """Cumulative normal distribution function (approximation)"""
        return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0


    @staticmethod
    def normal_pdf(x: float) -> float:
        """Probability density function for standard normal"""
        return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


    @classmethod
    def calculate_call_delta(cls, spot_price: float, strike: float,
                            time_to_expiry: float, volatility: float) -> float:
        """
        Calculate Call Option Delta
        Delta = N(d1)
        Range: 0 to 1

        Interpretation:
        - Delta 0.5: ATM, 50% chance of profit
        - Delta 0.7: ITM, 70% probability of finishing ITM
        - Delta 0.3: OTM, only 30% probability
        """
        try:
            d1, _ = cls.calculate_d1_d2(spot_price, strike, time_to_expiry, volatility)
            delta = cls.normal_cdf(d1)
            return round(delta, 4)
        except Exception as e:
            print(f"⚠️  Call Delta error: {e}")
            return 0.5  # Return neutral delta


    @classmethod
    def calculate_put_delta(cls, spot_price: float, strike: float,
                           time_to_expiry: float, volatility: float) -> float:
        """
        Calculate Put Option Delta
        Delta = N(d1) - 1
        Range: -1 to 0

        Interpretation:
        - Delta -0.5: ATM put
        - Delta -0.7: ITM put (strike above spot)
        - Delta -0.3: OTM put
        """
        try:
            call_delta = cls.calculate_call_delta(spot_price, strike, time_to_expiry, volatility)
            put_delta = call_delta - 1.0
            return round(put_delta, 4)
        except Exception as e:
            print(f"⚠️  Put Delta error: {e}")
            return -0.5  # Return neutral delta


    @classmethod
    def calculate_gamma(cls, spot_price: float, strike: float,
                       time_to_expiry: float, volatility: float) -> float:
        """
        Calculate Gamma (rate of change of Delta)
        Gamma = N'(d1) / (S * σ * √T)

        Interpretation:
        - Gamma 0.05: Delta changes by 0.05 for every 1 point move in spot
        - Higher gamma = higher risk of adverse moves
        - ATM options have highest gamma
        - Far OTM/ITM options have lower gamma
        """
        try:
            d1, _ = cls.calculate_d1_d2(spot_price, strike, time_to_expiry, volatility)
            sqrt_t = math.sqrt(time_to_expiry)

            if spot_price <= 0 or volatility <= 0 or sqrt_t <= 0:
                return 0.0

            gamma = cls.normal_pdf(d1) / (spot_price * volatility * sqrt_t)
            return round(gamma, 6)
        except Exception as e:
            print(f"⚠️  Gamma error: {e}")
            return 0.0


    @classmethod
    def calculate_vega(cls, spot_price: float, strike: float,
                      time_to_expiry: float, volatility: float) -> float:
        """
        Calculate Vega (sensitivity to volatility changes)
        Vega = S * N'(d1) * √T / 100

        Interpretation:
        - Positive vega: Benefits from IV increase
        - Long options = long vega
        - Short options = short vega
        """
        try:
            d1, _ = cls.calculate_d1_d2(spot_price, strike, time_to_expiry, volatility)
            sqrt_t = math.sqrt(time_to_expiry)
            vega = spot_price * cls.normal_pdf(d1) * sqrt_t / 100.0
            return round(vega, 4)
        except Exception as e:
            print(f"⚠️  Vega error: {e}")
            return 0.0


    @classmethod
    def calculate_theta(cls, spot_price: float, strike: float,
                       time_to_expiry: float, volatility: float,
                       is_call: bool = True) -> float:
        """
        Calculate Theta (time decay)
        Theta = -(S * N'(d1) * σ) / (2 * √T) - r*K*e^(-r*T)*N(±d2)

        Interpretation:
        - Negative = long options lose value with time
        - Positive = short options gain with time
        - Theta accelerates near expiry
        """
        try:
            d1, d2 = cls.calculate_d1_d2(spot_price, strike, time_to_expiry, volatility)
            sqrt_t = math.sqrt(time_to_expiry)
            rate = cls.RISK_FREE_RATE

            if spot_price <= 0 or sqrt_t <= 0:
                return 0.0

            first_term = -(spot_price * cls.normal_pdf(d1) * volatility) / (2 * sqrt_t)
            second_term = -rate * strike * math.exp(-rate * time_to_expiry)

            if is_call:
                second_term *= cls.normal_cdf(d2)
            else:
                second_term *= -cls.normal_cdf(-d2)

            theta = (first_term + second_term) / 365.0  # Per day
            return round(theta, 4)
        except Exception as e:
            print(f"⚠️  Theta error: {e}")
            return 0.0


class GreeksInjector:
    """Inject calculated Greeks into option chain data"""

    @staticmethod
    def inject_greeks_into_strikes(strikes_data: list, spot_price: float,
                                   atm_call_ltp: float, atm_put_ltp: float,
                                   days_to_expiry: int = 1) -> list:
        """
        Inject Delta and Gamma into option chain strikes

        Args:
            strikes_data: List of strike dicts with 'ce' and 'pe' sub-dicts
            spot_price: Current spot price
            atm_call_ltp: ATM call LTP for IV estimation
            atm_put_ltp: ATM put LTP for IV estimation
            days_to_expiry: Days to expiry (default 1 for daily expiry)

        Returns:
            Enhanced strikes_data with delta and gamma injected
        """
        try:
            # Estimate IV from ATM straddle
            iv = BlackScholesGreeks.estimate_iv_from_atm_straddle(
                spot_price, atm_call_ltp, atm_put_ltp, days_to_expiry
            )

            time_to_expiry = days_to_expiry / 365.0

            for strike_data in strikes_data:
                strike = strike_data.get('strike', 0)

                if strike <= 0:
                    continue

                # Calculate Greeks for CALL
                if 'ce' in strike_data and strike_data['ce']:
                    call_delta = BlackScholesGreeks.calculate_call_delta(
                        spot_price, strike, time_to_expiry, iv
                    )
                    call_gamma = BlackScholesGreeks.calculate_gamma(
                        spot_price, strike, time_to_expiry, iv
                    )
                    call_vega = BlackScholesGreeks.calculate_vega(
                        spot_price, strike, time_to_expiry, iv
                    )
                    call_theta = BlackScholesGreeks.calculate_theta(
                        spot_price, strike, time_to_expiry, iv, is_call=True
                    )

                    strike_data['ce']['delta'] = call_delta
                    strike_data['ce']['gamma'] = call_gamma
                    strike_data['ce']['vega'] = call_vega
                    strike_data['ce']['theta'] = call_theta
                    strike_data['ce']['iv'] = round(iv * 100, 2)  # As percentage

                # Calculate Greeks for PUT
                if 'pe' in strike_data and strike_data['pe']:
                    put_delta = BlackScholesGreeks.calculate_put_delta(
                        spot_price, strike, time_to_expiry, iv
                    )
                    put_gamma = BlackScholesGreeks.calculate_gamma(
                        spot_price, strike, time_to_expiry, iv
                    )
                    put_vega = BlackScholesGreeks.calculate_vega(
                        spot_price, strike, time_to_expiry, iv
                    )
                    put_theta = BlackScholesGreeks.calculate_theta(
                        spot_price, strike, time_to_expiry, iv, is_call=False
                    )

                    strike_data['pe']['delta'] = put_delta
                    strike_data['pe']['gamma'] = put_gamma
                    strike_data['pe']['vega'] = put_vega
                    strike_data['pe']['theta'] = put_theta
                    strike_data['pe']['iv'] = round(iv * 100, 2)  # As percentage

            return strikes_data

        except Exception as e:
            print(f"❌ Error injecting Greeks: {e}")
            return strikes_data


if __name__ == "__main__":
    # Test Greeks calculation
    print("\n" + "="*70)
    print("🧮 SYNTHETIC GREEKS CALCULATOR - TEST")
    print("="*70)

    spot = 23161.60
    strike_atm = 23161.60
    strike_otm_call = 23250.00
    strike_otm_put = 23050.00

    atm_call = 300.0
    atm_put = 280.0

    # Estimate IV
    iv = BlackScholesGreeks.estimate_iv_from_atm_straddle(spot, atm_call, atm_put, days_to_expiry=1)
    print(f"\n📊 Estimated IV (from ATM straddle): {iv*100:.2f}%")

    time_to_expiry = 1/365.0

    # ATM Call
    call_delta = BlackScholesGreeks.calculate_call_delta(spot, strike_atm, time_to_expiry, iv)
    call_gamma = BlackScholesGreeks.calculate_gamma(spot, strike_atm, time_to_expiry, iv)
    print(f"\n📈 ATM CALL ({strike_atm}):")
    print(f"   Delta: {call_delta} (expected ~0.5)")
    print(f"   Gamma: {call_gamma}")

    # OTM Call
    call_delta_otm = BlackScholesGreeks.calculate_call_delta(spot, strike_otm_call, time_to_expiry, iv)
    call_gamma_otm = BlackScholesGreeks.calculate_gamma(spot, strike_otm_call, time_to_expiry, iv)
    print(f"\n📈 OTM CALL ({strike_otm_call}):")
    print(f"   Delta: {call_delta_otm} (expected <0.5)")
    print(f"   Gamma: {call_gamma_otm}")

    # OTM Put
    put_delta_otm = BlackScholesGreeks.calculate_put_delta(spot, strike_otm_put, time_to_expiry, iv)
    put_gamma_otm = BlackScholesGreeks.calculate_gamma(spot, strike_otm_put, time_to_expiry, iv)
    print(f"\n📉 OTM PUT ({strike_otm_put}):")
    print(f"   Delta: {put_delta_otm} (expected >-0.5)")
    print(f"   Gamma: {put_gamma_otm}")

    print("\n" + "="*70)
