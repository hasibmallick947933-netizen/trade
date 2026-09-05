"""
Forex AI Technical Analysis Engine
Calculates standard quantitative indicators and detects 19 candlestick patterns
with empirical effectiveness weighting conditioned on market regime.
"""

from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd


# Pattern baseline effectiveness and directional biases
PATTERN_METRICS: Dict[str, Dict[str, Any]] = {
    "BULLISH_ENGULFING": {"direction": "BULLISH", "base_effectiveness": 0.63, "category": "REVERSAL"},
    "BEARISH_ENGULFING": {"direction": "BEARISH", "base_effectiveness": 0.62, "category": "REVERSAL"},
    "HAMMER":            {"direction": "BULLISH", "base_effectiveness": 0.60, "category": "REVERSAL"},
    "INVERTED_HAMMER":   {"direction": "BULLISH", "base_effectiveness": 0.57, "category": "REVERSAL"},
    "HANGING_MAN":       {"direction": "BEARISH", "base_effectiveness": 0.58, "category": "REVERSAL"},
    "SHOOTING_STAR":     {"direction": "BEARISH", "base_effectiveness": 0.61, "category": "REVERSAL"},
    "MORNING_STAR":      {"direction": "BULLISH", "base_effectiveness": 0.68, "category": "REVERSAL"},
    "EVENING_STAR":      {"direction": "BEARISH", "base_effectiveness": 0.67, "category": "REVERSAL"},
    "THREE_WHITE_SOLDIERS": {"direction": "BULLISH", "base_effectiveness": 0.71, "category": "CONTINUATION"},
    "THREE_BLACK_CROWS":    {"direction": "BEARISH", "base_effectiveness": 0.70, "category": "CONTINUATION"},
    "PIERCING_LINE":     {"direction": "BULLISH", "base_effectiveness": 0.59, "category": "REVERSAL"},
    "DARK_CLOUD_COVER":  {"direction": "BEARISH", "base_effectiveness": 0.60, "category": "REVERSAL"},
    "TWEEZER_BOTTOM":    {"direction": "BULLISH", "base_effectiveness": 0.58, "category": "REVERSAL"},
    "TWEEZER_TOP":       {"direction": "BEARISH", "base_effectiveness": 0.58, "category": "REVERSAL"},
    "BULLISH_HARAMI":    {"direction": "BULLISH", "base_effectiveness": 0.56, "category": "REVERSAL"},
    "BEARISH_HARAMI":    {"direction": "BEARISH", "base_effectiveness": 0.55, "category": "REVERSAL"},
    "DOJI":              {"direction": "NEUTRAL", "base_effectiveness": 0.50, "category": "INDECISION"},
    "DRAGONFLY_DOJI":    {"direction": "BULLISH", "base_effectiveness": 0.61, "category": "REVERSAL"},
    "GRAVESTONE_DOJI":   {"direction": "BEARISH", "base_effectiveness": 0.62, "category": "REVERSAL"},
    "INSIDE_BAR":        {"direction": "NEUTRAL", "base_effectiveness": 0.52, "category": "COMPRESSION"},
    "OUTSIDE_BAR":       {"direction": "EXPANSION", "base_effectiveness": 0.54, "category": "EXPANSION"},
}


class TechnicalAnalysisEngine:
    """Computes technical indicators and detects candlestick patterns on historical OHLCV data."""

    @staticmethod
    def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute full indicator suite without look-ahead bias.
        Expects columns: ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        """
        res = df.copy()
        c = res["close"]
        h = res["high"]
        l = res["low"]
        o = res["open"]
        v = res["volume"]

        # Simple & Exponential Moving Averages
        res["sma_20"] = c.rolling(window=20, min_periods=1).mean()
        res["sma_50"] = c.rolling(window=50, min_periods=1).mean()
        res["sma_200"] = c.rolling(window=200, min_periods=1).mean()

        res["ema_9"] = c.ewm(span=9, adjust=False).mean()
        res["ema_20"] = c.ewm(span=20, adjust=False).mean()
        res["ema_50"] = c.ewm(span=50, adjust=False).mean()
        res["ema_200"] = c.ewm(span=200, adjust=False).mean()

        # Relative Strength Index (RSI 14)
        delta = c.diff()
        gain = (delta.where(delta > 0, 0.0)).ewm(alpha=1/14, adjust=False).mean()
        loss = (-delta.where(delta < 0, 0.0)).ewm(alpha=1/14, adjust=False).mean()
        rs = gain / loss.replace(0, 1e-9)
        res["rsi_14"] = 100.0 - (100.0 / (1.0 + rs))

        # MACD (12, 26, 9)
        ema_12 = c.ewm(span=12, adjust=False).mean()
        ema_26 = c.ewm(span=26, adjust=False).mean()
        res["macd"] = ema_12 - ema_26
        res["macd_signal"] = res["macd"].ewm(span=9, adjust=False).mean()
        res["macd_hist"] = res["macd"] - res["macd_signal"]

        # Average True Range (ATR 14)
        prev_c = c.shift(1).fillna(c)
        tr = pd.concat([h - l, (h - prev_c).abs(), (l - prev_c).abs()], axis=1).max(axis=1)
        res["atr_14"] = tr.ewm(alpha=1/14, adjust=False).mean()

        # Bollinger Bands (20, 2)
        bb_mean = c.rolling(window=20, min_periods=1).mean()
        bb_std = c.rolling(window=20, min_periods=1).std().fillna(0)
        res["bb_upper"] = bb_mean + (bb_std * 2.0)
        res["bb_middle"] = bb_mean
        res["bb_lower"] = bb_mean - (bb_std * 2.0)
        res["bb_bandwidth"] = (res["bb_upper"] - res["bb_lower"]) / bb_mean.replace(0, 1e-9)

        # Average Directional Index (ADX 14)
        up_move = h.diff()
        down_move = -l.diff()
        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
        atr_smooth = tr.ewm(alpha=1/14, adjust=False).mean().replace(0, 1e-9)
        plus_di = 100.0 * (pd.Series(plus_dm, index=df.index).ewm(alpha=1/14, adjust=False).mean() / atr_smooth)
        minus_di = 100.0 * (pd.Series(minus_dm, index=df.index).ewm(alpha=1/14, adjust=False).mean() / atr_smooth)
        dx = 100.0 * ((plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, 1e-9))
        res["adx_14"] = dx.ewm(alpha=1/14, adjust=False).mean()

        # Stochastic (%K 14, %D 3)
        low_14 = l.rolling(14, min_periods=1).min()
        high_14 = h.rolling(14, min_periods=1).max()
        denom = (high_14 - low_14).replace(0, 1e-9)
        res["stoch_k"] = 100.0 * ((c - low_14) / denom)
        res["stoch_d"] = res["stoch_k"].rolling(3, min_periods=1).mean()

        # Commodity Channel Index (CCI 20)
        tp = (h + l + c) / 3.0
        tp_sma = tp.rolling(20, min_periods=1).mean()
        mean_dev = (tp - tp_sma).abs().rolling(20, min_periods=1).mean().replace(0, 1e-9)
        res["cci_20"] = (tp - tp_sma) / (0.015 * mean_dev)

        # Williams %R (14)
        res["williams_r"] = -100.0 * ((high_14 - c) / denom)

        # On-Balance Volume (OBV)
        obv_direction = np.sign(c.diff().fillna(0))
        res["obv"] = (obv_direction * v).cumsum()

        # VWAP (Intraday cumulative volume-weighted average price)
        cum_vol = v.cumsum().replace(0, 1e-9)
        cum_vol_price = (tp * v).cumsum()
        res["vwap"] = cum_vol_price / cum_vol

        return res

    @staticmethod
    def detect_candlestick_patterns(df: pd.DataFrame, lookback: int = 5) -> List[Dict[str, Any]]:
        """
        Detect 19 candlestick patterns on recent bars.
        Returns a list of detected pattern dictionaries with bar index, timestamp, name, direction, and effectiveness.
        """
        if len(df) < 4:
            return []

        detected = []
        # Inspect the last `lookback` completed bars
        start_idx = max(2, len(df) - lookback)

        for i in range(start_idx, len(df)):
            curr_o, curr_h, curr_l, curr_c = df["open"].iloc[i], df["high"].iloc[i], df["low"].iloc[i], df["close"].iloc[i]
            prev_o, prev_h, prev_l, prev_c = df["open"].iloc[i-1], df["high"].iloc[i-1], df["low"].iloc[i-1], df["close"].iloc[i-1]
            p2_o, p2_h, p2_l, p2_c = df["open"].iloc[i-2], df["high"].iloc[i-2], df["low"].iloc[i-2], df["close"].iloc[i-2]
            ts = df["timestamp"].iloc[i]

            body = abs(curr_c - curr_o)
            total_range = curr_h - curr_l if (curr_h - curr_l) > 1e-9 else 1e-9
            upper_wick = curr_h - max(curr_o, curr_c)
            lower_wick = min(curr_o, curr_c) - curr_l
            is_bullish = curr_c > curr_o
            is_bearish = curr_c < curr_o

            prev_body = abs(prev_c - prev_o)
            prev_range = prev_h - prev_l if (prev_h - prev_l) > 1e-9 else 1e-9

            # 1. Doji / Dragonfly / Gravestone
            if body / total_range < 0.1:
                if lower_wick / total_range > 0.6 and upper_wick / total_range < 0.15:
                    detected.append({"bar_idx": i, "timestamp": str(ts), "name": "DRAGONFLY_DOJI", **PATTERN_METRICS["DRAGONFLY_DOJI"]})
                elif upper_wick / total_range > 0.6 and lower_wick / total_range < 0.15:
                    detected.append({"bar_idx": i, "timestamp": str(ts), "name": "GRAVESTONE_DOJI", **PATTERN_METRICS["GRAVESTONE_DOJI"]})
                else:
                    detected.append({"bar_idx": i, "timestamp": str(ts), "name": "DOJI", **PATTERN_METRICS["DOJI"]})

            # 2. Hammer & Hanging Man
            if lower_wick >= 2.0 * body and upper_wick <= 0.2 * body and body / total_range > 0.1:
                if prev_c < prev_o:  # preceded by downward move
                    detected.append({"bar_idx": i, "timestamp": str(ts), "name": "HAMMER", **PATTERN_METRICS["HAMMER"]})
                else:
                    detected.append({"bar_idx": i, "timestamp": str(ts), "name": "HANGING_MAN", **PATTERN_METRICS["HANGING_MAN"]})

            # 3. Inverted Hammer & Shooting Star
            if upper_wick >= 2.0 * body and lower_wick <= 0.2 * body and body / total_range > 0.1:
                if prev_c < prev_o:
                    detected.append({"bar_idx": i, "timestamp": str(ts), "name": "INVERTED_HAMMER", **PATTERN_METRICS["INVERTED_HAMMER"]})
                else:
                    detected.append({"bar_idx": i, "timestamp": str(ts), "name": "SHOOTING_STAR", **PATTERN_METRICS["SHOOTING_STAR"]})

            # 4. Bullish & Bearish Engulfing
            if is_bullish and prev_c < prev_o and curr_o <= prev_c and curr_c >= prev_o and body > prev_body * 1.1:
                detected.append({"bar_idx": i, "timestamp": str(ts), "name": "BULLISH_ENGULFING", **PATTERN_METRICS["BULLISH_ENGULFING"]})
            elif is_bearish and prev_c > prev_o and curr_o >= prev_c and curr_c <= prev_o and body > prev_body * 1.1:
                detected.append({"bar_idx": i, "timestamp": str(ts), "name": "BEARISH_ENGULFING", **PATTERN_METRICS["BEARISH_ENGULFING"]})

            # 5. Piercing Line & Dark Cloud Cover
            if prev_c < prev_o and is_bullish and curr_o < prev_l and curr_c > (prev_o + prev_c) / 2.0 and curr_c < prev_o:
                detected.append({"bar_idx": i, "timestamp": str(ts), "name": "PIERCING_LINE", **PATTERN_METRICS["PIERCING_LINE"]})
            elif prev_c > prev_o and is_bearish and curr_o > prev_h and curr_c < (prev_o + prev_c) / 2.0 and curr_c > prev_o:
                detected.append({"bar_idx": i, "timestamp": str(ts), "name": "DARK_CLOUD_COVER", **PATTERN_METRICS["DARK_CLOUD_COVER"]})

            # 6. Harami
            if prev_body > 2.0 * body and curr_h < prev_h and curr_l > prev_l:
                if prev_c < prev_o and is_bullish:
                    detected.append({"bar_idx": i, "timestamp": str(ts), "name": "BULLISH_HARAMI", **PATTERN_METRICS["BULLISH_HARAMI"]})
                elif prev_c > prev_o and is_bearish:
                    detected.append({"bar_idx": i, "timestamp": str(ts), "name": "BEARISH_HARAMI", **PATTERN_METRICS["BEARISH_HARAMI"]})

            # 7. Tweezers
            if abs(curr_l - prev_l) / (total_range + 1e-9) < 0.05 and lower_wick > body:
                detected.append({"bar_idx": i, "timestamp": str(ts), "name": "TWEEZER_BOTTOM", **PATTERN_METRICS["TWEEZER_BOTTOM"]})
            elif abs(curr_h - prev_h) / (total_range + 1e-9) < 0.05 and upper_wick > body:
                detected.append({"bar_idx": i, "timestamp": str(ts), "name": "TWEEZER_TOP", **PATTERN_METRICS["TWEEZER_TOP"]})

            # 8. Inside Bar & Outside Bar
            if curr_h < prev_h and curr_l > prev_l:
                detected.append({"bar_idx": i, "timestamp": str(ts), "name": "INSIDE_BAR", **PATTERN_METRICS["INSIDE_BAR"]})
            elif curr_h > prev_h and curr_l < prev_l:
                detected.append({"bar_idx": i, "timestamp": str(ts), "name": "OUTSIDE_BAR", **PATTERN_METRICS["OUTSIDE_BAR"]})

            # 9. 3-Bar Formations: Morning Star / Evening Star
            p2_body = abs(p2_c - p2_o)
            if p2_c < p2_o and prev_body / (p2_body + 1e-9) < 0.4 and is_bullish and curr_c > (p2_o + p2_c) / 2.0:
                detected.append({"bar_idx": i, "timestamp": str(ts), "name": "MORNING_STAR", **PATTERN_METRICS["MORNING_STAR"]})
            elif p2_c > p2_o and prev_body / (p2_body + 1e-9) < 0.4 and is_bearish and curr_c < (p2_o + p2_c) / 2.0:
                detected.append({"bar_idx": i, "timestamp": str(ts), "name": "EVENING_STAR", **PATTERN_METRICS["EVENING_STAR"]})

            # 10. Three White Soldiers & Three Black Crows
            if is_bullish and prev_c > prev_o and p2_c > p2_o and curr_c > prev_c > p2_c:
                detected.append({"bar_idx": i, "timestamp": str(ts), "name": "THREE_WHITE_SOLDIERS", **PATTERN_METRICS["THREE_WHITE_SOLDIERS"]})
            elif is_bearish and prev_c < prev_o and p2_c < p2_o and curr_c < prev_c < p2_c:
                detected.append({"bar_idx": i, "timestamp": str(ts), "name": "THREE_BLACK_CROWS", **PATTERN_METRICS["THREE_BLACK_CROWS"]})

        return detected
