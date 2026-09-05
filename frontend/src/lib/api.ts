/**
 * Typed API Client for FOREX AI Backend
 */

export const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface Candle {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  is_complete: boolean;
}

export interface Quote {
  pair: string;
  bid: number;
  ask: number;
  spread: number;
  mid: number;
  timestamp: string;
}

export interface PairInfo {
  symbol: string;
  base_currency: string;
  quote_currency: string;
  pip_size: number;
  typical_spread_pips: number;
}

export interface Prediction {
  pair: string;
  timeframe: string;
  current_price: number;
  prob_buy: number;
  prob_sell: number;
  prob_hold: number;
  confidence: number;
  signal_state: string;
  market_direction: string;
  market_regime: string;
  expected_price_range: {
    low: number;
    high: number;
  };
  expected_return_pct: number;
  expected_volatility_pct: number;
  entry_zone: {
    min: number;
    max: number;
  };
  stop_loss: number;
  take_profit_1: number;
  take_profit_2: number;
  risk_reward_ratio: number;
  suggested_lot_size: number;
  account_risk_cash: number;
  factors_supporting: string[];
  factors_opposing: string[];
  explanation_summary: string;
  horizons: Record<string, { buy: number; sell: number; hold: number }>;
  detected_patterns: Array<{
    name: string;
    direction: string;
    base_effectiveness: number;
    timestamp: string;
  }>;
  support_levels: number[];
  resistance_levels: number[];
  order_blocks: Array<{
    type: string;
    top: number;
    bottom: number;
  }>;
  multi_timeframe: {
    alignment: string;
    alignment_score: number;
    timeframes: Record<string, any>;
  };
  macro_bias: {
    bias: string;
    description: string;
    differential: number;
  };
}

export interface CurrencyHeatmap {
  timeframe: string;
  strengths: Record<string, number>;
  rankings: Array<{ currency: string; score: number }>;
  strongest: string;
  weakest: string;
  best_long_opportunity: string;
}

export interface EconomicEvent {
  id: number;
  currency: string;
  country: string;
  event_name: string;
  timestamp: string;
  impact: string;
  actual: number | null;
  forecast: number | null;
  previous: number | null;
  surprise: number | null;
  bias: string;
}

export interface BacktestResult {
  pair: string;
  timeframe: string;
  initial_capital: number;
  final_capital: number;
  net_profit: number;
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  win_rate_pct: number;
  profit_factor: number;
  cagr_pct: number;
  max_drawdown_pct: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  average_win: number;
  average_loss: number;
  expectancy: number;
  consecutive_wins: number;
  consecutive_losses: number;
  equity_curve: Array<{ timestamp: string; equity: number; drawdown_pct: number }>;
  trades: Array<{
    trade_id: number;
    direction: string;
    entry_time: string;
    entry_price: number;
    exit_time: string;
    exit_price: number;
    lot_size: number;
    pnl: number;
    return_pct: number;
    exit_reason: string;
  }>;
}

export async function fetchPairs(): Promise<PairInfo[]> {
  const res = await fetch(`${API_BASE}/market/pairs`);
  if (!res.ok) throw new Error("Failed to fetch pairs");
  return res.json();
}

export async function fetchCandles(pair: string, timeframe: string, limit = 150): Promise<Candle[]> {
  const res = await fetch(`${API_BASE}/market/candles?pair=${encodeURIComponent(pair)}&timeframe=${timeframe}&limit=${limit}`);
  if (!res.ok) throw new Error("Failed to fetch candles");
  return res.json();
}

export async function fetchPrediction(pair: string, timeframe: string): Promise<Prediction> {
  const res = await fetch(`${API_BASE}/predictions/latest?pair=${encodeURIComponent(pair)}&timeframe=${timeframe}`);
  if (!res.ok) throw new Error("Failed to fetch prediction");
  return res.json();
}

export async function fetchHeatmap(timeframe: string): Promise<CurrencyHeatmap> {
  const res = await fetch(`${API_BASE}/analysis/heatmap?timeframe=${timeframe}`);
  if (!res.ok) throw new Error("Failed to fetch heatmap");
  return res.json();
}

export async function fetchCalendar(): Promise<EconomicEvent[]> {
  const res = await fetch(`${API_BASE}/macro/calendar`);
  if (!res.ok) throw new Error("Failed to fetch economic calendar");
  return res.json();
}

export async function runBacktest(params: {
  pair: string;
  timeframe: string;
  bars: number;
  initial_capital: number;
  risk_per_trade_pct: number;
  spread_pips: number;
  slippage_pips: number;
}): Promise<BacktestResult> {
  const res = await fetch(`${API_BASE}/backtest/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  if (!res.ok) throw new Error("Failed to run backtest");
  return res.json();
}

export async function queryAIChat(query: string, pair: string, timeframe: string) {
  const res = await fetch(`${API_BASE}/chat/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, pair, timeframe }),
  });
  if (!res.ok) throw new Error("Chat query failed");
  return res.json();
}
