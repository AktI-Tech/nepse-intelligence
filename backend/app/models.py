"""SQLAlchemy ORM models for NEPSE Intelligence."""

from sqlalchemy import Column, Integer, String, Numeric, DateTime, BigInteger, ForeignKey, Index as SQLIndex
from sqlalchemy.sql import func
from datetime import datetime
from app.database import Base


class Index(Base):
    """NEPSE Index model (NSE, Banking, Hydro, etc.)"""
    __tablename__ = "indices"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    current_value = Column(Numeric(10, 2), nullable=True)
    points_change = Column(Numeric(10, 2), nullable=True)
    percent_change = Column(Numeric(5, 2), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Stock(Base):
    """Individual stock model."""
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    sector = Column(String(100), nullable=True)
    current_price = Column(Numeric(10, 2), nullable=True)
    open_price = Column(Numeric(10, 2), nullable=True)
    high_price = Column(Numeric(10, 2), nullable=True)
    low_price = Column(Numeric(10, 2), nullable=True)
    volume = Column(BigInteger, nullable=True)
    market_cap = Column(Numeric(15, 2), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MarketData(Base):
    """Historical market data snapshots."""
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), ForeignKey("stocks.symbol", ondelete="CASCADE"), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    volume = Column(BigInteger, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        SQLIndex("idx_market_data_symbol", "symbol"),
        SQLIndex("idx_market_data_timestamp", "timestamp"),
    )


class IndexHistory(Base):
    """Historical index data."""
    __tablename__ = "index_history"

    id = Column(Integer, primary_key=True, index=True)
    index_id = Column(Integer, ForeignKey("indices.id", ondelete="CASCADE"), nullable=False)
    value = Column(Numeric(10, 2), nullable=False)
    points_change = Column(Numeric(10, 2), nullable=True)
    percent_change = Column(Numeric(5, 2), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        SQLIndex("idx_index_history_timestamp", "timestamp"),
    )


class TradingSignal(Base):
    """Trading signals and alerts from ML models."""
    __tablename__ = "trading_signals"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), ForeignKey("stocks.symbol", ondelete="CASCADE"), nullable=False)
    signal_type = Column(String(50), nullable=False)  # 'buy', 'sell', 'hold', 'alert'
    confidence = Column(Numeric(3, 2), nullable=True)
    reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        SQLIndex("idx_trading_signals_symbol", "symbol"),
    )
