"use client";

import React, { useState } from "react";
import { runBacktest, BacktestResult } from "@/lib/api";
import { X, Play, TrendingUp, ShieldAlert, BarChart2, Activity } from "lucide-react";

interface BacktestModalProps {
  isOpen: boolean;
  onClose: () => void;
  defaultPair: string;
  defaultTimeframe: string;
}

export const BacktestModal: React.FC<BacktestModalProps> = ({
  isOpen,
  onClose,
  defaultPair,
  defaultTimeframe,
}) => {
  const [pair, setPair] = useState(defaultPair);
  const [timeframe, setTimeframe] = useState(defaultTimeframe);
  const [bars, setBars] = useState(350);
  const [initialCapital, setInitialCapital] = useState(100000);
  const [riskPct, setRiskPct] = useState(1.0);
  const [spreadPips, setSpreadPips] = useState(1.2);
  const [slippagePips, setSlippagePips] = useState(0.5);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<BacktestResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleRun = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await runBacktest({
        pair,
        timeframe,
        bars,
        initial_capital: initialCapital,
        risk_per_trade_pct: riskPct,
        spread_pips: spreadPips,
        slippage_pips: slippagePips,
      });
      setResult(res);
    } catch (err: any) {
      setError(err.message || "Backtest execution failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="bg-surface border border-border rounded-2xl w-full max-w-5xl max-h-[92vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-border bg-surface-raised/80">
          <div>
            <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
              <Activity className="w-4 h-4 text-accent" />
              Walk-Forward Backtesting Studio
            </h2>
            <p className="text-xs text-slate-400">
              Point-in-time validation with real spread, slippage & fee modeling
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-surface-raised transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Parameter Controls */}
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3 bg-surface-raised/40 p-4 rounded-xl border border-border">
            <div>
              <label className="text-[11px] text-slate-400 font-mono">Pair</label>
              <input
                type="text"
                value={pair}
                onChange={(e) => setPair(e.target.value)}
                className="w-full mt-1 bg-surface border border-border rounded px-2.5 py-1 text-xs text-slate-100 font-mono focus:border-accent outline-none"
              />
            </div>
            <div>
              <label className="text-[11px] text-slate-400 font-mono">Timeframe</label>
              <input
                type="text"
                value={timeframe}
                onChange={(e) => setTimeframe(e.target.value)}
                className="w-full mt-1 bg-surface border border-border rounded px-2.5 py-1 text-xs text-slate-100 font-mono focus:border-accent outline-none"
              />
            </div>
            <div>
              <label className="text-[11px] text-slate-400 font-mono">Historical Bars</label>
              <input
                type="number"
                value={bars}
                onChange={(e) => setBars(Number(e.target.value))}
                className="w-full mt-1 bg-surface border border-border rounded px-2.5 py-1 text-xs text-slate-100 font-mono focus:border-accent outline-none"
              />
            </div>
            <div>
              <label className="text-[11px] text-slate-400 font-mono">Initial Capital ($)</label>
              <input
                type="number"
                value={initialCapital}
                onChange={(e) => setInitialCapital(Number(e.target.value))}
                className="w-full mt-1 bg-surface border border-border rounded px-2.5 py-1 text-xs text-slate-100 font-mono focus:border-accent outline-none"
              />
            </div>
            <div>
              <label className="text-[11px] text-slate-400 font-mono">Risk / Trade (%)</label>
              <input
                type="number"
                step="0.1"
                value={riskPct}
                onChange={(e) => setRiskPct(Number(e.target.value))}
                className="w-full mt-1 bg-surface border border-border rounded px-2.5 py-1 text-xs text-slate-100 font-mono focus:border-accent outline-none"
              />
            </div>
            <div>
              <label className="text-[11px] text-slate-400 font-mono">Spread (pips)</label>
              <input
                type="number"
                step="0.1"
                value={spreadPips}
                onChange={(e) => setSpreadPips(Number(e.target.value))}
                className="w-full mt-1 bg-surface border border-border rounded px-2.5 py-1 text-xs text-slate-100 font-mono focus:border-accent outline-none"
              />
            </div>
            <div>
              <label className="text-[11px] text-slate-400 font-mono">Slippage (pips)</label>
              <input
                type="number"
                step="0.1"
                value={slippagePips}
                onChange={(e) => setSlippagePips(Number(e.target.value))}
                className="w-full mt-1 bg-surface border border-border rounded px-2.5 py-1 text-xs text-slate-100 font-mono focus:border-accent outline-none"
              />
            </div>
          </div>

          <div className="flex justify-end">
            <button
              onClick={handleRun}
              disabled={loading}
              className="flex items-center gap-2 px-5 py-2 rounded-xl bg-accent hover:bg-accent/90 text-white text-xs font-bold transition shadow-lg shadow-accent/20 disabled:opacity-50"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              {loading ? "Simulating Walk-Forward Engine..." : "Execute Backtest"}
            </button>
          </div>

          {error && (
            <div className="p-3 rounded-lg bg-rose-500/20 border border-rose-500/40 text-rose-300 text-xs">
              {error}
            </div>
          )}

          {/* Results Display */}
          {result && (
            <div className="space-y-6">
              {/* Core Metric Cards */}
              <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3">
                <div className="p-3 rounded-xl bg-surface-raised border border-border">
                  <div className="text-[10px] text-slate-400 uppercase font-mono">Net Profit</div>
                  <div
                    className={`text-base font-extrabold font-mono mt-1 ${
                      result.net_profit >= 0 ? "text-emerald-400" : "text-rose-400"
                    }`}
                  >
                    ${result.net_profit.toLocaleString()}
                  </div>
                  <div className="text-[10px] text-slate-500 font-mono">
                    CAGR: {result.cagr_pct}%
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-surface-raised border border-border">
                  <div className="text-[10px] text-slate-400 uppercase font-mono">Win Rate</div>
                  <div className="text-base font-extrabold font-mono mt-1 text-slate-100">
                    {result.win_rate_pct}%
                  </div>
                  <div className="text-[10px] text-slate-500 font-mono">
                    {result.winning_trades}W / {result.losing_trades}L ({result.total_trades} total)
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-surface-raised border border-border">
                  <div className="text-[10px] text-slate-400 uppercase font-mono">Profit Factor</div>
                  <div className="text-base font-extrabold font-mono mt-1 text-accent">
                    {result.profit_factor}
                  </div>
                  <div className="text-[10px] text-slate-500 font-mono">
                    Expectancy: ${result.expectancy}
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-surface-raised border border-border">
                  <div className="text-[10px] text-slate-400 uppercase font-mono">Max Drawdown</div>
                  <div className="text-base font-extrabold font-mono mt-1 text-rose-400">
                    -{result.max_drawdown_pct}%
                  </div>
                  <div className="text-[10px] text-slate-500 font-mono">
                    Max Loss Streak: {result.consecutive_losses}
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-surface-raised border border-border">
                  <div className="text-[10px] text-slate-400 uppercase font-mono">Sharpe Ratio</div>
                  <div className="text-base font-extrabold font-mono mt-1 text-sky-400">
                    {result.sharpe_ratio}
                  </div>
                  <div className="text-[10px] text-slate-500 font-mono">Annualized</div>
                </div>

                <div className="p-3 rounded-xl bg-surface-raised border border-border">
                  <div className="text-[10px] text-slate-400 uppercase font-mono">Sortino Ratio</div>
                  <div className="text-base font-extrabold font-mono mt-1 text-purple-400">
                    {result.sortino_ratio}
                  </div>
                  <div className="text-[10px] text-slate-500 font-mono">Downside risk-adjusted</div>
                </div>
              </div>

              {/* Equity Curve SVG Chart */}
              <div className="p-4 rounded-xl bg-surface-raised border border-border">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-xs font-bold text-slate-200 uppercase font-mono">
                    Equity Growth Curve ($)
                  </h4>
                  <span className="text-[10px] text-slate-400 font-mono">
                    Final Capital: ${result.final_capital.toLocaleString()}
                  </span>
                </div>

                <div className="h-44 w-full">
                  <svg className="w-full h-full" viewBox="0 0 500 120" preserveAspectRatio="none">
                    <defs>
                      <linearGradient id="equityGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#6366f1" stopOpacity="0.4" />
                        <stop offset="100%" stopColor="#6366f1" stopOpacity="0.0" />
                      </linearGradient>
                    </defs>

                    {/* Generate SVG Path */}
                    {(() => {
                      const pts = result.equity_curve;
                      if (pts.length < 2) return null;
                      const equities = pts.map((p) => p.equity);
                      const minEq = Math.min(...equities) * 0.99;
                      const maxEq = Math.max(...equities) * 1.01;
                      const range = maxEq - minEq || 1;

                      const coords = pts.map((p, i) => {
                        const x = (i / (pts.length - 1)) * 500;
                        const y = 115 - ((p.equity - minEq) / range) * 105;
                        return `${x},${y}`;
                      });

                      const pathD = `M ${coords.join(" L ")}`;
                      const areaD = `${pathD} L 500,120 L 0,120 Z`;

                      return (
                        <>
                          <path d={areaD} fill="url(#equityGrad)" />
                          <path d={pathD} fill="none" stroke="#6366f1" strokeWidth="2" />
                        </>
                      );
                    })()}
                  </svg>
                </div>
              </div>

              {/* Recent Trades Table */}
              <div className="rounded-xl border border-border overflow-hidden">
                <div className="px-4 py-2 bg-surface-raised/90 border-b border-border text-xs font-bold text-slate-200 font-mono">
                  Executed Trades Log (Recent {result.trades.length})
                </div>
                <div className="max-h-60 overflow-y-auto">
                  <table className="w-full text-left text-xs font-mono">
                    <thead className="bg-surface sticky top-0 border-b border-border text-[10px] text-slate-400 uppercase">
                      <tr>
                        <th className="py-2 px-3">#</th>
                        <th className="py-2 px-3">Direction</th>
                        <th className="py-2 px-3">Entry Time</th>
                        <th className="py-2 px-3">Entry</th>
                        <th className="py-2 px-3">Exit</th>
                        <th className="py-2 px-3">Lot</th>
                        <th className="py-2 px-3">Net PnL</th>
                        <th className="py-2 px-3">Reason</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border/40">
                      {result.trades.map((t) => (
                        <tr key={t.trade_id} className="hover:bg-surface-raised/30 transition">
                          <td className="py-1.5 px-3 text-slate-400">{t.trade_id}</td>
                          <td className="py-1.5 px-3">
                            <span
                              className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                                t.direction === "BUY"
                                  ? "bg-emerald-500/20 text-emerald-400"
                                  : "bg-rose-500/20 text-rose-400"
                              }`}
                            >
                              {t.direction}
                            </span>
                          </td>
                          <td className="py-1.5 px-3 text-slate-400 text-[11px]">{t.entry_time.slice(0, 16)}</td>
                          <td className="py-1.5 px-3 text-slate-200">{t.entry_price.toFixed(5)}</td>
                          <td className="py-1.5 px-3 text-slate-200">{t.exit_price.toFixed(5)}</td>
                          <td className="py-1.5 px-3 text-slate-300">{t.lot_size}</td>
                          <td
                            className={`py-1.5 px-3 font-bold ${
                              t.pnl >= 0 ? "text-emerald-400" : "text-rose-400"
                            }`}
                          >
                            ${t.pnl.toFixed(2)}
                          </td>
                          <td className="py-1.5 px-3 text-slate-400 text-[10px]">{t.exit_reason}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
