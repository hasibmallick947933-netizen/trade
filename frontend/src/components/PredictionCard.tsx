"use client";

import React from "react";
import { Prediction } from "@/lib/api";
import { ShieldAlert, TrendingUp, TrendingDown, Minus, Target, DollarSign, Activity } from "lucide-react";

interface PredictionCardProps {
  prediction: Prediction | null;
  loading: boolean;
}

export const PredictionCard: React.FC<PredictionCardProps> = ({ prediction, loading }) => {
  if (loading || !prediction) {
    return (
      <div className="bg-surface border border-border rounded-xl p-5 animate-pulse min-h-[360px] flex flex-col justify-between">
        <div className="h-6 bg-surface-raised rounded w-1/3 mb-4"></div>
        <div className="h-20 bg-surface-raised rounded mb-4"></div>
        <div className="space-y-2">
          <div className="h-4 bg-surface-raised rounded"></div>
          <div className="h-4 bg-surface-raised rounded w-5/6"></div>
          <div className="h-4 bg-surface-raised rounded w-4/6"></div>
        </div>
      </div>
    );
  }

  const {
    prob_buy,
    prob_sell,
    prob_hold,
    confidence,
    signal_state,
    market_direction,
    market_regime,
    current_price,
    entry_zone,
    stop_loss,
    take_profit_1,
    take_profit_2,
    risk_reward_ratio,
    suggested_lot_size,
    account_risk_cash,
    horizons,
  } = prediction;

  const isBull = market_direction === "BULLISH";
  const isBear = market_direction === "BEARISH";

  const getSignalBadgeColor = () => {
    if (signal_state.includes("STRONG BUY")) return "bg-emerald-500/20 text-emerald-400 border-emerald-500/40";
    if (signal_state.includes("BUY")) return "bg-emerald-500/15 text-emerald-300 border-emerald-500/30";
    if (signal_state.includes("STRONG SELL")) return "bg-rose-500/20 text-rose-400 border-rose-500/40";
    if (signal_state.includes("SELL")) return "bg-rose-500/15 text-rose-300 border-rose-500/30";
    return "bg-slate-700/30 text-slate-300 border-slate-600/40";
  };

  return (
    <div className="bg-surface border border-border rounded-xl p-5 flex flex-col justify-between shadow-xl">
      {/* Top Banner: Signal State & Regime */}
      <div>
        <div className="flex items-center justify-between gap-2 mb-3">
          <div className="flex items-center gap-2">
            <span
              className={`px-2.5 py-1 rounded-md text-xs font-mono font-bold tracking-wide border uppercase flex items-center gap-1.5 shadow-sm ${getSignalBadgeColor()}`}
            >
              {isBull && <TrendingUp className="w-3.5 h-3.5" />}
              {isBear && <TrendingDown className="w-3.5 h-3.5" />}
              {!isBull && !isBear && <Minus className="w-3.5 h-3.5" />}
              {signal_state}
            </span>
            <span className="text-xs text-slate-400 font-mono">
              @ {current_price.toFixed(5)}
            </span>
          </div>

          <div className="text-right">
            <div className="text-[11px] uppercase tracking-wider text-slate-400">Confidence</div>
            <div className="text-sm font-extrabold font-mono text-accent">
              {confidence}%
            </div>
          </div>
        </div>

        {/* Market Regime Badge */}
        <div className="mb-4 flex items-center justify-between px-3 py-2 rounded-lg bg-surface-raised/70 border border-border/80 text-xs">
          <span className="text-slate-400 flex items-center gap-1.5">
            <Activity className="w-3.5 h-3.5 text-accent" /> Market Regime:
          </span>
          <span className="font-semibold text-slate-200">{market_regime}</span>
        </div>

        {/* Probabilities Bar */}
        <div className="mb-4">
          <div className="flex justify-between text-xs font-mono mb-1.5">
            <span className="text-emerald-400 font-bold">BUY {prob_buy}%</span>
            <span className="text-slate-400 font-medium">HOLD {prob_hold}%</span>
            <span className="text-rose-400 font-bold">SELL {prob_sell}%</span>
          </div>

          {/* Segmented Progress bar */}
          <div className="h-2.5 w-full rounded-full bg-surface-raised overflow-hidden flex shadow-inner">
            <div
              style={{ width: `${prob_buy}%` }}
              className="bg-emerald-500 transition-all duration-500"
            />
            <div
              style={{ width: `${prob_hold}%` }}
              className="bg-slate-500 transition-all duration-500"
            />
            <div
              style={{ width: `${prob_sell}%` }}
              className="bg-rose-500 transition-all duration-500"
            />
          </div>
        </div>

        {/* Risk & Execution Targets Matrix */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-4">
          <div className="p-2.5 rounded-lg bg-surface-raised/50 border border-border text-center">
            <div className="text-[10px] text-slate-400 uppercase">Entry Zone</div>
            <div className="text-xs font-mono font-bold text-slate-200 mt-0.5">
              {entry_zone.min.toFixed(4)} - {entry_zone.max.toFixed(4)}
            </div>
          </div>

          <div className="p-2.5 rounded-lg bg-surface-raised/50 border border-rose-500/20 text-center">
            <div className="text-[10px] text-rose-400 uppercase flex items-center justify-center gap-1">
              <ShieldAlert className="w-3 h-3" /> Stop Loss
            </div>
            <div className="text-xs font-mono font-bold text-rose-300 mt-0.5">
              {stop_loss.toFixed(5)}
            </div>
          </div>

          <div className="p-2.5 rounded-lg bg-surface-raised/50 border border-emerald-500/20 text-center">
            <div className="text-[10px] text-emerald-400 uppercase flex items-center justify-center gap-1">
              <Target className="w-3 h-3" /> Take Profit 1
            </div>
            <div className="text-xs font-mono font-bold text-emerald-300 mt-0.5">
              {take_profit_1.toFixed(5)}
            </div>
          </div>

          <div className="p-2.5 rounded-lg bg-surface-raised/50 border border-emerald-500/20 text-center">
            <div className="text-[10px] text-emerald-400 uppercase flex items-center justify-center gap-1">
              <Target className="w-3 h-3" /> Take Profit 2
            </div>
            <div className="text-xs font-mono font-bold text-emerald-300 mt-0.5">
              {take_profit_2.toFixed(5)}
            </div>
          </div>
        </div>

        {/* Position Sizing and R:R */}
        <div className="flex items-center justify-between p-3 rounded-lg bg-surface-raised border border-border text-xs font-mono">
          <div>
            <span className="text-slate-400">Risk/Reward: </span>
            <span className="font-bold text-emerald-400">1 : {risk_reward_ratio}</span>
          </div>
          <div>
            <span className="text-slate-400">Rec. Sizing: </span>
            <span className="font-bold text-accent">{suggested_lot_size} Lots</span>
            <span className="text-[10px] text-slate-500 ml-1">(${account_risk_cash} risk)</span>
          </div>
        </div>
      </div>

      {/* Horizon Forecast Strip */}
      <div className="mt-4 pt-3 border-t border-border">
        <div className="text-[11px] text-slate-400 uppercase tracking-wider mb-2 font-mono">
          Multi-Horizon Probability Outlook
        </div>
        <div className="grid grid-cols-5 gap-1.5 text-center font-mono">
          {Object.entries(horizons).map(([hz, p]) => (
            <div key={hz} className="p-1.5 rounded bg-surface-raised/60 border border-border/50">
              <div className="text-[10px] text-slate-400 font-bold">{hz}</div>
              <div className="text-[11px] font-extrabold text-emerald-400">{p.buy}%</div>
              <div className="text-[10px] text-rose-400">{p.sell}%</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
