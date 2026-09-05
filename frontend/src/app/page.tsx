"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  fetchPairs,
  fetchCandles,
  fetchPrediction,
  fetchHeatmap,
  fetchCalendar,
  Candle,
  Prediction,
  CurrencyHeatmap,
  EconomicEvent,
} from "@/lib/api";
import { Header } from "@/components/Header";
import { CandlestickChart } from "@/components/CandlestickChart";
import { PredictionCard } from "@/components/PredictionCard";
import { ReasoningCard } from "@/components/ReasoningCard";
import { MultiTimeframeMatrix } from "@/components/MultiTimeframeMatrix";
import { CurrencyHeatmapWidget } from "@/components/CurrencyHeatmap";
import { EconomicCalendarWidget } from "@/components/EconomicCalendarWidget";
import { BacktestModal } from "@/components/BacktestModal";
import { AIChatModal } from "@/components/AIChatModal";
import { RefreshCw } from "lucide-react";

export default function ForexAITerminal() {
  const [pairs, setPairs] = useState<string[]>([
    "EUR/USD",
    "GBP/USD",
    "USD/JPY",
    "USD/CHF",
    "AUD/USD",
    "USD/CAD",
    "NZD/USD",
    "EUR/GBP",
    "EUR/JPY",
    "GBP/JPY",
  ]);
  const timeframes = ["1M", "5M", "15M", "30M", "1H", "4H", "1D"];

  const [selectedPair, setSelectedPair] = useState("EUR/USD");
  const [selectedTimeframe, setSelectedTimeframe] = useState("1H");

  const [candles, setCandles] = useState<Candle[]>([]);
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [heatmap, setHeatmap] = useState<CurrencyHeatmap | null>(null);
  const [events, setEvents] = useState<EconomicEvent[]>([]);

  const [loading, setLoading] = useState(true);
  const [lastRefreshed, setLastRefreshed] = useState<Date>(new Date());
  const [isBacktestOpen, setIsBacktestOpen] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);

  // Load available pairs on mount
  useEffect(() => {
    fetchPairs()
      .then((data) => {
        if (data && data.length > 0) {
          setPairs(data.map((p) => p.symbol));
        }
      })
      .catch(() => {});
  }, []);

  // Main data fetching function
  const loadMarketData = useCallback(async () => {
    try {
      const [candleData, predData, heatmapData, calData] = await Promise.all([
        fetchCandles(selectedPair, selectedTimeframe, 80),
        fetchPrediction(selectedPair, selectedTimeframe),
        fetchHeatmap(selectedTimeframe),
        fetchCalendar(),
      ]);

      setCandles(candleData);
      setPrediction(predData);
      setHeatmap(heatmapData);
      setEvents(calData);
      setLastRefreshed(new Date());
    } catch (err) {
      console.error("Error loading market data:", err);
    } finally {
      setLoading(false);
    }
  }, [selectedPair, selectedTimeframe]);

  // Trigger load on pair or timeframe change
  useEffect(() => {
    setLoading(true);
    loadMarketData();
  }, [loadMarketData]);

  // Periodic polling for simulated live market tick updates (every 5 seconds)
  useEffect(() => {
    const timer = setInterval(() => {
      loadMarketData();
    }, 5000);
    return () => clearInterval(timer);
  }, [loadMarketData]);

  return (
    <div className="min-h-screen flex flex-col bg-background text-slate-100">
      {/* Navigation & Control Header */}
      <Header
        pair={selectedPair}
        setPair={setSelectedPair}
        timeframe={selectedTimeframe}
        setTimeframe={setSelectedTimeframe}
        pairs={pairs}
        timeframes={timeframes}
        onOpenBacktest={() => setIsBacktestOpen(true)}
        onOpenChat={() => setIsChatOpen(true)}
      />

      {/* Main Terminal Workspace */}
      <main className="flex-1 p-4 max-w-[1920px] w-full mx-auto space-y-4">
        {/* Row 1: Chart (Left) + Prediction & Risk (Right) */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
          {/* Candlestick Chart Area (7 Cols) */}
          <div className="lg:col-span-7 flex flex-col h-[520px]">
            <CandlestickChart
              candles={candles}
              prediction={prediction}
              pair={selectedPair}
              timeframe={selectedTimeframe}
            />
          </div>

          {/* AI Calibrated Prediction & Risk Targets (5 Cols) */}
          <div className="lg:col-span-5 flex flex-col">
            <PredictionCard prediction={prediction} loading={loading} />
          </div>
        </div>

        {/* Row 2: AI Explainability (6 Cols) + Multi-Timeframe Alignment (6 Cols) */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
          <div className="lg:col-span-6 flex flex-col">
            <ReasoningCard prediction={prediction} loading={loading} />
          </div>
          <div className="lg:col-span-6 flex flex-col">
            <MultiTimeframeMatrix mtfData={prediction?.multi_timeframe || null} />
          </div>
        </div>

        {/* Row 3: Currency Heatmap (5 Cols) + Economic Calendar (7 Cols) */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
          <div className="lg:col-span-5 flex flex-col">
            <CurrencyHeatmapWidget heatmap={heatmap} loading={loading} />
          </div>
          <div className="lg:col-span-7 flex flex-col">
            <EconomicCalendarWidget events={events} loading={loading} />
          </div>
        </div>
      </main>

      {/* Terminal Footer Bar */}
      <footer className="border-t border-border bg-surface px-4 py-2.5 text-[11px] font-mono text-slate-400 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-4">
          <span>Active Asset: <strong className="text-slate-200">{selectedPair}</strong></span>
          <span>Timeframe: <strong className="text-slate-200">{selectedTimeframe}</strong></span>
          <span>
            Current Bid/Ask Spread:{" "}
            <strong className="text-emerald-400">
              {prediction ? `${(prediction.current_price * 0.0001).toFixed(5)}` : "1.2 pips"}
            </strong>
          </span>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => loadMarketData()}
            className="flex items-center gap-1 hover:text-slate-200 transition"
          >
            <RefreshCw className="w-3 h-3 text-accent" />
            <span>Updated: {lastRefreshed.toLocaleTimeString()}</span>
          </button>
          <span className="text-slate-600">|</span>
          <span className="text-slate-500">
            Forex AI Quantitative Platform • Probabilistic Estimator
          </span>
        </div>
      </footer>

      {/* Backtesting Studio Modal */}
      <BacktestModal
        isOpen={isBacktestOpen}
        onClose={() => setIsBacktestOpen(false)}
        defaultPair={selectedPair}
        defaultTimeframe={selectedTimeframe}
      />

      {/* Conversational Analyst Chat Modal */}
      <AIChatModal
        isOpen={isChatOpen}
        onClose={() => setIsChatOpen(false)}
        activePair={selectedPair}
        activeTimeframe={selectedTimeframe}
      />
    </div>
  );
}
