"""
Market Data Provider Interface
Standardizes ingestion across mock generators and live data providers (TwelveData, OANDA, AlphaVantage, Finnhub).
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import pandas as pd


@dataclass
class Candle:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    is_complete: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else str(self.timestamp),
            "open": round(self.open, 5),
            "high": round(self.high, 5),
            "low": round(self.low, 5),
            "close": round(self.close, 5),
            "volume": round(self.volume, 2),
            "is_complete": self.is_complete,
        }


@dataclass
class Quote:
    pair: str
    bid: float
    ask: float
    spread: float
    timestamp: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pair": self.pair,
            "bid": round(self.bid, 5),
            "ask": round(self.ask, 5),
            "spread": round(self.spread, 5),
            "mid": round((self.bid + self.ask) / 2.0, 5),
            "timestamp": self.timestamp.isoformat(),
        }


class MarketDataProvider(ABC):
    """
    Abstract interface for all Forex market data providers.
    All implementations must return clean data without look-ahead bias.
    """

    @abstractmethod
    async def get_candles(
        self,
        pair: str,
        timeframe: str,
        limit: int = 500,
        end_time: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """
        Fetch OHLCV candles as a pandas DataFrame.
        Columns required: ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        Chronologically ordered: oldest first, newest last.
        """
        pass

    @abstractmethod
    async def get_latest_quote(self, pair: str) -> Quote:
        """Fetch the latest bid/ask tick for a pair."""
        pass

    @abstractmethod
    def get_supported_pairs(self) -> List[str]:
        """Return list of supported currency pairs."""
        pass

    @abstractmethod
    def get_supported_timeframes(self) -> List[str]:
        """Return list of supported timeframes."""
        pass
