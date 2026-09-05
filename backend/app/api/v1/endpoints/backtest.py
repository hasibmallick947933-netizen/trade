"""
Backtesting and AI Chat Endpoints
"""

from fastapi import APIRouter, HTTPException
from data.providers.mock_provider import GarchMockMarketDataProvider
from backtesting.engine import BacktestEngine
from backend.app.services.multi_timeframe import MultiTimeframeEngine
from backend.app.services.macro_engine import MacroEngine
from backend.app.services.prediction_engine import PredictionEngine
from backend.app.services.currency_heatmap import CurrencyHeatmapEngine
from backend.app.services.chat_engine import ForexAIChatAssistant
from backend.app.schemas.backtest import BacktestRequest, BacktestResponse, ChatRequest, ChatResponse

router = APIRouter()
provider = GarchMockMarketDataProvider()
backtest_engine = BacktestEngine(provider)
mtf_engine = MultiTimeframeEngine(provider)
macro_engine = MacroEngine()
prediction_engine = PredictionEngine(mtf_engine, macro_engine)
heatmap_engine = CurrencyHeatmapEngine(provider)
chat_assistant = ForexAIChatAssistant(prediction_engine, heatmap_engine)


@router.post("/backtest/run", response_model=BacktestResponse)
async def run_backtest(req: BacktestRequest):
    """Execute a point-in-time walk-forward backtest accounting for spread and slippage."""
    try:
        res = await backtest_engine.run_backtest(
            pair=req.pair,
            timeframe=req.timeframe,
            bars=req.bars,
            initial_capital=req.initial_capital,
            risk_per_trade_pct=req.risk_per_trade_pct,
            spread_pips=req.spread_pips,
            slippage_pips=req.slippage_pips,
        )
        return BacktestResponse(**res)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/chat/query", response_model=ChatResponse)
async def chat_query(req: ChatRequest):
    """Context-grounded Forex conversational agent."""
    try:
        res = await chat_assistant.respond(
            query=req.query,
            active_pair=req.pair,
            timeframe=req.timeframe,
        )
        return ChatResponse(**res)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
