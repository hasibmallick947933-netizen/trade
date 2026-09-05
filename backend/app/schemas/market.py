"""
Pydantic Schemas for Market Data and Analysis
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class CandleResponse(BaseModel):
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    is_complete: bool


class QuoteResponse(BaseModel):
    pair: str
    bid: float
    ask: float
    spread: float
    mid: float
    timestamp: str


class PairInfo(BaseModel):
    symbol: str
    base_currency: str
    quote_currency: str
    pip_size: float
    typical_spread_pips: float


class TechnicalAnalysisResponse(BaseModel):
    pair: str
    timeframe: str
    current_price: float
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    ema_20: Optional[float] = None
    ema_50: Optional[float] = None
    ema_200: Optional[float] = None
    rsi_14: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_hist: Optional[float] = None
    atr_14: Optional[float] = None
    adx_14: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_middle: Optional[float] = None
    bb_lower: Optional[float] = None
    stoch_k: Optional[float] = None
    stoch_d: Optional[float] = None
    williams_r: Optional[float] = None
    detected_patterns: List[Dict[str, Any]]
    market_structure: Dict[str, Any]
