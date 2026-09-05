"""
Technical and Market Structure Analysis Endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from data.providers.mock_provider import GarchMockMarketDataProvider
from backend.app.services.technical_analysis import TechnicalAnalysisEngine
from backend.app.services.market_structure import MarketStructureEngine
from backend.app.services.multi_timeframe import MultiTimeframeEngine
from backend.app.services.currency_heatmap import CurrencyHeatmapEngine
from backend.app.schemas.market import TechnicalAnalysisResponse
from backend.app.schemas.prediction import CurrencyHeatmapResponse

router = APIRouter()
provider = GarchMockMarketDataProvider()
mtf_engine = MultiTimeframeEngine(provider)
heatmap_engine = CurrencyHeatmapEngine(provider)


@router.get("/technical", response_model=TechnicalAnalysisResponse)
async def get_technical(
    pair: str = Query("EUR/USD"),
    timeframe: str = Query("1H"),
    limit: int = Query(100, ge=30, le=500),
):
    """Compute complete quantitative indicator suite and detect candlestick patterns."""
    try:
        df = await provider.get_candles(pair, timeframe, limit=limit)
        df_ind = TechnicalAnalysisEngine.calculate_indicators(df)
        patterns = TechnicalAnalysisEngine.detect_candlestick_patterns(df_ind, lookback=5)
        structure = MarketStructureEngine.analyze_structure(df_ind)

        last_row = df_ind.iloc[-1]
        return TechnicalAnalysisResponse(
            pair=pair,
            timeframe=timeframe,
            current_price=float(last_row["close"]),
            sma_20=float(last_row["sma_20"]),
            sma_50=float(last_row["sma_50"]),
            sma_200=float(last_row["sma_200"]),
            ema_20=float(last_row["ema_20"]),
            ema_50=float(last_row["ema_50"]),
            ema_200=float(last_row["ema_200"]),
            rsi_14=round(float(last_row["rsi_14"]), 1),
            macd=round(float(last_row["macd"]), 5),
            macd_signal=round(float(last_row["macd_signal"]), 5),
            macd_hist=round(float(last_row["macd_hist"]), 5),
            atr_14=round(float(last_row["atr_14"]), 5),
            adx_14=round(float(last_row["adx_14"]), 1),
            bb_upper=round(float(last_row["bb_upper"]), 5),
            bb_middle=round(float(last_row["bb_middle"]), 5),
            bb_lower=round(float(last_row["bb_lower"]), 5),
            stoch_k=round(float(last_row["stoch_k"]), 1),
            stoch_d=round(float(last_row["stoch_d"]), 1),
            williams_r=round(float(last_row["williams_r"]), 1),
            detected_patterns=patterns,
            market_structure=structure,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/multi-timeframe")
async def get_multi_timeframe(pair: str = Query("EUR/USD")):
    """Analyze trend confluence across 1D, 4H, 1H, 15M, and 5M timeframes."""
    try:
        res = await mtf_engine.analyze_pair(pair)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/heatmap", response_model=CurrencyHeatmapResponse)
async def get_heatmap(timeframe: str = Query("1H")):
    """Get currency relative strength indices across 8 major currencies."""
    try:
        res = await heatmap_engine.calculate_strength(timeframe)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
