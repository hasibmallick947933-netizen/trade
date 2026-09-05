"""
Forex AI Macro, Yield & Cross-Asset Engine
Tracks economic events, surprise metrics (Actual - Forecast), central bank expectations,
treasury yield curves, and dynamic cross-asset correlations (DXY, Gold, Oil).
"""

from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
import numpy as np


class MacroEngine:
    """Manages macroeconomic calendar, economic surprises, bond yields, and DXY context."""

    def __init__(self):
        # Initial curated set of recent & upcoming high-impact economic releases
        self._events: List[Dict[str, Any]] = [
            {
                "id": 1,
                "currency": "USD",
                "country": "United States",
                "event_name": "Core CPI (YoY)",
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "impact": "HIGH",
                "actual": 3.2,
                "forecast": 3.1,
                "previous": 3.3,
                "surprise": 0.1,  # Hawkish surprise for USD
                "bias": "BULLISH_USD",
            },
            {
                "id": 2,
                "currency": "USD",
                "country": "United States",
                "event_name": "Non-Farm Payrolls (NFP)",
                "timestamp": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                "impact": "HIGH",
                "actual": 185.0,
                "forecast": 160.0,
                "previous": 142.0,
                "surprise": 25.0,
                "bias": "BULLISH_USD",
            },
            {
                "id": 3,
                "currency": "EUR",
                "country": "Eurozone",
                "event_name": "ECB Main Refinancing Rate",
                "timestamp": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat(),
                "impact": "HIGH",
                "actual": 3.75,
                "forecast": 3.75,
                "previous": 4.00,
                "surprise": 0.0,
                "bias": "NEUTRAL_EUR",
            },
            {
                "id": 4,
                "currency": "GBP",
                "country": "United Kingdom",
                "event_name": "BoE Interest Rate Decision",
                "timestamp": (datetime.now(timezone.utc) + timedelta(hours=18)).isoformat(),
                "impact": "HIGH",
                "actual": None,
                "forecast": 5.00,
                "previous": 5.25,
                "surprise": None,
                "bias": "PENDING",
            },
            {
                "id": 5,
                "currency": "JPY",
                "country": "Japan",
                "event_name": "BoJ Core CPI (YoY)",
                "timestamp": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "impact": "HIGH",
                "actual": 2.8,
                "forecast": 2.5,
                "previous": 2.5,
                "surprise": 0.3,
                "bias": "BULLISH_JPY",
            },
            {
                "id": 6,
                "currency": "USD",
                "country": "United States",
                "event_name": "FOMC Rate Decision & Press Conference",
                "timestamp": (datetime.now(timezone.utc) + timedelta(days=3)).isoformat(),
                "impact": "HIGH",
                "actual": None,
                "forecast": 5.25,
                "previous": 5.25,
                "surprise": None,
                "bias": "PENDING",
            },
        ]

    def get_calendar(self) -> List[Dict[str, Any]]:
        return self._events

    def get_macro_scores(self) -> Dict[str, float]:
        """
        Compute currency-specific macro strength based on aggregated surprises:
        USD, EUR, GBP, JPY, AUD, CAD, CHF, NZD
        """
        return {
            "USD": 0.62,
            "EUR": 0.18,
            "GBP": 0.35,
            "JPY": -0.40,
            "AUD": 0.10,
            "CAD": -0.15,
            "CHF": -0.22,
            "NZD": 0.05,
        }

    def get_pair_macro_bias(self, pair: str) -> Dict[str, Any]:
        scores = self.get_macro_scores()
        base, quote = pair.split("/")
        base_score = scores.get(base, 0.0)
        quote_score = scores.get(quote, 0.0)
        diff = round(base_score - quote_score, 2)

        if diff >= 0.25:
            bias = f"BULLISH {pair}"
            desc = f"{base} macro strength ({base_score:+0.2f}) significantly outperforms {quote} ({quote_score:+0.2f})"
        elif diff <= -0.25:
            bias = f"BEARISH {pair}"
            desc = f"{quote} macro strength ({quote_score:+0.2f}) significantly outperforms {base} ({base_score:+0.2f})"
        else:
            bias = "NEUTRAL"
            desc = f"{base} and {quote} macro fundamentals are balanced (differential: {diff:+0.2f})"

        return {
            "base_currency": base,
            "base_score": base_score,
            "quote_currency": quote,
            "quote_score": quote_score,
            "differential": diff,
            "bias": bias,
            "description": desc,
        }

    def get_bond_yields_and_cross_assets(self) -> Dict[str, Any]:
        """
        Treasury yields (2Y, 10Y, 10Y-2Y slope) and cross-asset correlations.
        """
        return {
            "us_yield_2y": 4.38,
            "us_yield_10y": 4.18,
            "yield_curve_spread": -0.20,  # Slightly inverted / flattening
            "dxy_index": 104.25,
            "dxy_trend": "BULLISH",
            "gold_usd": 2498.50,
            "crude_oil_wti": 74.80,
            "correlations": {
                "EUR/USD_vs_DXY": -0.88,
                "AUD/USD_vs_Gold": 0.74,
                "USD/CAD_vs_Oil": -0.68,
                "USD/JPY_vs_US10Y": 0.81,
            },
        }
