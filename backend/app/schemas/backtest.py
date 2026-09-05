"""
Pydantic Schemas for Backtest Engine and AI Chat
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class BacktestRequest(BaseModel):
    pair: str = "EUR/USD"
    timeframe: str = "1H"
    bars: int = Field(default=400, ge=100, le=2000)
    initial_capital: float = Field(default=100000.0, ge=1000.0)
    risk_per_trade_pct: float = Field(default=1.0, ge=0.1, le=10.0)
    spread_pips: float = Field(default=1.2, ge=0.0)
    slippage_pips: float = Field(default=0.5, ge=0.0)


class BacktestResponse(BaseModel):
    pair: str
    timeframe: str
    initial_capital: float
    final_capital: float
    net_profit: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate_pct: float
    profit_factor: float
    cagr_pct: float
    max_drawdown_pct: float
    sharpe_ratio: float
    sortino_ratio: float
    average_win: float
    average_loss: float
    expectancy: float
    consecutive_wins: int
    consecutive_losses: int
    spread_pips: float
    slippage_pips: float
    equity_curve: List[Dict[str, Any]]
    trades: List[Dict[str, Any]]


class ChatRequest(BaseModel):
    query: str
    pair: str = "EUR/USD"
    timeframe: str = "1H"


class ChatResponse(BaseModel):
    query: str
    pair: str
    timeframe: str
    response: str
    citations: List[str]
