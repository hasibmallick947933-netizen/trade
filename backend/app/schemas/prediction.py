"""
Pydantic Schemas for Predictions, Signals, Risk, and Heatmap
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class PriceRange(BaseModel):
    low: float
    high: float


class EntryZone(BaseModel):
    min: float
    max: float


class PredictionResponse(BaseModel):
    pair: str
    timeframe: str
    current_price: float
    prob_buy: float
    prob_sell: float
    prob_hold: float
    confidence: float
    signal_state: str
    market_direction: str
    market_regime: str
    expected_price_range: PriceRange
    expected_return_pct: float
    expected_volatility_pct: float
    entry_zone: EntryZone
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    sl_pips: Optional[float] = 20.0
    tp_pips: Optional[float] = 40.0
    risk_reward_ratio: float
    suggested_lot_size: float
    account_risk_cash: float
    factors_supporting: List[str]
    factors_opposing: List[str]
    explanation_summary: str
    horizons: Dict[str, Any]
    detected_patterns: List[Dict[str, Any]]
    support_levels: List[float]
    resistance_levels: List[float]
    order_blocks: List[Dict[str, Any]]
    multi_timeframe: Dict[str, Any]
    macro_bias: Dict[str, Any]


class CurrencyHeatmapResponse(BaseModel):
    timeframe: str
    strengths: Dict[str, float]
    rankings: List[Dict[str, Any]]
    strongest: str
    weakest: str
    best_long_opportunity: str
