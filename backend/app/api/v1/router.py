"""
API V1 Master Router
Aggregates market, analysis, predictions, macro, backtest, and chat routes.
"""

from fastapi import APIRouter
from backend.app.api.v1.endpoints import market, analysis, predictions, macro, backtest

api_router = APIRouter()

api_router.include_router(market.router, prefix="/market", tags=["Market Data"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["Technical Analysis & Structure"])
api_router.include_router(predictions.router, prefix="/predictions", tags=["ML Predictions & Signals"])
api_router.include_router(macro.router, prefix="/macro", tags=["Macro & Cross-Asset"])
api_router.include_router(backtest.router, prefix="", tags=["Backtesting & AI Chat"])
