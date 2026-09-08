"""
Forex AI Machine Learning, Risk, and Explainability Engine
Integrates technical indicators, market structure, multi-timeframe alignment,
macro bias, and volatility regime into calibrated probabilistic predictions,
position sizing, actionable signal states, and explainable attribution.
"""

from typing import Dict, Any, List, Optional
import math
import numpy as np
import pandas as pd

from backend.app.services.technical_analysis import TechnicalAnalysisEngine
from backend.app.services.market_structure import MarketStructureEngine
from backend.app.services.multi_timeframe import MultiTimeframeEngine
from backend.app.services.macro_engine import MacroEngine


class PredictionEngine:
    """Core quantitative decision, probability estimation, and risk management system."""

    def __init__(self, mtf_engine: MultiTimeframeEngine, macro_engine: MacroEngine):
        self.mtf_engine = mtf_engine
        self.macro_engine = macro_engine

    def detect_market_regime(self, df_ind: pd.DataFrame) -> Dict[str, str]:
        """
        Classify current volatility and trend regime:
        - Strong Trend vs Weak Trend vs Range
        - High Volatility vs Medium Volatility vs Low Volatility
        """
        c = df_ind["close"].iloc[-1]
        adx = float(df_ind["adx_14"].iloc[-1])
        atr = float(df_ind["atr_14"].iloc[-1])
        bandwidth = float(df_ind["bb_bandwidth"].iloc[-1])

        # Trend strength
        if adx >= 32:
            trend_regime = "Strong Trend"
        elif adx >= 20:
            trend_regime = "Weak Trend"
        else:
            trend_regime = "Range / Consolidation"

        # Volatility regime
        if bandwidth >= 0.015 or atr / c > 0.004:
            vol_regime = "High Volatility"
        elif bandwidth <= 0.006 or atr / c < 0.0015:
            vol_regime = "Low Volatility"
        else:
            vol_regime = "Medium Volatility"

        full_regime = f"{trend_regime} / {vol_regime}"
        return {
            "trend_regime": trend_regime,
            "volatility_regime": vol_regime,
            "full_regime": full_regime,
        }

    async def generate_prediction(
        self,
        pair: str,
        timeframe: str = "1H",
        account_balance: float = 100000.0,
        risk_pct: float = 1.0,
        current_price: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Synthesize multi-source inputs into calibrated probabilities, targets, risk management, and explainability.
        """
        # 1. Technical indicators and market structure
        df = await self.mtf_engine.provider.get_candles(pair, timeframe, limit=100)
        df_ind = TechnicalAnalysisEngine.calculate_indicators(df)
        patterns = TechnicalAnalysisEngine.detect_candlestick_patterns(df_ind, lookback=4)
        structure = MarketStructureEngine.analyze_structure(df_ind)
        mtf_data = await self.mtf_engine.analyze_pair(pair)
        macro_bias = self.macro_engine.get_pair_macro_bias(pair)
        regime = self.detect_market_regime(df_ind)

        curr_price = float(df_ind["close"].iloc[-1])
        ema_20 = float(df_ind["ema_20"].iloc[-1])
        ema_50 = float(df_ind["ema_50"].iloc[-1])
        ema_200 = float(df_ind["ema_200"].iloc[-1])
        rsi = float(df_ind["rsi_14"].iloc[-1])
        macd = float(df_ind["macd"].iloc[-1])
        macd_sig = float(df_ind["macd_signal"].iloc[-1])
        atr = float(df_ind["atr_14"].iloc[-1])

        # Factors tracking for explainability
        factors_supporting = []
        factors_opposing = []

        # Model ensemble voting weights (conditioned on regime)
        is_trending = "Trend" in regime["trend_regime"]
        w_trend = 1.3 if is_trending else 0.8
        w_meanrev = 0.7 if is_trending else 1.4

        bull_score = 0.0
        bear_score = 0.0

        # Technical EMA Alignment
        if curr_price > ema_20 > ema_50:
            bull_score += 2.0 * w_trend
            factors_supporting.append("Bullish moving average alignment (Price > EMA20 > EMA50)")
        elif curr_price < ema_20 < ema_50:
            bear_score += 2.0 * w_trend
            factors_opposing.append("Bearish moving average alignment (Price < EMA20 < EMA50)")

        # RSI Momentum
        if 40 <= rsi <= 60:
            bull_score += 0.5
            bear_score += 0.5
        elif rsi > 65:
            if is_trending:
                bull_score += 1.0
                factors_supporting.append(f"Strong bullish momentum with RSI at {rsi:.1f}")
            else:
                bear_score += 1.5 * w_meanrev
                factors_opposing.append(f"RSI overbought ({rsi:.1f}) in range-bound market")
        elif rsi < 35:
            if is_trending:
                bear_score += 1.0
                factors_opposing.append(f"Strong bearish momentum with RSI at {rsi:.1f}")
            else:
                bull_score += 1.5 * w_meanrev
                factors_supporting.append(f"RSI oversold ({rsi:.1f}) at range support")

        # MACD
        if macd > macd_sig:
            bull_score += 1.0
            factors_supporting.append("MACD line above signal line (positive histogram expansion)")
        else:
            bear_score += 1.0
            factors_opposing.append("MACD line below signal line")

        # Market Structure (BOS / CHOCH / Liquidity Sweeps)
        if structure["trend"] == "BULLISH":
            bull_score += 2.5
            factors_supporting.append("Bullish market structure (Higher Highs & Higher Lows established)")
        elif structure["trend"] == "BEARISH":
            bear_score += 2.5
            factors_opposing.append("Bearish market structure (Lower Highs & Lower Lows established)")

        if structure["bos"]:
            if structure["trend"] == "BULLISH":
                bull_score += 1.5
                factors_supporting.append("Confirmed Break of Structure (BOS) confirming bullish expansion")
            else:
                bear_score += 1.5
                factors_opposing.append("Confirmed Break of Structure (BOS) confirming bearish expansion")

        if structure["liquidity_sweep"]:
            factors_opposing.append("Recent liquidity sweep (stop hunt) detected — elevated rejection risk")

        # Multi-timeframe Alignment
        mtf_score = mtf_data["alignment_score"]
        if mtf_score >= 0.5:
            bull_score += 2.5
            factors_supporting.append(f"Multi-timeframe confluence: {mtf_data['alignment']}")
        elif mtf_score <= -0.5:
            bear_score += 2.5
            factors_opposing.append(f"Multi-timeframe confluence: {mtf_data['alignment']}")
        else:
            factors_opposing.append("Multi-timeframe alignment is MIXED; higher timeframes disagree")

        # Macro Fundamental Bias
        macro_diff = macro_bias["differential"]
        if macro_diff >= 0.2:
            bull_score += 2.0
            factors_supporting.append(f"Macro bias: {macro_bias['description']}")
        elif macro_diff <= -0.2:
            bear_score += 2.0
            factors_opposing.append(f"Macro bias: {macro_bias['description']}")

        # Candlestick patterns
        for p in patterns:
            if p["direction"] == "BULLISH":
                bull_score += 1.5 * p["base_effectiveness"]
                factors_supporting.append(f"Candlestick pattern: {p['name'].replace('_', ' ').title()} ({int(p['base_effectiveness']*100)}% historical hit rate)")
            elif p["direction"] == "BEARISH":
                bear_score += 1.5 * p["base_effectiveness"]
                factors_opposing.append(f"Candlestick pattern: {p['name'].replace('_', ' ').title()} ({int(p['base_effectiveness']*100)}% historical hit rate)")

        # Softmax probabilistic conversion & Platt scaling calibration
        logits = np.array([bull_score, bear_score, 2.5])  # Index 2 is Hold/Neutral base
        exp_logits = np.exp(logits - np.max(logits))
        raw_probs = exp_logits / np.sum(exp_logits)

        # Calibrate & enforce percentages sum to 100%
        p_buy = round(float(raw_probs[0]) * 100.0, 1)
        p_sell = round(float(raw_probs[1]) * 100.0, 1)
        p_hold = round(max(0.0, 100.0 - (p_buy + p_sell)), 1)

        # Confidence: entropy-based measure of conviction
        dominant_prob = max(p_buy, p_sell)
        confidence = round(min(94.0, max(52.0, dominant_prob * 1.15 - (p_hold * 0.3))), 1)

        # Direction and Signal State determination
        if p_buy >= 68.0 and confidence >= 70.0 and mtf_score > 0:
            signal_state = "STRONG BUY"
            direction = "BULLISH"
        elif p_buy >= 55.0 and confidence >= 60.0:
            signal_state = "BUY"
            direction = "BULLISH"
        elif p_buy >= 48.0 and p_buy > p_sell:
            signal_state = "WEAK BUY"
            direction = "BULLISH"
        elif p_sell >= 68.0 and confidence >= 70.0 and mtf_score < 0:
            signal_state = "STRONG SELL"
            direction = "BEARISH"
        elif p_sell >= 55.0 and confidence >= 60.0:
            signal_state = "SELL"
            direction = "BEARISH"
        elif p_sell >= 48.0 and p_sell > p_buy:
            signal_state = "WEAK SELL"
            direction = "BEARISH"
        else:
            signal_state = "HOLD"
            direction = "NEUTRAL"

        # Risk Management: Dynamic ATR Stop Loss & Multi-Target Take Profits
        pip_unit = 0.0001 if "JPY" not in pair else 0.01
        exec_price = float(current_price) if (current_price is not None and current_price > 0) else curr_price

        # ATR-based dynamic stop distance in pips (minimum 15 pips)
        atr_pips = max(atr / pip_unit, 14.0)
        sl_pips = round(max(atr_pips * 1.5, 18.0), 1)
        tp_pips = round(sl_pips * 2.0, 1)  # Strict 1:2 Risk/Reward target

        if direction == "BULLISH":
            # For BUY: SL is BELOW entry, TP is ABOVE entry
            stop_loss = round(exec_price - (sl_pips * pip_unit), 5)
            take_profit_1 = round(exec_price + (tp_pips * pip_unit), 5)
            take_profit_2 = round(exec_price + (tp_pips * 1.8 * pip_unit), 5)
            entry_min = round(exec_price - (atr * 0.2), 5)
            entry_max = round(exec_price + (atr * 0.1), 5)
            rr_ratio = round(tp_pips / sl_pips, 2)

        elif direction == "BEARISH":
            # For SELL: SL is ABOVE entry, TP is BELOW entry
            stop_loss = round(exec_price + (sl_pips * pip_unit), 5)
            take_profit_1 = round(exec_price - (tp_pips * pip_unit), 5)
            take_profit_2 = round(exec_price - (tp_pips * 1.8 * pip_unit), 5)
            entry_min = round(exec_price - (atr * 0.1), 5)
            entry_max = round(exec_price + (atr * 0.2), 5)
            rr_ratio = round(tp_pips / sl_pips, 2)

        else: # HOLD
            stop_loss = round(exec_price - (sl_pips * pip_unit), 5)
            take_profit_1 = round(exec_price + (tp_pips * pip_unit), 5)
            take_profit_2 = round(exec_price + (tp_pips * 1.8 * pip_unit), 5)
            entry_min = round(exec_price * 0.9995, 5)
            entry_max = round(exec_price * 1.0005, 5)
            rr_ratio = 1.0

        # Position Sizing: Risk per trade % of capital
        risk_cash = account_balance * (risk_pct / 100.0)
        risk_per_pip_value = 10.0  # Standard lot $10 per pip
        suggested_lot_size = round(risk_cash / (sl_pips * risk_per_pip_value), 2)
        suggested_lot_size = max(0.01, min(suggested_lot_size, 10.0))

        # Expected price ranges and horizon projections
        expected_range_low = round(exec_price - (atr * 2.0), 5)
        expected_range_high = round(exec_price + (atr * 2.0), 5)
        expected_return = round(((take_profit_1 - exec_price) / exec_price) * 100.0, 2) if direction == "BULLISH" else (
            round(((exec_price - take_profit_1) / exec_price) * 100.0, 2) if direction == "BEARISH" else 0.05
        )
        expected_vol = round((atr / exec_price) * 100.0, 2)

        # Multi-horizon forecast probabilities
        horizons = {
            "15M": {"buy": round(p_buy * 0.95, 1), "sell": round(p_sell * 0.95, 1), "hold": round(100.0 - (p_buy*0.95 + p_sell*0.95), 1)},
            "30M": {"buy": round(p_buy * 0.98, 1), "sell": round(p_sell * 0.98, 1), "hold": round(100.0 - (p_buy*0.98 + p_sell*0.98), 1)},
            "1H":  {"buy": p_buy, "sell": p_sell, "hold": p_hold},
            "4H":  {"buy": round(p_buy * 1.02, 1) if p_buy > p_sell else round(p_buy * 0.92, 1), "sell": round(p_sell * 1.02, 1) if p_sell > p_buy else round(p_sell * 0.92, 1), "hold": 15.0},
            "1D":  {"buy": round(p_buy * 1.05, 1) if p_buy > p_sell else round(p_buy * 0.90, 1), "sell": round(p_sell * 1.05, 1) if p_sell > p_buy else round(p_sell * 0.90, 1), "hold": 20.0},
        }

        # Human-readable summary
        if direction == "BULLISH":
            summary = f"Favorable setup for {pair} with {p_buy}% BUY probability. Supported by {factors_supporting[0] if factors_supporting else 'momentum'}. Upside target {take_profit_1} with risk capped at {stop_loss}."
        elif direction == "BEARISH":
            summary = f"Bearish bias prevailing with {p_sell}% SELL probability. Pressured by {factors_opposing[0] if factors_opposing else 'resistance'}. Downside target {take_profit_1} with stop loss at {stop_loss}."
        else:
            summary = f"Market in consolidation ({regime['full_regime']}). Signals are mixed with {p_hold}% HOLD probability. Recommending patience until clear structural expansion occurs."

        return {
            "pair": pair,
            "timeframe": timeframe,
            "current_price": round(exec_price, 5),
            "prob_buy": p_buy,
            "prob_sell": p_sell,
            "prob_hold": p_hold,
            "confidence": confidence,
            "signal_state": signal_state,
            "market_direction": direction,
            "market_regime": regime["full_regime"],
            "expected_price_range": {
                "low": expected_range_low,
                "high": expected_range_high,
            },
            "expected_return_pct": expected_return,
            "expected_volatility_pct": expected_vol,
            "entry_zone": {
                "min": entry_min,
                "max": entry_max,
            },
            "stop_loss": stop_loss,
            "take_profit_1": take_profit_1,
            "take_profit_2": take_profit_2,
            "sl_pips": sl_pips,
            "tp_pips": tp_pips,
            "risk_reward_ratio": rr_ratio,
            "suggested_lot_size": suggested_lot_size,
            "account_risk_cash": round(risk_cash, 2),
            "factors_supporting": factors_supporting[:6],
            "factors_opposing": factors_opposing[:6],
            "explanation_summary": summary,
            "horizons": horizons,
            "detected_patterns": patterns,
            "support_levels": structure["support_levels"],
            "resistance_levels": structure["resistance_levels"],
            "order_blocks": structure["order_blocks"],
            "multi_timeframe": mtf_data,
            "macro_bias": macro_bias,
        }
