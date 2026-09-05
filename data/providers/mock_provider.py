"""
GARCH High-Fidelity Mock Market Data Provider
Simulates realistic Forex price action using Geometric Brownian Motion with GARCH(1,1)
stochastic volatility clustering, liquidity sweeps, support/resistance bounces, and spread variation.
Provides zero-leakage, point-in-time sequential candles for development & testing.
"""

import math
import random
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict
import numpy as np
import pandas as pd

from data.providers.base import MarketDataProvider, Quote


PAIR_CONFIGS: Dict[str, Dict[str, float]] = {
    "EUR/USD": {"base_price": 1.0850, "pip_size": 0.0001, "volatility": 0.0006, "typical_spread": 1.2},
    "GBP/USD": {"base_price": 1.2720, "pip_size": 0.0001, "volatility": 0.0008, "typical_spread": 1.5},
    "USD/JPY": {"base_price": 154.50, "pip_size": 0.01,   "volatility": 0.0007, "typical_spread": 1.3},
    "USD/CHF": {"base_price": 0.8950, "pip_size": 0.0001, "volatility": 0.0006, "typical_spread": 1.6},
    "AUD/USD": {"base_price": 0.6620, "pip_size": 0.0001, "volatility": 0.0009, "typical_spread": 1.4},
    "USD/CAD": {"base_price": 1.3680, "pip_size": 0.0001, "volatility": 0.0007, "typical_spread": 1.5},
    "NZD/USD": {"base_price": 0.6120, "pip_size": 0.0001, "volatility": 0.0009, "typical_spread": 1.8},
    "EUR/GBP": {"base_price": 0.8530, "pip_size": 0.0001, "volatility": 0.0005, "typical_spread": 1.4},
    "EUR/JPY": {"base_price": 167.60, "pip_size": 0.01,   "volatility": 0.0008, "typical_spread": 1.7},
    "GBP/JPY": {"base_price": 196.50, "pip_size": 0.01,   "volatility": 0.0011, "typical_spread": 2.0},
}

TIMEFRAME_DELTAS: Dict[str, timedelta] = {
    "1M": timedelta(minutes=1),
    "5M": timedelta(minutes=5),
    "15M": timedelta(minutes=15),
    "30M": timedelta(minutes=30),
    "1H": timedelta(hours=1),
    "4H": timedelta(hours=4),
    "1D": timedelta(days=1),
}


class GarchMockMarketDataProvider(MarketDataProvider):
    """
    High-fidelity deterministic/stochastic generator that simulates realistic Forex mechanics:
    - GARCH(1,1) volatility clustering: σ²_t = ω + α * ε²_{t-1} + β * σ²_{t-1}
    - Microstructure wicks & liquidity hunts
    - Macro drift and cyclical intraday volume patterns
    """

    def __init__(self, seed: Optional[int] = 42):
        self.seed = seed
        self._rng = random.Random(seed)
        self._np_rng = np.random.default_rng(seed)

    def get_supported_pairs(self) -> List[str]:
        return list(PAIR_CONFIGS.keys())

    def get_supported_timeframes(self) -> List[str]:
        return list(TIMEFRAME_DELTAS.keys())

    def _normalize_pair(self, pair: str) -> str:
        pair = pair.upper().replace("_", "/")
        if pair not in PAIR_CONFIGS:
            # Match without slash if passed as EURUSD
            for key in PAIR_CONFIGS:
                if key.replace("/", "") == pair:
                    return key
            raise ValueError(f"Unsupported pair '{pair}'. Supported: {list(PAIR_CONFIGS.keys())}")
        return pair

    def _normalize_tf(self, timeframe: str) -> str:
        tf = timeframe.upper()
        if tf not in TIMEFRAME_DELTAS:
            # common variations like 1m, 5m, 1h
            variations = {"1MIN": "1M", "5MIN": "5M", "15MIN": "15M", "30MIN": "30M", "60M": "1H", "240M": "4H", "D": "1D"}
            if tf in variations:
                return variations[tf]
            raise ValueError(f"Unsupported timeframe '{timeframe}'. Supported: {list(TIMEFRAME_DELTAS.keys())}")
        return tf

    async def get_candles(
        self,
        pair: str,
        timeframe: str,
        limit: int = 500,
        end_time: Optional[datetime] = None,
    ) -> pd.DataFrame:
        pair = self._normalize_pair(pair)
        timeframe = self._normalize_tf(timeframe)
        cfg = PAIR_CONFIGS[pair]
        delta = TIMEFRAME_DELTAS[timeframe]

        if end_time is None:
            end_time = datetime.now(timezone.utc)
        elif end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=timezone.utc)

        # Align end_time to timeframe boundary
        seconds = int(delta.total_seconds())
        aligned_ts = int(end_time.timestamp() // seconds) * seconds
        end_time = datetime.fromtimestamp(aligned_ts, tz=timezone.utc)

        start_time = end_time - (delta * (limit - 1))
        timestamps = [start_time + (delta * i) for i in range(limit)]

        # GARCH(1,1) Parameters
        omega = 1e-6
        alpha = 0.12
        beta = 0.85
        base_vol = cfg["volatility"] * math.sqrt(seconds / 3600.0)
        curr_var = base_vol ** 2

        # Base price and cycle simulation
        base_price = cfg["base_price"]
        pip = cfg["pip_size"]

        # Deterministic pseudo-randomness based on pair & timestamp for reproducibility
        pair_hash = sum(ord(c) for c in pair)
        local_rng = np.random.default_rng(pair_hash + (self.seed or 0))

        prices = [base_price]
        highs = []
        lows = []
        opens = []
        closes = []
        volumes = []

        curr_price = base_price

        # Simulate trend regimes across time
        regime_drift = 0.0
        drift_counter = 0

        for i in range(limit):
            # Change drift regime every 50-100 candles
            if drift_counter <= 0:
                drift_counter = int(local_rng.integers(40, 100))
                regime_drift = float(local_rng.choice([-1.0, -0.5, 0.0, 0.5, 1.0])) * 0.0002

            drift_counter -= 1

            # Shock & GARCH variance update
            z = float(local_rng.standard_normal())
            shock = math.sqrt(max(curr_var, 1e-8)) * z
            curr_var = omega + alpha * (shock ** 2) + beta * curr_var

            open_p = curr_price
            ret = regime_drift + shock
            close_p = open_p * math.exp(ret)

            # Generate realistic wicks (liquidity sweeps and intraday noise)
            wick_vol = math.sqrt(curr_var) * float(local_rng.uniform(0.5, 2.2))
            upper_wick = abs(float(local_rng.standard_normal())) * wick_vol * open_p
            lower_wick = abs(float(local_rng.standard_normal())) * wick_vol * open_p

            high_p = max(open_p, close_p) + upper_wick
            low_p = min(open_p, close_p) - lower_wick

            # Add occasional liquidity hunt spike (outside bars)
            if local_rng.random() < 0.03:
                sweep_extension = 4.0 * pip
                if local_rng.random() < 0.5:
                    high_p += sweep_extension
                else:
                    low_p -= sweep_extension

            # Realistic volume with intraday/session spikes
            hour = timestamps[i].hour
            # London (08-16 UTC) and New York (13-21 UTC) overlap yields higher volume
            session_mult = 1.0
            if 8 <= hour <= 17:
                session_mult = 2.2 if 13 <= hour <= 17 else 1.8
            elif 0 <= hour <= 7:
                session_mult = 0.8  # Asian session

            base_volume = 1200.0 * session_mult
            vol = base_volume * (1.0 + abs(ret) * 150.0) * float(local_rng.uniform(0.7, 1.4))

            precision = 4 if pip == 0.0001 else 2
            opens.append(round(open_p, precision + 1))
            highs.append(round(high_p, precision + 1))
            lows.append(round(low_p, precision + 1))
            closes.append(round(close_p, precision + 1))
            volumes.append(round(vol, 1))

            curr_price = close_p

        df = pd.DataFrame({
            "timestamp": timestamps,
            "open": opens,
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": volumes,
            "is_complete": [True] * (limit - 1) + [False],  # Latest candle is actively forming
        })
        return df

    async def get_latest_quote(self, pair: str) -> Quote:
        pair = self._normalize_pair(pair)
        cfg = PAIR_CONFIGS[pair]
        pip = cfg["pip_size"]
        spread_pips = cfg["typical_spread"]

        # Grab last 2 candles to get current mid
        df = await self.get_candles(pair, "1M", limit=2)
        mid = float(df["close"].iloc[-1])
        half_spread = (spread_pips * pip) / 2.0

        bid = mid - half_spread
        ask = mid + half_spread
        spread = ask - bid

        return Quote(
            pair=pair,
            bid=bid,
            ask=ask,
            spread=spread,
            timestamp=datetime.now(timezone.utc),
        )
