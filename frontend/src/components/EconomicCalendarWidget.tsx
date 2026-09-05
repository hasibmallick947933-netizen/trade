"use client";

import React from "react";
import { EconomicEvent } from "@/lib/api";
import { Calendar, AlertCircle } from "lucide-react";

interface EconomicCalendarWidgetProps {
  events: EconomicEvent[];
  loading: boolean;
}

export const EconomicCalendarWidget: React.FC<EconomicCalendarWidgetProps> = ({ events, loading }) => {
  if (loading || events.length === 0) {
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

  return (
    <div className="bg-surface border border-border rounded-xl p-4 shadow-xl">
      <div className="flex items-center justify-between mb-3 border-b border-border pb-2">
        <div className="flex items-center gap-2">
          <Calendar className="w-4 h-4 text-accent" />
          <h3 className="font-bold text-xs text-slate-100 uppercase tracking-wider">
            Economic Calendar & Surprises
          </h3>
        </div>
        <span className="text-[11px] text-slate-400 font-mono">
          Actual vs Forecast
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs font-mono">
          <thead>
            <tr className="border-b border-border/60 text-slate-400 text-[10px] uppercase">
              <th className="py-1 px-2">Cur</th>
              <th className="py-1 px-2">Event</th>
              <th className="py-1 px-2">Impact</th>
              <th className="py-1 px-2">Actual</th>
              <th className="py-1 px-2">Forecast</th>
              <th className="py-1 px-2">Surprise</th>
              <th className="py-1 px-2">Implication</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/40">
            {events.map((ev) => {
              const hasSurprise = ev.surprise !== null;
              const isPositiveSurprise = (ev.surprise || 0) > 0;

              return (
                <tr key={ev.id} className="hover:bg-surface-raised/40 transition">
                  <td className="py-2 px-2 font-bold text-slate-100">{ev.currency}</td>
                  <td className="py-2 px-2 text-slate-200 font-sans text-xs">{ev.event_name}</td>
                  <td className="py-2 px-2">
                    <span
                      className={`text-[9px] px-1.5 py-0.5 rounded font-bold uppercase ${
                        ev.impact === "HIGH"
                          ? "bg-rose-500/20 text-rose-400 border border-rose-500/30"
                          : "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                      }`}
                    >
                      {ev.impact}
                    </span>
                  </td>
                  <td className="py-2 px-2 font-bold text-slate-100">
                    {ev.actual !== null ? ev.actual : "—"}
                  </td>
                  <td className="py-2 px-2 text-slate-400">
                    {ev.forecast !== null ? ev.forecast : "—"}
                  </td>
                  <td className="py-2 px-2">
                    {hasSurprise ? (
                      <span
                        className={`font-bold ${
                          isPositiveSurprise ? "text-emerald-400" : "text-rose-400"
                        }`}
                      >
                        {isPositiveSurprise ? `+${ev.surprise}` : ev.surprise}
                      </span>
                    ) : (
                      <span className="text-slate-500">PENDING</span>
                    )}
                  </td>
                  <td className="py-2 px-2">
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-surface-raised text-slate-300 border border-border">
                      {ev.bias.replace(/_/g, " ")}
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
