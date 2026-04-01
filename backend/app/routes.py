"""Database-backed API endpoints for market data."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime, timedelta
from app.database import get_db
from app.models import Stock, Index, MarketData, IndexHistory, TradingSignal
from app.schemas import StockResponse, IndexResponse, MarketDataPoint, TradingSignalResponse
from app.pipeline import get_pipeline

router = APIRouter(prefix="/api", tags=["market"])


@router.get("/stocks", response_model=list[StockResponse])
def get_all_stocks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all stocks from database."""
    stocks = db.query(Stock).offset(skip).limit(limit).all()
    return stocks


@router.get("/stocks/{symbol}", response_model=StockResponse)
def get_stock(symbol: str, db: Session = Depends(get_db)):
    """Get a specific stock by symbol."""
    stock = db.query(Stock).filter(Stock.symbol == symbol).first()
    if not stock:
        raise HTTPException(status_code=404, detail=f"Stock {symbol} not found")
    return stock


@router.get("/stocks/{symbol}/history", response_model=list[MarketDataPoint])
def get_stock_history(
    symbol: str,
    limit: int = Query(100, ge=1, le=1000),
    hours: int = Query(24, ge=1, le=720),
    db: Session = Depends(get_db)
):
    """Get historical market data for a stock."""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    data = db.query(MarketData).filter(
        MarketData.symbol == symbol,
        MarketData.timestamp >= cutoff_time
    ).order_by(desc(MarketData.timestamp)).limit(limit).all()
    
    return list(reversed(data))


@router.get("/indices", response_model=list[IndexResponse])
def get_all_indices(db: Session = Depends(get_db)):
    """Get all indices (NSE, Banking, Hydro, etc.)."""
    indices = db.query(Index).all()
    return indices


@router.get("/indices/{symbol}", response_model=IndexResponse)
def get_index(symbol: str, db: Session = Depends(get_db)):
    """Get a specific index by symbol."""
    index = db.query(Index).filter(Index.symbol == symbol).first()
    if not index:
        raise HTTPException(status_code=404, detail=f"Index {symbol} not found")
    return index


@router.get("/indices/{symbol}/history", response_model=list[MarketDataPoint])
def get_index_history(
    symbol: str,
    limit: int = Query(100, ge=1, le=1000),
    hours: int = Query(24, ge=1, le=720),
    db: Session = Depends(get_db)
):
    """Get historical index data."""
    index = db.query(Index).filter(Index.symbol == symbol).first()
    if not index:
        raise HTTPException(status_code=404, detail=f"Index {symbol} not found")
    
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    data = db.query(IndexHistory).filter(
        IndexHistory.index_id == index.id,
        IndexHistory.timestamp >= cutoff_time
    ).order_by(desc(IndexHistory.timestamp)).limit(limit).all()
    
    return list(reversed(data))


@router.get("/market/top-gainers", response_model=list[StockResponse])
def get_top_gainers(limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    """Get top gaining stocks."""
    stocks = db.query(Stock).order_by(Stock.market_cap.desc()).limit(limit).all()
    return stocks


@router.get("/market/top-losers", response_model=list[StockResponse])
def get_top_losers(limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    """Get top losing stocks."""
    stocks = db.query(Stock).order_by(Stock.market_cap.asc()).limit(limit).all()
    return stocks


@router.get("/signals", response_model=list[TradingSignalResponse])
def get_trading_signals(
    symbol: str = Query(None),
    signal_type: str = Query(None),
    db: Session = Depends(get_db)
):
    """Get trading signals, optionally filtered by symbol or type."""
    query = db.query(TradingSignal)
    if symbol:
        query = query.filter(TradingSignal.symbol == symbol)
    if signal_type:
        query = query.filter(TradingSignal.signal_type == signal_type)
    
    return query.order_by(desc(TradingSignal.created_at)).all()


@router.get("/market/summary")
def get_market_summary(db: Session = Depends(get_db)):
    """Get market summary (total stocks, indices, latest update)."""
    stock_count = db.query(func.count(Stock.id)).scalar()
    index_count = db.query(func.count(Index.id)).scalar()
    
    latest_stock = db.query(Stock).order_by(desc(Stock.updated_at)).first()
    latest_index = db.query(Index).order_by(desc(Index.updated_at)).first()
    
    return {
        "total_stocks": stock_count,
        "total_indices": index_count,
        "last_stock_update": latest_stock.updated_at if latest_stock else None,
        "last_index_update": latest_index.updated_at if latest_index else None,
    }


@router.get("/pipeline-health")
def get_pipeline_health():
    """Get NEPSE API pipeline health status."""
    pipeline = get_pipeline()
    health = pipeline.get_api_health()
    
    # Add cache availability info
    db = next(get_db())
    try:
        stock_count = db.query(func.count(Stock.id)).scalar()
        index_count = db.query(func.count(Index.id)).scalar()
        
        health["cache_available"] = stock_count > 0 or index_count > 0
        health["cached_stocks"] = stock_count
        health["cached_indices"] = index_count
    finally:
        db.close()
    
    return health
