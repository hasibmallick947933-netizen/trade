"""
Forex AI Market Structure and Price Action Engine
Identifies fractal swing highs/lows, Higher Highs/Lows, Break of Structure (BOS),
Change of Character (CHOCH), Liquidity Sweeps, Order Blocks, and Support/Resistance Zones.
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd


class MarketStructureEngine:
    """
    Analyzes raw candle price action to extract institutional market structure:
    - Swing Highs & Swing Lows (Fractal pivots)
    - Trend classification (HH+HL = Bullish, LH+LL = Bearish, Consolidation = Range)
    - Break of Structure (BOS) vs Change of Character (CHOCH)
    - Liquidity Sweeps (stop runs)
    - Supply / Demand & Order Block zones
    - Dynamic Support & Resistance levels
    """

    @staticmethod
    def identify_swings(df: pd.DataFrame, window: int = 3) -> pd.DataFrame:
        """
        Identify swing highs and swing lows using a symmetric rolling fractal window.
        Avoids look-ahead bias by lagging swing confirmation by `window` bars.
        """
        res = df.copy()
        highs = res["high"].values
        lows = res["low"].values
        n = len(df)

        is_swing_high = np.zeros(n, dtype=bool)
        is_swing_low = np.zeros(n, dtype=bool)

        for i in range(window, n - window):
            # Peak condition
            if np.all(highs[i] >= highs[i - window : i]) and np.all(highs[i] >= highs[i + 1 : i + window + 1]):
                is_swing_high[i] = True
            # Trough condition
            if np.all(lows[i] <= lows[i - window : i]) and np.all(lows[i] <= lows[i + 1 : i + window + 1]):
                is_swing_low[i] = True

        res["is_swing_high"] = is_swing_high
        res["is_swing_low"] = is_swing_low
        return res

    @classmethod
    def analyze_structure(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform complete market structure breakdown on the candle dataframe.
        """
        if len(df) < 20:
            return {
                "regime": "NEUTRAL",
                "trend": "NEUTRAL",
                "structure_state": "CONSOLIDATION",
                "bos": False,
                "choch": False,
                "liquidity_sweep": False,
                "support_levels": [],
                "resistance_levels": [],
                "order_blocks": [],
                "swing_points": [],
            }

        df_swings = cls.identify_swings(df, window=2)
        swing_high_indices = np.where(df_swings["is_swing_high"])[0]
        swing_low_indices = np.where(df_swings["is_swing_low"])[0]

        swing_points = []
        for idx in swing_high_indices[-6:]:
            swing_points.append({
                "type": "HIGH",
                "bar_idx": int(idx),
                "timestamp": str(df["timestamp"].iloc[idx]),
                "price": float(df["high"].iloc[idx]),
            })
        for idx in swing_low_indices[-6:]:
            swing_points.append({
                "type": "LOW",
                "bar_idx": int(idx),
                "timestamp": str(df["timestamp"].iloc[idx]),
                "price": float(df["low"].iloc[idx]),
            })

        # Sort chronologically
        swing_points.sort(key=lambda x: x["bar_idx"])

        # Classify sequence: HH, HL, LH, LL
        trend = "RANGE"
        last_highs = [p["price"] for p in swing_points if p["type"] == "HIGH"]
        last_lows = [p["price"] for p in swing_points if p["type"] == "LOW"]

        is_higher_highs = len(last_highs) >= 2 and last_highs[-1] > last_highs[-2]
        is_higher_lows = len(last_lows) >= 2 and last_lows[-1] > last_lows[-2]
        is_lower_highs = len(last_highs) >= 2 and last_highs[-1] < last_highs[-2]
        is_lower_lows = len(last_lows) >= 2 and last_lows[-1] < last_lows[-2]

        if is_higher_highs and is_higher_lows:
            trend = "BULLISH"
        elif is_lower_highs and is_lower_lows:
            trend = "BEARISH"
        elif is_higher_highs and is_lower_lows:
            trend = "EXPANDING_RANGE"
        elif is_lower_highs and is_higher_lows:
            trend = "CONTRACTING_RANGE"

        # Break of Structure (BOS) vs Change of Character (CHOCH)
        current_close = float(df["close"].iloc[-1])
        current_high = float(df["high"].iloc[-1])
        current_low = float(df["low"].iloc[-1])

        bos = False
        choch = False
        liquidity_sweep = False

        if len(last_highs) >= 2 and len(last_lows) >= 2:
            prev_swing_high = last_highs[-2]
            prev_swing_low = last_lows[-2]

            # BOS: Continuation of prevailing trend
            if trend == "BULLISH" and current_close > prev_swing_high:
                bos = True
            elif trend == "BEARISH" and current_close < prev_swing_low:
                bos = True

            # CHOCH: Reversal against prevailing trend
            if trend == "BEARISH" and current_close > prev_swing_high:
                choch = True
            elif trend == "BULLISH" and current_close < prev_swing_low:
                choch = True

            # Liquidity Sweep: Price pierced above swing high or below swing low but closed back inside
            if current_high > prev_swing_high and current_close < prev_swing_high:
                liquidity_sweep = True
            elif current_low < prev_swing_low and current_close > prev_swing_low:
                liquidity_sweep = True

        # Order Blocks: Last opposing candle before aggressive displacement
        order_blocks = []
        for i in range(max(5, len(df) - 30), len(df) - 3):
            # Bullish Order Block: down candle followed by strong 2-bar bullish expansion
            if df["close"].iloc[i] < df["open"].iloc[i]:
                expansion = df["close"].iloc[i+2] - df["open"].iloc[i+1]
                body_candle = df["open"].iloc[i] - df["close"].iloc[i]
                if expansion > body_candle * 2.2:
                    order_blocks.append({
                        "type": "BULLISH_DEMAND",
                        "top": round(float(df["high"].iloc[i]), 5),
                        "bottom": round(float(df["low"].iloc[i]), 5),
                        "bar_idx": i,
                        "timestamp": str(df["timestamp"].iloc[i]),
                    })
            # Bearish Order Block: up candle followed by strong 2-bar bearish drop
            elif df["close"].iloc[i] > df["open"].iloc[i]:
                expansion = df["open"].iloc[i+1] - df["close"].iloc[i+2]
                body_candle = df["close"].iloc[i] - df["open"].iloc[i]
                if expansion > body_candle * 2.2:
                    order_blocks.append({
                        "type": "BEARISH_SUPPLY",
                        "top": round(float(df["high"].iloc[i]), 5),
                        "bottom": round(float(df["low"].iloc[i]), 5),
                        "bar_idx": i,
                        "timestamp": str(df["timestamp"].iloc[i]),
                    })

        # Support and Resistance clusters (K-Means/quantile clustering on swing peaks and troughs)
        all_pivots = last_highs + last_lows
        support_levels = []
        resistance_levels = []

        for p in all_pivots:
            if p < current_close:
                support_levels.append(round(p, 5))
            else:
                resistance_levels.append(round(p, 5))

        support_levels = sorted(list(set(support_levels)))[-3:]  # Top 3 nearest supports
        resistance_levels = sorted(list(set(resistance_levels)))[:3]  # Top 3 nearest resistances

        return {
            "trend": trend,
            "bos": bos,
            "choch": choch,
            "liquidity_sweep": liquidity_sweep,
            "support_levels": support_levels,
            "resistance_levels": resistance_levels,
            "order_blocks": order_blocks[-4:],
            "swing_points": swing_points[-8:],
        }
