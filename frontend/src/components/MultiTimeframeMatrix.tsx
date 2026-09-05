"use client";

import React from "react";
import { Layers, ArrowUpRight, ArrowDownRight, Minus } from "lucide-react";

interface MultiTimeframeMatrixProps {
  mtfData: {
    alignment: string;
    alignment_score: number;
    timeframes: Record<string, any>;
  } | null;
}

export const MultiTimeframeMatrix: React.FC<MultiTimeframeMatrixProps> = ({ mtfData }) => {
  if (!mtfData) {
    return (
      <div className="bg-surface border border-border rounded-xl p-4 animate-pulse min-h-[200px]">
        <div className="h-5 bg-surface-raised rounded w-1/3 mb-3"></div>
        <div className="h-28 bg-surface-raised rounded"></div>
      </div>
    );
  }

  const { alignment, alignment_score, timeframes } = mtfData;

  const getAlignmentColor = () => {
    if (alignment.includes("STRONG BULLISH")) return "bg-emerald-500/20 text-emerald-400 border-emerald-500/40";
    if (alignment.includes("MODERATE BULLISH")) return "bg-emerald-500/10 text-emerald-300 border-emerald-500/30";
    if (alignment.includes("STRONG BEARISH")) return "bg-rose-500/20 text-rose-400 border-rose-500/40";
    if (alignment.includes("MODERATE BEARISH")) return "bg-rose-500/10 text-rose-300 border-rose-500/30";
    return "bg-amber-500/15 text-amber-300 border-amber-500/30";
  };

  const tfList = ["1D", "4H", "1H", "15M", "5M"];

  return (
    <div className="bg-surface border border-border rounded-xl p-4 shadow-xl">
      <div className="flex items-center justify-between mb-3 border-b border-border pb-2">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-accent" />
          <h3 className="font-bold text-xs text-slate-100 uppercase tracking-wider">
            Multi-Timeframe Confluence
          </h3>
        </div>
        <span
          className={`px-2.5 py-0.5 rounded text-xs font-mono font-bold border uppercase ${getAlignmentColor()}`}
        >
          {alignment} ({alignment_score > 0 ? `+${alignment_score}` : alignment_score})
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs font-mono">
          <thead>
            <tr className="border-b border-border/60 text-slate-400 text-[10px] uppercase">
              <th className="py-1.5 px-2">TF</th>
              <th className="py-1.5 px-2">Bias</th>
              <th className="py-1.5 px-2">Close</th>
              <th className="py-1.5 px-2">EMA20</th>
              <th className="py-1.5 px-2">RSI</th>
              <th className="py-1.5 px-2">ADX</th>
              <th className="py-1.5 px-2">Structure</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/40">
            {tfList.map((tf) => {
              const d = timeframes[tf];
              if (!d) return null;
              const isBull = d.bias === "BULLISH";
              const isBear = d.bias === "BEARISH";

              return (
                <tr key={tf} className="hover:bg-surface-raised/40 transition">
                  <td className="py-2 px-2 font-bold text-slate-200">{tf}</td>
                  <td className="py-2 px-2">
                    <span
                      className={`inline-flex items-center gap-1 font-semibold ${
                        isBull
                          ? "text-emerald-400"
                          : isBear
                          ? "text-rose-400"
                          : "text-slate-400"
                      }`}
                    >
                      {isBull && <ArrowUpRight className="w-3 h-3" />}
                      {isBear && <ArrowDownRight className="w-3 h-3" />}
                      {!isBull && !isBear && <Minus className="w-3 h-3" />}
                      {d.bias}
                    </span>
                  </td>
                  <td className="py-2 px-2 text-slate-200">{d.close.toFixed(5)}</td>
                  <td className="py-2 px-2 text-sky-400">{d.ema_20.toFixed(5)}</td>
                  <td className="py-2 px-2 text-slate-300">{d.rsi_14}</td>
                  <td className="py-2 px-2 text-slate-300">{d.adx_14}</td>
                  <td className="py-2 px-2">
                    <span className="text-[11px] px-1.5 py-0.5 rounded bg-surface-raised text-slate-300 border border-border">
                      {d.structure}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
