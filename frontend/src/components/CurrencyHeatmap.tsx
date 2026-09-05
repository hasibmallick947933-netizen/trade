"use client";

import React from "react";
import { CurrencyHeatmap } from "@/lib/api";
import { BarChart3, TrendingUp, TrendingDown, Sparkles } from "lucide-react";

interface CurrencyHeatmapProps {
  heatmap: CurrencyHeatmap | null;
  loading: boolean;
}

export const CurrencyHeatmapWidget: React.FC<CurrencyHeatmapProps> = ({ heatmap, loading }) => {
  if (loading || !heatmap) {
    return (
      <div className="bg-surface border border-border rounded-xl p-4 animate-pulse min-h-[220px]">
        <div className="h-5 bg-surface-raised rounded w-1/3 mb-3"></div>
        <div className="space-y-2">
          <div className="h-4 bg-surface-raised rounded"></div>
          <div className="h-4 bg-surface-raised rounded"></div>
        </div>
      </div>
    );
  }

  const { rankings, strongest, weakest, best_long_opportunity } = heatmap;

  return (
    <div className="bg-surface border border-border rounded-xl p-4 shadow-xl">
      <div className="flex items-center justify-between mb-3 border-b border-border pb-2">
        <div className="flex items-center gap-2">
          <BarChart3 className="w-4 h-4 text-accent" />
          <h3 className="font-bold text-xs text-slate-100 uppercase tracking-wider">
            Currency Relative Strength Heatmap
          </h3>
        </div>
        <span className="text-[11px] text-slate-400 font-mono">
          Basket Aggregate ({heatmap.timeframe})
        </span>
      </div>

      {/* Recommended Long Setup */}
      <div className="mb-3 px-3 py-2 rounded-lg bg-accent/10 border border-accent/30 flex items-center justify-between text-xs font-mono">
        <span className="text-slate-300 flex items-center gap-1">
          <Sparkles className="w-3.5 h-3.5 text-accent" /> Optimal Relative Pair:
        </span>
        <span className="font-bold text-accent px-2 py-0.5 rounded bg-accent/20">
          {best_long_opportunity} (Long {strongest} vs Short {weakest})
        </span>
      </div>

      {/* Currency Strength Bars */}
      <div className="space-y-2">
        {rankings.map(({ currency, score }) => {
          const isPos = score >= 0;
          const absPct = Math.min(100, Math.abs(score) * 100);

          return (
            <div key={currency} className="flex items-center gap-2 text-xs font-mono">
              <span className="w-9 font-bold text-slate-200">{currency}</span>

              {/* Centered zero bar chart */}
              <div className="flex-1 h-3 bg-surface-raised rounded flex overflow-hidden relative">
                {/* Left side: Negative */}
                <div className="w-1/2 flex justify-end">
                  {!isPos && (
                    <div
                      style={{ width: `${absPct}%` }}
                      className="h-full bg-rose-500 rounded-l"
                    />
                  )}
                </div>
                {/* Center marker */}
                <div className="w-0.5 h-full bg-slate-600 z-10"></div>
                {/* Right side: Positive */}
                <div className="w-1/2 flex justify-start">
                  {isPos && (
                    <div
                      style={{ width: `${absPct}%` }}
                      className="h-full bg-emerald-500 rounded-r"
                    />
                  )}
                </div>
              </div>

              <span
                className={`w-12 text-right font-bold ${
                  isPos ? "text-emerald-400" : "text-rose-400"
                }`}
              >
                {score >= 0 ? `+${score.toFixed(2)}` : score.toFixed(2)}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
