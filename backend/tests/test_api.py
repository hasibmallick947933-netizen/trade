"""
Comprehensive Backend Test Suite
Tests endpoints: Market Data, Technical Indicators, Market Structure, Predictions, Backtest, Chat.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app


@pytest.mark.asyncio
async def test_root():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "FOREX AI"
        assert data["status"] == "online"


@pytest.mark.asyncio
async def test_market_pairs():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/market/pairs")
        assert response.status_code == 200
        pairs = response.json()
        assert len(pairs) == 10
        symbols = [p["symbol"] for p in pairs]
        assert "EUR/USD" in symbols
        assert "GBP/USD" in symbols
        assert "USD/JPY" in symbols


@pytest.mark.asyncio
async def test_market_candles():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/market/candles?pair=EUR/USD&timeframe=1H&limit=30")
        assert response.status_code == 200
        candles = response.json()
        assert len(candles) == 30
        assert "open" in candles[0]
        assert "close" in candles[0]
        assert "volume" in candles[0]


@pytest.mark.asyncio
async def test_technical_analysis():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/analysis/technical?pair=EUR/USD&timeframe=1H")
        assert response.status_code == 200
        data = response.json()
        assert "ema_20" in data
        assert "rsi_14" in data
        assert "market_structure" in data
        assert "detected_patterns" in data


@pytest.mark.asyncio
async def test_multi_timeframe():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/analysis/multi-timeframe?pair=EUR/USD")
        assert response.status_code == 200
        data = response.json()
        assert "alignment" in data
        assert "timeframes" in data
        assert "1D" in data["timeframes"]
        assert "1H" in data["timeframes"]


@pytest.mark.asyncio
async def test_currency_heatmap():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/analysis/heatmap?timeframe=1H")
        assert response.status_code == 200
        data = response.json()
        assert "strengths" in data
        assert "USD" in data["strengths"]
        assert "EUR" in data["strengths"]
        assert "strongest" in data


@pytest.mark.asyncio
async def test_predictions():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/predictions/latest?pair=EUR/USD&timeframe=1H")
        assert response.status_code == 200
        data = response.json()
        assert "prob_buy" in data
        assert "prob_sell" in data
        assert "prob_hold" in data
        # Probabilities must sum to ~100%
        total_prob = data["prob_buy"] + data["prob_sell"] + data["prob_hold"]
        assert abs(total_prob - 100.0) < 0.2
        assert "confidence" in data
        assert "signal_state" in data
        assert "stop_loss" in data
        assert "take_profit_1" in data
        assert "factors_supporting" in data
        assert "factors_opposing" in data


@pytest.mark.asyncio
async def test_backtest_run():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "pair": "EUR/USD",
            "timeframe": "1H",
            "bars": 200,
            "initial_capital": 100000.0,
            "risk_per_trade_pct": 1.0,
            "spread_pips": 1.2,
            "slippage_pips": 0.5,
        }
        response = await client.post("/api/v1/backtest/run", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "win_rate_pct" in data
        assert "profit_factor" in data
        assert "sharpe_ratio" in data
        assert "equity_curve" in data


@pytest.mark.asyncio
async def test_ai_chat():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "query": "Why is EUR/USD bullish or bearish?",
            "pair": "EUR/USD",
            "timeframe": "1H",
        }
        response = await client.post("/api/v1/chat/query", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "EUR/USD" in data["response"]
        assert len(data["citations"]) > 0
