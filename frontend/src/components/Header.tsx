"use client";

import React from "react";
import { Activity, Bot, History, Sliders, Zap } from "lucide-react";

interface HeaderProps {
  pair: string;
  setPair: (p: string) => void;
  timeframe: string;
  setTimeframe: (tf: string) => void;
  pairs: string[];
  timeframes: string[];
  onOpenBacktest: () => void;
  onOpenChat: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  pair,
  setPair,
  timeframe,
  setTimeframe,
  pairs,
  timeframes,
  onOpenBacktest,
  onOpenChat,
}) => {
  return (
    <header className="border-b border-border bg-surface px-4 py-3 sticky top-0 z-40">
      <div className="flex flex-wrap items-center justify-between gap-4 max-w-[1920px] mx-auto">
        {/* Brand & Status */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded bg-gradient-to-tr from-accent to-blue-500 flex items-center justify-center font-bold text-white shadow-lg shadow-accent/20">
              FX
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold tracking-wider text-base text-slate-100">
                  FOREX <span className="text-accent">AI</span>
                </span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-surface-raised border border-border text-slate-400 font-mono">
                  v1.0.0
                </span>
              </div>
              <p className="text-[11px] text-slate-400">
                Institutional Quant & Explainable Signal Terminal
              </p>
            </div>
          </div>

          <div className="hidden lg:flex items-center gap-2 pl-4 border-l border-border text-xs text-slate-300">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="font-mono text-emerald-400 text-[11px]">LIVE ENGINE ACTIVE</span>
          </div>
        </div>

        {/* Pair & Timeframe Selectors */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Pair Selector */}
          <div className="relative">
            <select
              value={pair}
              onChange={(e) => setPair(e.target.value)}
              className="bg-surface-raised border border-border text-slate-100 text-sm font-semibold rounded-lg px-3 py-1.5 pr-8 focus:outline-none focus:border-accent cursor-pointer hover:bg-slate-800 transition"
            >
              {pairs.map((p) => (
                <option key={p} value={p}>
                  {p}
                </option>
              ))}
            </select>
          </div>

          {/* Timeframe Buttons */}
          <div className="flex items-center bg-surface-raised border border-border rounded-lg p-0.5">
            {timeframes.map((tf) => (
              <button
                key={tf}
                onClick={() => setTimeframe(tf)}
                className={`px-2.5 py-1 text-xs font-mono font-medium rounded-md transition ${
                  timeframe === tf
                    ? "bg-accent text-white shadow-sm"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
                }`}
              >
                {tf}
              </button>
            ))}
          </div>
        </div>

        {/* Action Tools */}
        <div className="flex items-center gap-2">
          <button
            onClick={onOpenBacktest}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-surface-raised border border-border hover:border-accent/60 text-slate-200 hover:text-white rounded-lg text-xs font-medium transition shadow-sm"
          >
            <History className="w-3.5 h-3.5 text-accent" />
            <span>Backtest Studio</span>
          </button>

          <button
            onClick={onOpenChat}
            className="flex items-center gap-1.5 px-3.5 py-1.5 bg-accent hover:bg-accent/90 text-white rounded-lg text-xs font-medium transition shadow-sm shadow-accent/30"
          >
            <Bot className="w-3.5 h-3.5" />
            <span>AI Analyst Chat</span>
          </button>
        </div>
      </div>
    </header>
  );
};
