"""Database query schemas and utilities."""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class StockResponse(BaseModel):
    symbol: str
    name: str
    sector: Optional[str] = None
    current_price: Optional[float] = None
    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    volume: Optional[int] = None
    market_cap: Optional[float] = None
    updated_at: datetime

    class Config:
        from_attributes = True


class IndexResponse(BaseModel):
    symbol: str
    name: str
    current_value: Optional[float] = None
    points_change: Optional[float] = None
    percent_change: Optional[float] = None
    updated_at: datetime

    class Config:
        from_attributes = True


class MarketDataPoint(BaseModel):
    price: float
    volume: Optional[int] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class TradingSignalResponse(BaseModel):
    symbol: str
    signal_type: str
    confidence: Optional[float] = None
    reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
