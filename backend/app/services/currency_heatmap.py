"""
Forex AI Currency Strength and Relative Momentum Engine
Computes relative strength indices across 8 major currencies (USD, EUR, GBP, JPY, AUD, CAD, CHF, NZD)
by aggregating performance against all cross pairs across multiple time horizons.
"""

from typing import Dict, Any, List
import pandas as pd
from data.providers.base import MarketDataProvider


MAJOR_CURRENCIES = ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "NZD"]


class CurrencyHeatmapEngine:
    """Calculates cross-currency relative strength metrics."""

    def __init__(self, provider: MarketDataProvider):
        self.provider = provider

    async def calculate_strength(self, timeframe: str = "1H") -> Dict[str, Any]:
        """
        Calculates normalized currency strength score from -1.0 to +1.0 for each currency.
        """
        pairs = self.provider.get_supported_pairs()
        returns = {}

        # Fetch recent returns for all supported pairs
        for pair in pairs:
            try:
                df = await self.provider.get_candles(pair, timeframe, limit=10)
                if len(df) >= 2:
                    p_now = df["close"].iloc[-1]
                    p_prev = df["close"].iloc[-5] if len(df) >= 5 else df["close"].iloc[0]
                    ret = (p_now - p_prev) / p_prev
                    returns[pair] = ret
            except Exception:
                continue

        # Accumulate score for base and quote
        scores = {cur: 0.0 for cur in MAJOR_CURRENCIES}
        counts = {cur: 0 for cur in MAJOR_CURRENCIES}

        for pair, ret in returns.items():
            base, quote = pair.split("/")
            if base in scores:
                scores[base] += ret
                counts[base] += 1
            if quote in scores:
                scores[quote] -= ret  # Inverse for quote currency
                counts[quote] += 1

        # Average and normalize to [-1.0, 1.0] scale
        raw_strengths = {}
        for cur in MAJOR_CURRENCIES:
            if counts[cur] > 0:
                raw_strengths[cur] = scores[cur] / counts[cur]
            else:
                raw_strengths[cur] = 0.0

        max_abs = max(abs(v) for v in raw_strengths.values()) if raw_strengths else 1.0
        max_abs = max(max_abs, 1e-6)

        normalized = {}
        for cur, val in raw_strengths.items():
            # Normalized between -1.0 and +1.0
            norm_val = round(val / max_abs, 2)
            normalized[cur] = norm_val

        # Sort currencies by strength descending
        ranked = sorted(normalized.items(), key=lambda x: x[1], reverse=True)

        strongest = ranked[0][0]
        weakest = ranked[-1][0]

        return {
            "timeframe": timeframe,
            "strengths": normalized,
            "rankings": [{"currency": c, "score": s} for c, s in ranked],
            "strongest": strongest,
            "weakest": weakest,
            "best_long_opportunity": f"{strongest}/{weakest}" if f"{strongest}/{weakest}" in pairs else f"{weakest}/{strongest}",
        }
