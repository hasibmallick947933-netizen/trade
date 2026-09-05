"""
Forex AI Multi-Timeframe Analysis Engine
Synthesizes trend and momentum across 1D, 4H, 1H, 15M, and 5M timeframes.
Evaluates higher-timeframe context, medium-timeframe setup, and lower-timeframe entry trigger.
"""

from typing import Dict, Any, List
from data.providers.base import MarketDataProvider
from backend.app.services.technical_analysis import TechnicalAnalysisEngine
from backend.app.services.market_structure import MarketStructureEngine


class MultiTimeframeEngine:
    """Evaluates multi-timeframe directional confluence and structural alignment."""

    def __init__(self, provider: MarketDataProvider):
        self.provider = provider
        self.timeframes = ["1D", "4H", "1H", "15M", "5M"]

    async def analyze_pair(self, pair: str) -> Dict[str, Any]:
        """
        Run parallel analysis across all 5 key timeframes.
        """
        tf_results = {}

        for tf in self.timeframes:
            df = await self.provider.get_candles(pair, tf, limit=60)
            df_ind = TechnicalAnalysisEngine.calculate_indicators(df)
            structure = MarketStructureEngine.analyze_structure(df_ind)

            c = float(df_ind["close"].iloc[-1])
            ema_20 = float(df_ind["ema_20"].iloc[-1])
            ema_50 = float(df_ind["ema_50"].iloc[-1])
            rsi = float(df_ind["rsi_14"].iloc[-1])
            adx = float(df_ind["adx_14"].iloc[-1])

            # Determine timeframe-specific bias
            bull_votes = 0
            bear_votes = 0

            if c > ema_20 > ema_50:
                bull_votes += 2
            elif c < ema_20 < ema_50:
                bear_votes += 2

            if rsi > 52:
                bull_votes += 1
            elif rsi < 48:
                bear_votes += 1

            if structure["trend"] == "BULLISH":
                bull_votes += 2
            elif structure["trend"] == "BEARISH":
                bear_votes += 2

            if bull_votes >= 3 and bull_votes > bear_votes:
                bias = "BULLISH"
            elif bear_votes >= 3 and bear_votes > bull_votes:
                bias = "BEARISH"
            else:
                bias = "NEUTRAL"

            tf_results[tf] = {
                "bias": bias,
                "close": round(c, 5),
                "ema_20": round(ema_20, 5),
                "ema_50": round(ema_50, 5),
                "rsi_14": round(rsi, 1),
                "adx_14": round(adx, 1),
                "structure": structure["trend"],
                "bos": structure["bos"],
                "choch": structure["choch"],
            }

        # Hierarchy synthesis
        htf_bias = "BULLISH" if tf_results["1D"]["bias"] == "BULLISH" and tf_results["4H"]["bias"] == "BULLISH" else (
            "BEARISH" if tf_results["1D"]["bias"] == "BEARISH" and tf_results["4H"]["bias"] == "BEARISH" else "MIXED"
        )
        mtf_bias = tf_results["1H"]["bias"]
        ltf_bias = "BULLISH" if tf_results["15M"]["bias"] == "BULLISH" or tf_results["5M"]["bias"] == "BULLISH" else (
            "BEARISH" if tf_results["15M"]["bias"] == "BEARISH" or tf_results["5M"]["bias"] == "BEARISH" else "NEUTRAL"
        )

        # Multi-timeframe alignment score (-1.0 to +1.0)
        weights = {"1D": 0.30, "4H": 0.25, "1H": 0.20, "15M": 0.15, "5M": 0.10}
        score = 0.0
        for tf, w in weights.items():
            b = tf_results[tf]["bias"]
            val = 1.0 if b == "BULLISH" else (-1.0 if b == "BEARISH" else 0.0)
            score += val * w

        if score >= 0.70:
            alignment = "STRONG BULLISH"
        elif score >= 0.35:
            alignment = "MODERATE BULLISH"
        elif score <= -0.70:
            alignment = "STRONG BEARISH"
        elif score <= -0.35:
            alignment = "MODERATE BEARISH"
        else:
            alignment = "MIXED"

        return {
            "pair": pair,
            "alignment": alignment,
            "alignment_score": round(score, 2),
            "higher_timeframe": htf_bias,
            "medium_timeframe": mtf_bias,
            "lower_timeframe": ltf_bias,
            "timeframes": tf_results,
        }
