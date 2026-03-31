import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
from pydantic import BaseModel
from typing import Any
from app.database import init_db
from app.scheduler import start_scheduler, stop_scheduler
from app.routes import router as market_router

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="NEPSE Intelligence API",
    description="Nepal's open trading intelligence dashboard",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include market data routes
app.include_router(market_router)

NEPSE_BASE = "https://nepseapi.surajrimal.dev"

class LiveMarketResponse(BaseModel):
    data: Any


@app.on_event("startup")
async def startup_event():
    """Initialize database and start scheduler on startup."""
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
    
    try:
        start_scheduler()
        logger.info("Scheduler started")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Stop scheduler on shutdown."""
    try:
        stop_scheduler()
        logger.info("Scheduler stopped")
    except Exception as e:
        logger.error(f"Failed to stop scheduler: {e}")


@app.get("/")
def root():
    return {
        "message": "NEPSE Intelligence API running 🚀",
        "docs": "/docs",
        "live_data": "/api/live-market",
        "database_endpoints": "/api/stocks, /api/indices, /api/market/summary",
    }


@app.get("/api/live-market", response_model=LiveMarketResponse)
def get_live_market():
    """Fetch live NEPSE market data from external API"""
    try:
        r = requests.get(f"{NEPSE_BASE}/LiveMarket", timeout=10)
        r.raise_for_status()
        return {"data": r.json()}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"NEPSE data temporarily unavailable: {str(e)}")


@app.get("/api/nepse-index")
def get_nepse_index():
    """NEPSE Index + sub-indices from external API"""
    try:
        r = requests.get(f"{NEPSE_BASE}/NepseIndex", timeout=10)
        r.raise_for_status()
        return r.json()
    except:
        raise HTTPException(status_code=503, detail="Index data unavailable")


@app.get("/health")
def health():
    return {"status": "healthy", "nepse_api": "connected"}
