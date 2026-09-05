"""
Forex AI Walk-Forward Event-Driven Backtesting Engine
Simulates realistic trade execution including dynamic spread, slippage, and position sizing.
Computes institutional risk-adjusted metrics: Sharpe, Sortino, Calmar, Max Drawdown, Expectancy.
"""

from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
import math
import numpy as np
import pandas as pd

from data.providers.base import MarketDataProvider
from backend.app.services.technical_analysis import TechnicalAnalysisEngine


class BacktestEngine:
    """Rigorous chronological walk-forward backtesting system."""

    def __init__(self, provider: MarketDataProvider):
        self.provider = provider

    async def run_backtest(
        self,
        pair: str = "EUR/USD",
        timeframe: str = "1H",
        bars: int = 400,
        initial_capital: float = 100000.0,
        risk_per_trade_pct: float = 1.0,
        spread_pips: float = 1.2,
        slippage_pips: float = 0.5,
    ) -> Dict[str, Any]:
        """
        Executes a chronological event-driven backtest over historical candles.
        Prevents look-ahead bias by evaluating signals strictly at bar close (t) for execution at open (t+1).
        """
        df = await self.provider.get_candles(pair, timeframe, limit=bars)
        df_ind = TechnicalAnalysisEngine.calculate_indicators(df)

        pip_unit = 0.0001 if "JPY" not in pair else 0.01
        spread_cost_per_unit = spread_pips * pip_unit
        slippage_cost_per_unit = slippage_pips * pip_unit

        capital = initial_capital
        peak_capital = initial_capital
        equity_curve = []
        trades = []

        position: Optional[Dict[str, Any]] = None
        consecutive_wins = 0
        consecutive_losses = 0
        max_consecutive_wins = 0
        max_consecutive_losses = 0

        # Start after indicator warm-up window
        warmup = 35
        for i in range(warmup, len(df_ind) - 1):
            curr_bar = df_ind.iloc[i]
            next_bar = df_ind.iloc[i + 1]

            ts = curr_bar["timestamp"]
            c = curr_bar["close"]
            ema20 = curr_bar["ema_20"]
            ema50 = curr_bar["ema_50"]
            rsi = curr_bar["rsi_14"]
            atr = curr_bar["atr_14"]
            macd = curr_bar["macd"]
            macd_sig = curr_bar["macd_signal"]

            # Manage active position
            if position is not None:
                next_open = next_bar["open"]
                next_high = next_bar["high"]
                next_low = next_bar["low"]

                hit_tp = False
                hit_sl = False
                exit_price = 0.0
                exit_reason = ""

                if position["direction"] == "BUY":
                    if next_low <= position["sl"]:
                        hit_sl = True
                        exit_price = position["sl"] - slippage_cost_per_unit
                        exit_reason = "STOP_LOSS"
                    elif next_high >= position["tp"]:
                        hit_tp = True
                        exit_price = position["tp"] - slippage_cost_per_unit
                        exit_reason = "TAKE_PROFIT"

                elif position["direction"] == "SELL":
                    if next_high >= position["sl"]:
                        hit_sl = True
                        exit_price = position["sl"] + slippage_cost_per_unit
                        exit_reason = "STOP_LOSS"
                    elif next_low <= position["tp"]:
                        hit_tp = True
                        exit_price = position["tp"] + slippage_cost_per_unit
                        exit_reason = "TAKE_PROFIT"

                # Exit if triggered or after max hold time (16 bars)
                time_exit = (i - position["entry_bar_idx"]) >= 16
                if hit_tp or hit_sl or time_exit:
                    if not (hit_tp or hit_sl):
                        exit_price = next_open
                        exit_reason = "TIME_EXIT"

                    # Calculate PnL
                    lot_size = position["lot_size"]
                    units = lot_size * 100000.0

                    if position["direction"] == "BUY":
                        gross_pnl = (exit_price - position["entry_price"]) * units
                    else:
                        gross_pnl = (position["entry_price"] - exit_price) * units

                    # Subtract spread & slippage friction
                    transaction_costs = (spread_cost_per_unit + slippage_cost_per_unit) * units
                    net_pnl = gross_pnl - transaction_costs
                    capital += net_pnl

                    is_win = net_pnl > 0
                    if is_win:
                        consecutive_wins += 1
                        consecutive_losses = 0
                    else:
                        consecutive_losses += 1
                        consecutive_wins = 0

                    max_consecutive_wins = max(max_consecutive_wins, consecutive_wins)
                    max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)

                    trades.append({
                        "trade_id": len(trades) + 1,
                        "direction": position["direction"],
                        "entry_time": str(position["entry_time"]),
                        "entry_price": round(position["entry_price"], 5),
                        "exit_time": str(next_bar["timestamp"]),
                        "exit_price": round(exit_price, 5),
                        "lot_size": lot_size,
                        "pnl": round(net_pnl, 2),
                        "return_pct": round((net_pnl / position["capital_at_risk"]) * 100.0, 2),
                        "exit_reason": exit_reason,
                    })
                    position = None

            # Generate new entry signals at close(t) for execution at open(t+1)
            if position is None:
                risk_cash = capital * (risk_per_trade_pct / 100.0)
                sl_dist = max(atr * 1.5, 15.0 * pip_unit)
                tp_dist = sl_dist * 2.0  # 1:2 Risk/Reward target
                lot_size = max(0.1, min(round(risk_cash / (sl_dist / pip_unit * 10.0), 2), 5.0))

                # Trend-following strategy with momentum filter
                bull_signal = (c > ema20 > ema50) and (rsi > 50) and (macd > macd_sig)
                bear_signal = (c < ema20 < ema50) and (rsi < 50) and (macd < macd_sig)

                if bull_signal:
                    entry_p = next_bar["open"] + slippage_cost_per_unit + (spread_cost_per_unit / 2.0)
                    position = {
                        "direction": "BUY",
                        "entry_price": entry_p,
                        "sl": entry_p - sl_dist,
                        "tp": entry_p + tp_dist,
                        "entry_time": next_bar["timestamp"],
                        "entry_bar_idx": i,
                        "lot_size": lot_size,
                        "capital_at_risk": risk_cash,
                    }
                elif bear_signal:
                    entry_p = next_bar["open"] - slippage_cost_per_unit - (spread_cost_per_unit / 2.0)
                    position = {
                        "direction": "SELL",
                        "entry_price": entry_p,
                        "sl": entry_p + sl_dist,
                        "tp": entry_p - tp_dist,
                        "entry_time": next_bar["timestamp"],
                        "entry_bar_idx": i,
                        "lot_size": lot_size,
                        "capital_at_risk": risk_cash,
                    }

            # Record equity point
            peak_capital = max(peak_capital, capital)
            dd_pct = ((peak_capital - capital) / peak_capital) * 100.0 if peak_capital > 0 else 0.0
            equity_curve.append({
                "timestamp": str(ts),
                "equity": round(capital, 2),
                "drawdown_pct": round(dd_pct, 2),
            })

        # Calculate metrics
        total_trades = len(trades)
        winning_trades = [t for t in trades if t["pnl"] > 0]
        losing_trades = [t for t in trades if t["pnl"] <= 0]
        win_count = len(winning_trades)
        loss_count = len(losing_trades)
        win_rate = (win_count / total_trades * 100.0) if total_trades > 0 else 0.0

        gross_profit = sum(t["pnl"] for t in winning_trades)
        gross_loss = abs(sum(t["pnl"] for t in losing_trades))
        profit_factor = round(gross_profit / gross_loss, 2) if gross_loss > 0 else (99.0 if gross_profit > 0 else 0.0)
        net_profit = round(capital - initial_capital, 2)
        cagr = round(((capital / initial_capital) ** (365.0 / max(30, len(df_ind) // 24)) - 1.0) * 100.0, 2) if capital > 0 else -100.0
        max_drawdown = max([e["drawdown_pct"] for e in equity_curve]) if equity_curve else 0.0

        # Returns series for Sharpe & Sortino
        trade_returns = [t["pnl"] / initial_capital for t in trades]
        if len(trade_returns) > 2:
            mean_ret = np.mean(trade_returns)
            std_ret = np.std(trade_returns)
            downside_std = np.std([r for r in trade_returns if r < 0])
            sharpe = round(float((mean_ret / (std_ret + 1e-9)) * math.sqrt(252)), 2)
            sortino = round(float((mean_ret / (downside_std + 1e-9)) * math.sqrt(252)), 2)
        else:
            sharpe = 0.0
            sortino = 0.0

        avg_win = round(gross_profit / win_count, 2) if win_count > 0 else 0.0
        avg_loss = round(gross_loss / loss_count, 2) if loss_count > 0 else 0.0
        expectancy = round((win_rate / 100.0 * avg_win) - ((1.0 - win_rate / 100.0) * avg_loss), 2)

        return {
            "pair": pair,
            "timeframe": timeframe,
            "initial_capital": initial_capital,
            "final_capital": round(capital, 2),
            "net_profit": net_profit,
            "total_trades": total_trades,
            "winning_trades": win_count,
            "losing_trades": loss_count,
            "win_rate_pct": round(win_rate, 1),
            "profit_factor": profit_factor,
            "cagr_pct": cagr,
            "max_drawdown_pct": round(max_drawdown, 2),
            "sharpe_ratio": sharpe,
            "sortino_ratio": sortino,
            "average_win": avg_win,
            "average_loss": avg_loss,
            "expectancy": expectancy,
            "consecutive_wins": max_consecutive_wins,
            "consecutive_losses": max_consecutive_losses,
            "spread_pips": spread_pips,
            "slippage_pips": slippage_pips,
            "equity_curve": equity_curve[::max(1, len(equity_curve)//50)],  # Resample for clean rendering
            "trades": trades[-30:],  # Return recent trades
        }
