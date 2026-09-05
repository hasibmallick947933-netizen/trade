"""
Market Data Endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from data.providers.mock_provider import GarchMockMarketDataProvider, PAIR_CONFIGS
from backend.app.schemas.market import CandleResponse, QuoteResponse, PairInfo

router = APIRouter()
provider = GarchMockMarketDataProvider()


@router.get("/pairs", response_model=List[PairInfo])
async def get_pairs():
    """List all supported currency pairs with institutional specifications."""
    res = []
    for pair, cfg in PAIR_CONFIGS.items():
        base, quote = pair.split("/")
        res.append(PairInfo(
            symbol=pair,
            base_currency=base,
            quote_currency=quote,
            pip_size=cfg["pip_size"],
            typical_spread_pips=cfg["typical_spread"],
        ))
    return res


@router.get("/candles", response_model=List[CandleResponse])
async def get_candles(
    pair: str = Query("EUR/USD", description="Currency pair (e.g. EUR/USD)"),
    timeframe: str = Query("1H", description="Timeframe (1M, 5M, 15M, 30M, 1H, 4H, 1D)"),
    limit: int = Query(150, ge=10, le=1000, description="Number of candles"),
):
    """Retrieve historical OHLCV candles without look-ahead bias."""
    try:
        df = await provider.get_candles(pair, timeframe, limit=limit)
        candles = []
        for _, row in df.iterrows():
            candles.append(CandleResponse(
                timestamp=row["timestamp"].isoformat() if hasattr(row["timestamp"], "isoformat") else str(row["timestamp"]),
                open=float(row["open"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=float(row["close"]),
                volume=float(row["volume"]),
                is_complete=bool(row["is_complete"]),
            ))
        return candles
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/quote", response_model=QuoteResponse)
async def get_quote(pair: str = Query("EUR/USD")):
    """Get the latest real-time bid/ask quote with spread."""
    try:
        q = await provider.get_latest_quote(pair)
        return QuoteResponse(
            pair=q.pair,
            bid=q.bid,
            ask=q.ask,
            spread=q.spread,
            mid=round((q.bid + q.ask) / 2.0, 5),
            timestamp=q.timestamp.isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
