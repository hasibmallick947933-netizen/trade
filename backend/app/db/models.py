"""
SQLAlchemy ORM Models for Forex AI Platform
Implements all 15 core schemas with appropriate indexes and foreign keys.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime,
    ForeignKey, Text, JSON, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship
from backend.app.db.session import Base


def utcnow():
    return datetime.now(timezone.utc)


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), default="USER", nullable=False)  # USER, ANALYST, ADMIN
    account_balance = Column(Float, default=100000.0, nullable=False)  # Default demo 100k
    risk_per_trade_pct = Column(Float, default=1.0, nullable=False)    # Default 1%
    max_daily_loss_pct = Column(Float, default=3.0, nullable=False)    # Default 3%
    created_at = Column(DateTime, default=utcnow, nullable=False)

    backtests = relationship("Backtest", back_populates="user", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="user", cascade="all, delete-orphan")


class CurrencyPair(Base):
    __tablename__ = "currency_pairs"

    symbol = Column(String(20), primary_key=True)  # e.g., "EUR/USD"
    base_currency = Column(String(10), nullable=False)   # e.g., "EUR"
    quote_currency = Column(String(10), nullable=False)  # e.g., "USD"
    pip_size = Column(Float, nullable=False, default=0.0001)
    typical_spread_pips = Column(Float, nullable=False, default=1.2)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)


class MarketCandle(Base):
    __tablename__ = "market_candles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pair_symbol = Column(String(20), ForeignKey("currency_pairs.symbol"), index=True, nullable=False)
    timeframe = Column(String(10), index=True, nullable=False)  # 1M, 5M, 15M, 30M, 1H, 4H, 1D
    timestamp = Column(DateTime, index=True, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    is_complete = Column(Boolean, default=True, nullable=False)

    __table_args__ = (
        UniqueConstraint("pair_symbol", "timeframe", "timestamp", name="uq_pair_tf_timestamp"),
        Index("idx_candles_pair_tf_ts", "pair_symbol", "timeframe", "timestamp"),
    )


class TechnicalFeature(Base):
    __tablename__ = "technical_features"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pair_symbol = Column(String(20), ForeignKey("currency_pairs.symbol"), index=True, nullable=False)
    timeframe = Column(String(10), index=True, nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)
    
    # Moving averages
    sma_20 = Column(Float, nullable=True)
    ema_20 = Column(Float, nullable=True)
    ema_50 = Column(Float, nullable=True)
    ema_200 = Column(Float, nullable=True)
    
    # Momentum & Volatility
    rsi_14 = Column(Float, nullable=True)
    macd = Column(Float, nullable=True)
    macd_signal = Column(Float, nullable=True)
    macd_hist = Column(Float, nullable=True)
    atr_14 = Column(Float, nullable=True)
    adx_14 = Column(Float, nullable=True)
    bb_upper = Column(Float, nullable=True)
    bb_lower = Column(Float, nullable=True)
    stoch_k = Column(Float, nullable=True)
    stoch_d = Column(Float, nullable=True)
    
    # Market Structure & Patterns
    market_structure = Column(String(50), nullable=True)  # BULLISH_TREND, BEARISH_TREND, RANGE
    bos_detected = Column(Boolean, default=False)         # Break of Structure
    choch_detected = Column(Boolean, default=False)       # Change of Character
    liquidity_sweep = Column(Boolean, default=False)      # Liquidity sweep detected
    detected_patterns = Column(JSON, nullable=True)       # Array of candlestick patterns detected

    __table_args__ = (
        UniqueConstraint("pair_symbol", "timeframe", "timestamp", name="uq_features_pair_tf_ts"),
    )


class EconomicEvent(Base):
    __tablename__ = "economic_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    currency = Column(String(10), index=True, nullable=False)  # USD, EUR, GBP, JPY
    country = Column(String(50), nullable=False)
    event_name = Column(String(255), nullable=False)           # CPI, Non-Farm Payrolls, Rate Decision
    timestamp = Column(DateTime, index=True, nullable=False)
    impact = Column(String(20), default="MEDIUM")              # LOW, MEDIUM, HIGH
    actual = Column(Float, nullable=True)
    forecast = Column(Float, nullable=True)
    previous = Column(Float, nullable=True)
    surprise = Column(Float, nullable=True)                    # actual - forecast
    bias_implication = Column(String(50), nullable=True)       # BULLISH_USD, BEARISH_USD, NEUTRAL


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, autoincrement=True)
    headline = Column(Text, nullable=False)
    source = Column(String(100), nullable=False)
    published_at = Column(DateTime, index=True, nullable=False)
    url = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)

    sentiments = relationship("NewsSentiment", back_populates="news", cascade="all, delete-orphan")


class NewsSentiment(Base):
    __tablename__ = "news_sentiment"

    id = Column(Integer, primary_key=True, autoincrement=True)
    news_id = Column(Integer, ForeignKey("news.id"), nullable=False)
    currency = Column(String(10), index=True, nullable=False)
    sentiment_label = Column(String(20), nullable=False)  # BULLISH, BEARISH, NEUTRAL
    sentiment_score = Column(Float, nullable=False)       # -1.0 to +1.0
    expected_impact = Column(String(20), default="MEDIUM")# LOW, MEDIUM, HIGH
    confidence = Column(Float, nullable=False)            # 0.0 to 1.0

    news = relationship("News", back_populates="sentiments")


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)             # e.g., "Forex-Ensemble-Alpha"
    model_type = Column(String(50), nullable=False)        # XGBOOST, LSTM, ENSEMBLE
    version = Column(String(50), nullable=False)           # e.g., "1.2.0"
    hyperparameters = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    trained_at = Column(DateTime, default=utcnow)

    predictions = relationship("Prediction", back_populates="model_version")
    metrics = relationship("ModelMetric", back_populates="model_version")


class ModelMetric(Base):
    __tablename__ = "model_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_version_id = Column(String, ForeignKey("model_versions.id"), nullable=False)
    evaluation_date = Column(DateTime, default=utcnow, index=True)
    brier_score = Column(Float, nullable=False)
    accuracy = Column(Float, nullable=False)
    auc_roc = Column(Float, nullable=True)
    log_loss = Column(Float, nullable=True)
    sharpe_ratio = Column(Float, nullable=True)
    data_drift_score = Column(Float, default=0.0)

    model_version = relationship("ModelVersion", back_populates="metrics")


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(String, primary_key=True, default=generate_uuid)
    pair_symbol = Column(String(20), ForeignKey("currency_pairs.symbol"), index=True, nullable=False)
    timeframe = Column(String(10), nullable=False)
    model_version_id = Column(String, ForeignKey("model_versions.id"), nullable=True)
    timestamp = Column(DateTime, default=utcnow, index=True, nullable=False)
    
    # Probabilities (strictly calibrated, sum to 100%)
    prob_buy = Column(Float, nullable=False)
    prob_sell = Column(Float, nullable=False)
    prob_hold = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    
    # Market Context
    market_regime = Column(String(100), nullable=False)   # Bullish trend / Medium volatility
    trend_direction = Column(String(50), nullable=False)  # BULLISH, BEARISH, NEUTRAL
    expected_price_range_low = Column(Float, nullable=False)
    expected_price_range_high = Column(Float, nullable=False)
    expected_return_pct = Column(Float, nullable=False)
    expected_volatility_pct = Column(Float, nullable=False)

    # Explainability & Audit
    factors_supporting = Column(JSON, nullable=False)      # List of supporting strings
    factors_opposing = Column(JSON, nullable=False)        # List of opposing strings
    explanation_summary = Column(Text, nullable=False)
    feature_snapshot = Column(JSON, nullable=True)
    
    # Outcome tracking for Real Walk-Forward Accuracy
    actual_outcome_price = Column(Float, nullable=True)
    actual_return_pct = Column(Float, nullable=True)
    evaluated_at = Column(DateTime, nullable=True)

    model_version = relationship("ModelVersion", back_populates="predictions")
    signal = relationship("Signal", uselist=False, back_populates="prediction")


class Signal(Base):
    __tablename__ = "signals"

    id = Column(String, primary_key=True, default=generate_uuid)
    prediction_id = Column(String, ForeignKey("predictions.id"), unique=True, nullable=False)
    pair_symbol = Column(String(20), ForeignKey("currency_pairs.symbol"), index=True, nullable=False)
    timeframe = Column(String(10), nullable=False)
    signal_state = Column(String(30), nullable=False)     # STRONG BUY, BUY, WEAK BUY, HOLD, WEAK SELL, SELL, STRONG SELL
    
    # Actionable Zones
    entry_zone_min = Column(Float, nullable=False)
    entry_zone_max = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)
    take_profit_1 = Column(Float, nullable=False)
    take_profit_2 = Column(Float, nullable=False)
    risk_reward_ratio = Column(Float, nullable=False)
    suggested_position_size = Column(Float, nullable=True)
    created_at = Column(DateTime, default=utcnow, index=True, nullable=False)

    prediction = relationship("Prediction", back_populates="signal")


class Backtest(Base):
    __tablename__ = "backtests"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    pair_symbol = Column(String(20), nullable=False)
    timeframe = Column(String(10), nullable=False)
    strategy_name = Column(String(100), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    
    # Parameters
    initial_capital = Column(Float, default=100000.0, nullable=False)
    risk_per_trade_pct = Column(Float, default=1.0, nullable=False)
    spread_pips = Column(Float, default=1.2, nullable=False)
    slippage_pips = Column(Float, default=0.5, nullable=False)
    
    # Performance Statistics
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    win_rate_pct = Column(Float, default=0.0)
    profit_factor = Column(Float, default=0.0)
    net_profit = Column(Float, default=0.0)
    cagr_pct = Column(Float, default=0.0)
    max_drawdown_pct = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, default=0.0)
    sortino_ratio = Column(Float, default=0.0)
    expectancy = Column(Float, default=0.0)
    
    # Series
    equity_curve = Column(JSON, nullable=True)     # [{timestamp, equity, drawdown}]
    created_at = Column(DateTime, default=utcnow, nullable=False)

    user = relationship("User", back_populates="backtests")
    trades = relationship("Trade", back_populates="backtest", cascade="all, delete-orphan")


class Trade(Base):
    __tablename__ = "trades"

    id = Column(String, primary_key=True, default=generate_uuid)
    backtest_id = Column(String, ForeignKey("backtests.id"), nullable=True)
    pair_symbol = Column(String(20), nullable=False)
    direction = Column(String(10), nullable=False)  # BUY or SELL
    entry_time = Column(DateTime, nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_time = Column(DateTime, nullable=False)
    exit_price = Column(Float, nullable=False)
    lot_size = Column(Float, nullable=False)
    spread_cost = Column(Float, default=0.0)
    slippage_cost = Column(Float, default=0.0)
    pnl = Column(Float, nullable=False)
    return_pct = Column(Float, nullable=False)
    exit_reason = Column(String(50), nullable=False) # TP1, TP2, SL, TIME_EXIT

    backtest = relationship("Backtest", back_populates="trades")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    pair_symbol = Column(String(20), nullable=False)
    timeframe = Column(String(10), nullable=False)
    condition_type = Column(String(50), nullable=False) # BUY_PROB_GT, SELL_PROB_GT, BREAKOUT, NEWS_HIGH
    threshold_value = Column(Float, nullable=True)
    status = Column(String(20), default="ACTIVE")       # ACTIVE, TRIGGERED, DISABLED
    triggered_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    user = relationship("User", back_populates="alerts")


class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    service = Column(String(100), nullable=False)
    level = Column(String(20), default="INFO")
    message = Column(Text, nullable=False)
    context = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=utcnow, index=True)
