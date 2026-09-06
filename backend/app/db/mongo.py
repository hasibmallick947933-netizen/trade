"""
MongoDB Async Connection and Schema Management
Uses Motor (official async MongoDB driver) with MongoDB Atlas (mongodb+srv://) support.
"""

import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import IndexModel, ASCENDING, DESCENDING
from backend.app.core.config import settings

logger = logging.getLogger("forex_ai.db.mongo")

# Global client and DB references
mongo_client: Optional[AsyncIOMotorClient] = None
mongo_db: Optional[AsyncIOMotorDatabase] = None


class MongoCollections:
    USERS = "users"
    CURRENCY_PAIRS = "currency_pairs"
    MARKET_CANDLES = "market_candles"
    TECHNICAL_FEATURES = "technical_features"
    ECONOMIC_EVENTS = "economic_events"
    NEWS = "news"
    NEWS_SENTIMENT = "news_sentiment"
    PREDICTIONS = "predictions"
    SIGNALS = "signals"
    BACKTESTS = "backtests"
    TRADES = "trades"
    MODEL_VERSIONS = "model_versions"
    MODEL_METRICS = "model_metrics"
    ALERTS = "alerts"
    SYSTEM_LOGS = "system_logs"


async def get_mongo_db() -> Optional[AsyncIOMotorDatabase]:
    """Dependency / accessor for the active MongoDB database."""
    global mongo_db
    return mongo_db


async def init_mongo():
    """
    Initializes the async MongoDB client, verifies connection,
    and creates required indexes for all Forex AI collections.
    """
    global mongo_client, mongo_db

    mongo_uri = getattr(settings, "MONGODB_URI", "mongodb://localhost:27017")
    db_name = getattr(settings, "MONGODB_DB_NAME", "forex_ai")

    try:
        mongo_client = AsyncIOMotorClient(
            mongo_uri,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
        )
        mongo_db = mongo_client[db_name]

        # Verify ping
        await mongo_client.admin.command("ping")
        logger.info(f"Connected successfully to MongoDB: {db_name}")

        # Create indexes
        await _create_indexes(mongo_db)

    except Exception as e:
        logger.warning(
            f"MongoDB connection notice ({e}). Operating in memory/cached mode if MongoDB is not running locally. "
            "To connect to MongoDB Atlas, set MONGODB_URI in your environment."
        )


async def _create_indexes(db: AsyncIOMotorDatabase):
    """Ensure optimized compound indexes for fast timeseries queries and uniqueness."""
    try:
        # Candles: unique compound index on pair + timeframe + timestamp
        await db[MongoCollections.MARKET_CANDLES].create_indexes([
            IndexModel(
                [("pair_symbol", ASCENDING), ("timeframe", ASCENDING), ("timestamp", ASCENDING)],
                unique=True,
                name="uq_candle_pair_tf_ts"
            )
        ])

        # Predictions: query by pair and recent timestamp
        await db[MongoCollections.PREDICTIONS].create_indexes([
            IndexModel([("pair_symbol", ASCENDING), ("timestamp", DESCENDING)], name="idx_pred_pair_ts")
        ])

        # Signals: query by pair and creation date
        await db[MongoCollections.SIGNALS].create_indexes([
            IndexModel([("pair_symbol", ASCENDING), ("created_at", DESCENDING)], name="idx_sig_pair_date")
        ])

        # Economic Events: query by currency and timestamp
        await db[MongoCollections.ECONOMIC_EVENTS].create_indexes([
            IndexModel([("currency", ASCENDING), ("timestamp", DESCENDING)], name="idx_econ_curr_ts")
        ])

        # Users: unique index on email
        await db[MongoCollections.USERS].create_indexes([
            IndexModel([("email", ASCENDING)], unique=True, name="uq_user_email")
        ])

        logger.info("MongoDB indexes verified successfully.")
    except Exception as e:
        logger.error(f"Error creating MongoDB indexes: {e}")


async def close_mongo():
    """Close MongoDB connection gracefully on application shutdown."""
    global mongo_client
    if mongo_client:
        mongo_client.close()
        logger.info("MongoDB connection closed.")
