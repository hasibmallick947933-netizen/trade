"use client";

import React from "react";
import { Prediction } from "@/lib/api";
import { CheckCircle2, AlertTriangle, Lightbulb, Sparkles } from "lucide-react";

interface ReasoningCardProps {
  prediction: Prediction | null;
  loading: boolean;
}

export const ReasoningCard: React.FC<ReasoningCardProps> = ({ prediction, loading }) => {
  if (loading || !prediction) {
    return (
      <div className="bg-surface border border-border rounded-xl p-5 animate-pulse min-h-[300px]">
        <div className="h-5 bg-surface-raised rounded w-1/4 mb-4"></div>
        <div className="space-y-3">
          <div className="h-4 bg-surface-raised rounded w-5/6"></div>
          <div className="h-4 bg-surface-raised rounded w-4/6"></div>
          <div className="h-4 bg-surface-raised rounded w-3/6"></div>
        </div>
      </div>
    );
  }

  const { factors_supporting, factors_opposing, explanation_summary, detected_patterns } = prediction;

  return (
    <div className="bg-surface border border-border rounded-xl p-5 flex flex-col justify-between shadow-xl">
      <div>
        {/* Title */}
        <div className="flex items-center justify-between mb-3 border-b border-border pb-2.5">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-accent" />
            <h3 className="font-bold text-sm text-slate-100 uppercase tracking-wider">
              AI Explainability & Rationale
            </h3>
          </div>
          <span className="text-[11px] text-slate-400 font-mono">
            SHAP & Rule Attribution
          </span>
        </div>

        {/* Synthesis Box */}
        <div className="mb-4 p-3 rounded-lg bg-surface-raised border border-accent/20 flex gap-2.5 items-start">
          <Lightbulb className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
          <p className="text-xs text-slate-200 leading-relaxed font-sans">
            {explanation_summary}
          </p>
        </div>

        {/* Two-Column Factor Attribution */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Supporting Factors */}
          <div className="p-3 rounded-lg bg-emerald-950/20 border border-emerald-500/20">
            <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-400 uppercase mb-2">
              <CheckCircle2 className="w-3.5 h-3.5" /> Supporting Factors ({factors_supporting.length})
            </div>
            <ul className="space-y-1.5 text-xs text-slate-300">
              {factors_supporting.map((factor, idx) => (
                <li key={idx} className="flex items-start gap-1.5">
                  <span className="text-emerald-500 font-bold shrink-0">✓</span>
                  <span>{factor}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Opposing Factors / Risks */}
          <div className="p-3 rounded-lg bg-rose-950/20 border border-rose-500/20">
            <div className="flex items-center gap-1.5 text-xs font-bold text-rose-400 uppercase mb-2">
              <AlertTriangle className="w-3.5 h-3.5" /> Risk Factors ({factors_opposing.length})
            </div>
            <ul className="space-y-1.5 text-xs text-slate-300">
              {factors_opposing.map((factor, idx) => (
                <li key={idx} className="flex items-start gap-1.5">
                  <span className="text-rose-400 font-bold shrink-0">⚠</span>
                  <span>{factor}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Detected Candlestick Patterns */}
      {detected_patterns.length > 0 && (
        <div className="mt-4 pt-3 border-t border-border">
          <div className="text-[11px] text-slate-400 uppercase tracking-wider mb-2 font-mono">
            Active Candlestick Formations
          </div>
          <div className="flex flex-wrap gap-2">
            {detected_patterns.map((p, idx) => (
              <span
                key={idx}
                className={`text-[11px] font-mono px-2 py-1 rounded border flex items-center gap-1.5 ${
                  p.direction === "BULLISH"
                    ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
                    : p.direction === "BEARISH"
                    ? "bg-rose-500/10 text-rose-400 border-rose-500/30"
                    : "bg-slate-700/20 text-slate-300 border-slate-600/30"
                }`}
              >
                <span>{p.name.replace(/_/g, " ")}</span>
                <span className="text-[9px] px-1 rounded bg-black/40 text-slate-300">
                  {Math.round(p.base_effectiveness * 100)}% Win
                </span>
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
