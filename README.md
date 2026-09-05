# FOREX AI — Institutional Quantitative Market Analysis Platform

A production-quality, AI-powered Forex quantitative analysis, calibrated probabilistic prediction, and walk-forward backtesting platform.

---

## Key Capabilities

1. **Probabilistic Prediction Engine**:
   - Calculates calibrated $P(\text{BUY})$, $P(\text{SELL})$, and $P(\text{HOLD})$ probabilities that sum to 100%.
   - Computes an entropy-based **Confidence Score** (50%–95%).
   - Dynamic **Market Regime Detection** (e.g., *Strong Trend / High Volatility*, *Range / Low Volatility*).
   - Multi-horizon forecasts for 15M, 30M, 1H, 4H, and 1D.

2. **Technical Analysis & Institutional Market Structure Engine**:
   - Computes standard quantitative indicators (SMA, EMA, RSI, MACD, Bollinger Bands, ATR, ADX, Stochastic, CCI, Williams %R, OBV, VWAP).
   - Detects 19 classic candlestick patterns with historical effectiveness weights:
     - Doji, Dragonfly Doji, Gravestone Doji, Hammer, Inverted Hammer, Hanging Man, Shooting Star, Bullish/Bearish Engulfing, Piercing Line, Dark Cloud Cover, Morning/Evening Star, Three White Soldiers, Three Black Crows, Tweezer Top/Bottom, Harami, Inside Bar, Outside Bar.
   - Institutional price action:
     - Fractal Swing Highs & Lows
     - Break of Structure (BOS) & Change of Character (CHOCH)
     - Liquidity Sweeps (stop runs)
     - Supply & Demand Order Blocks
     - Dynamic Support & Resistance levels

3. **Multi-Timeframe Confluence Matrix**:
   - Simultaneous analysis across **1D, 4H, 1H, 15M, and 5M**.
   - Determines higher-timeframe trend, medium-timeframe setup, and lower-timeframe entry trigger.
   - Calculates alignment score (-1.0 to +1.0) and status (*STRONG BULLISH*, *MODERATE BULLISH*, *MIXED*, *MODERATE BEARISH*, *STRONG BEARISH*).

4. **Macroeconomic, Yield & Cross-Asset Engine**:
   - Economic Calendar with surprises ($\text{Actual} - \text{Forecast}$) for CPI, NFP, GDP, Interest Rate Decisions.
   - Relative currency fundamental scoring and pair bias.
   - US Treasury yields (2Y, 10Y), yield curve slope, DXY index, and rolling cross-asset correlations (Gold, Oil).

5. **Currency Strength Heatmap**:
   - Real-time relative strength index across 8 major currencies: **USD, EUR, GBP, JPY, AUD, CAD, CHF, NZD**.
   - Automatic identification of the strongest vs. weakest currencies to select optimal divergence pairs.

6. **Risk Management & Position Sizing**:
   - Dynamic ATR-based Stop Loss and multi-target Take Profits (TP1, TP2).
   - Risk/Reward ratio calculation.
   - Position sizing recommendation based on account balance and risk-per-trade percentage (e.g., 1% risk).

7. **Walk-Forward Backtesting Studio**:
   - Point-in-time chronological simulation (no look-ahead bias, no data leakage).
   - Realistic friction modeling: configurable bid-ask spread and slippage.
   - Institutional performance statistics: Total trades, Win rate %, Profit factor, Net profit, CAGR %, Max drawdown %, Sharpe ratio, Sortino ratio, Expectancy, and interactive SVG Equity Curve.

8. **Grounded Conversational AI Analyst**:
   - Natural language assistant strictly grounded on live quantitative metrics, market structure, and macro surprises, avoiding market hallucinations.

---

## Technology Stack

- **Frontend**: Next.js 14 (App Router), React 18, TypeScript, Tailwind CSS, Lucide Icons, Canvas Candlestick Chart.
- **Backend**: Python 3.11, FastAPI, Pydantic v2, SQLAlchemy 2.0 Async, aiosqlite / asyncpg, Uvicorn.
- **Quantitative & ML**: NumPy, pandas, scikit-learn, scipy.
- **Architecture**: Modular monorepo with provider-independent interfaces (`MarketDataProvider`).

---

## Quick Start Guide

### 1. Start Both Services
Run the startup script from the root directory:
```bash
./start.sh
```

Or start them individually:

#### Backend:
```bash
source .venv/bin/activate
export PYTHONPATH=.
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
- API Base URL: `http://localhost:8000`
- Interactive OpenAPI Docs: `http://localhost:8000/docs`

#### Frontend:
```bash
cd frontend
npm run dev
```
- Frontend URL: `http://localhost:3000`

---

## Running Automated Tests

Execute the backend test suite:
```bash
source .venv/bin/activate
PYTHONPATH=. pytest backend/tests/test_api.py -v -o asyncio_mode=auto
```
All 9 test cases will run and validate the REST endpoints, mathematical models, backtest engine, and chat assistant.
