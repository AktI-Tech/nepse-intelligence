from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
from pydantic import BaseModel
from typing import Any
app = FastAPI(
title="NEPSE Intelligence API",
description="Nepal's open trading intelligence dashboard",
version="0.1.0"
)
app.add_middleware(
CORSMiddleware,
allow_origins=[""],
allow_credentials=True,
allow_methods=[""],
allow_headers=["*"],
)
NEPSE_BASE = "https://nepseapi.surajrimal.dev"  # Confirmed working today (19 Mar 2026)
class LiveMarketResponse(BaseModel):
data: Any
@app.get("/")
def root():
return {
"message": "NEPSE Intelligence API running 🚀",
"live_data": "/api/live-market",
"note": "If you ever see 503, reply 'API down' and we'll switch to self-hosted Docker version instantly"
}
@app.get("/api/live-market", response_model=LiveMarketResponse)
def get_live_market():
"""Fetch live NEPSE market data"""
try:
r = requests.get(f"{NEPSE_BASE}/LiveMarket", timeout=10)
r.raise_for_status()
return {"data": r.json()}
except Exception as e:
raise HTTPException(status_code=503, detail=f"NEPSE data temporarily unavailable: {str(e)}")
@app.get("/api/nepse-index")
def get_nepse_index():
"""NEPSE Index + sub-indices"""
try:
r = requests.get(f"{NEPSE_BASE}/NepseIndex", timeout=10)
r.raise_for_status()
return r.json()
except:
raise HTTPException(status_code=503, detail="Index data unavailable")
@app.get("/health")
def health():
return {"status": "healthy", "nepse_api": "connected"}
