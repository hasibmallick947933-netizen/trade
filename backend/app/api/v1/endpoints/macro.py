"""
Macroeconomic Calendar and Cross-Asset Endpoints
"""

from fastapi import APIRouter, Query
from backend.app.services.macro_engine import MacroEngine

router = APIRouter()
macro_engine = MacroEngine()


@router.get("/calendar")
async def get_calendar():
    """Retrieve high-impact economic calendar events and surprises."""
    return macro_engine.get_calendar()


@router.get("/scores")
async def get_macro_scores():
    """Retrieve relative currency fundamental scores."""
    return macro_engine.get_macro_scores()


@router.get("/bias")
async def get_pair_macro_bias(pair: str = Query("EUR/USD")):
    """Evaluate fundamental macro bias for a specific currency pair."""
    return macro_engine.get_pair_macro_bias(pair)


@router.get("/yields")
async def get_yields():
    """Get US Treasury yields (2Y, 10Y), yield curve slope, and cross-asset correlations."""
    return macro_engine.get_bond_yields_and_cross_assets()
