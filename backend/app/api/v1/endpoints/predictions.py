"""
Probabilistic Prediction and Explainability Endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from data.providers.mock_provider import GarchMockMarketDataProvider
from backend.app.services.multi_timeframe import MultiTimeframeEngine
from backend.app.services.macro_engine import MacroEngine
from backend.app.services.prediction_engine import PredictionEngine
from backend.app.schemas.prediction import PredictionResponse

router = APIRouter()
provider = GarchMockMarketDataProvider()
mtf_engine = MultiTimeframeEngine(provider)
macro_engine = MacroEngine()
prediction_engine = PredictionEngine(mtf_engine, macro_engine)


@router.get("/latest", response_model=PredictionResponse)
async def get_latest_prediction(
    pair: str = Query("EUR/USD"),
    timeframe: str = Query("1H"),
    account_balance: float = Query(100000.0, ge=100.0),
    risk_pct: float = Query(1.0, ge=0.1, le=10.0),
):
    """
    Generate calibrated probabilistic prediction (BUY/SELL/HOLD), confidence score,
    regime detection, risk zones (SL/TP1/TP2), and explainability factors.
    """
    try:
        pred = await prediction_engine.generate_prediction(
            pair=pair,
            timeframe=timeframe,
            account_balance=account_balance,
            risk_pct=risk_pct,
        )
        return PredictionResponse(**pred)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
