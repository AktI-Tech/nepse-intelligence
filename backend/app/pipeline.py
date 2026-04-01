"""NEPSE data pipeline: fetch live data and store in PostgreSQL."""

import requests
import logging
import time
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models import Index, Stock, MarketData, IndexHistory
from app.database import SessionLocal

logger = logging.getLogger(__name__)

NEPSE_API = "https://nepseapi.surajrimal.dev"
TIMEOUT = 10
MAX_RETRIES = 3
INITIAL_BACKOFF = 2  # seconds
MAX_BACKOFF = 30  # seconds


class NEPSEPipeline:
    """Fetch live NEPSE data and persist to database with retry logic."""

    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()
        self.api = NEPSE_API
        self.last_successful_fetch = None
        self.api_status = "unknown"
        self.last_error = None

    def _exponential_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff duration."""
        backoff = INITIAL_BACKOFF * (2 ** attempt)
        return min(backoff, MAX_BACKOFF)

    def fetch_live_market(self, retry: bool = True) -> dict:
        """Fetch live market data from NEPSE API with retry logic."""
        attempt = 0
        last_exception = None

        while attempt < MAX_RETRIES:
            try:
                r = requests.get(f"{self.api}/LiveMarket", timeout=TIMEOUT)
                r.raise_for_status()
                
                self.api_status = "healthy"
                self.last_error = None
                data = r.json()
                self.last_successful_fetch = datetime.utcnow()
                logger.info("Successfully fetched live market data")
                return data

            except requests.exceptions.Timeout:
                last_exception = "API timeout"
                attempt += 1
                if attempt < MAX_RETRIES and retry:
                    backoff = self._exponential_backoff(attempt - 1)
                    logger.warning(f"Timeout fetching live market (attempt {attempt}/{MAX_RETRIES}), retrying in {backoff}s...")
                    time.sleep(backoff)
                else:
                    break

            except requests.exceptions.ConnectionError:
                last_exception = "Connection error"
                attempt += 1
                if attempt < MAX_RETRIES and retry:
                    backoff = self._exponential_backoff(attempt - 1)
                    logger.warning(f"Connection error fetching live market (attempt {attempt}/{MAX_RETRIES}), retrying in {backoff}s...")
                    time.sleep(backoff)
                else:
                    break

            except requests.exceptions.HTTPError as e:
                last_exception = f"HTTP {e.response.status_code}"
                if e.response.status_code in [500, 502, 503, 504, 521]:
                    self.api_status = "unavailable"
                    attempt += 1
                    if attempt < MAX_RETRIES and retry:
                        backoff = self._exponential_backoff(attempt - 1)
                        logger.warning(f"API error {e.response.status_code} (attempt {attempt}/{MAX_RETRIES}), retrying in {backoff}s...")
                        time.sleep(backoff)
                    else:
                        break
                else:
                    logger.error(f"HTTP error fetching live market: {e}")
                    self.api_status = "error"
                    break

            except Exception as e:
                last_exception = str(e)
                logger.error(f"Unexpected error fetching live market: {e}")
                self.api_status = "error"
                break

        self.last_error = last_exception
        self.api_status = "unavailable"
        logger.error(f"Failed to fetch live market after {MAX_RETRIES} attempts: {last_exception}")
        return None

    def fetch_nepse_index(self, retry: bool = True) -> dict:
        """Fetch NEPSE index data with retry logic."""
        attempt = 0
        last_exception = None

        while attempt < MAX_RETRIES:
            try:
                r = requests.get(f"{self.api}/NepseIndex", timeout=TIMEOUT)
                r.raise_for_status()
                
                data = r.json()
                logger.info("Successfully fetched NEPSE index data")
                return data

            except requests.exceptions.Timeout:
                last_exception = "API timeout"
                attempt += 1
                if attempt < MAX_RETRIES and retry:
                    backoff = self._exponential_backoff(attempt - 1)
                    logger.warning(f"Timeout fetching index (attempt {attempt}/{MAX_RETRIES}), retrying in {backoff}s...")
                    time.sleep(backoff)
                else:
                    break

            except requests.exceptions.ConnectionError:
                last_exception = "Connection error"
                attempt += 1
                if attempt < MAX_RETRIES and retry:
                    backoff = self._exponential_backoff(attempt - 1)
                    logger.warning(f"Connection error fetching index (attempt {attempt}/{MAX_RETRIES}), retrying in {backoff}s...")
                    time.sleep(backoff)
                else:
                    break

            except requests.exceptions.HTTPError as e:
                last_exception = f"HTTP {e.response.status_code}"
                if e.response.status_code in [500, 502, 503, 504, 521]:
                    attempt += 1
                    if attempt < MAX_RETRIES and retry:
                        backoff = self._exponential_backoff(attempt - 1)
                        logger.warning(f"API error {e.response.status_code} (attempt {attempt}/{MAX_RETRIES}), retrying in {backoff}s...")
                        time.sleep(backoff)
                    else:
                        break
                else:
                    logger.error(f"HTTP error fetching index: {e}")
                    break

            except Exception as e:
                last_exception = str(e)
                logger.error(f"Unexpected error fetching index: {e}")
                break

        logger.error(f"Failed to fetch index after {MAX_RETRIES} attempts: {last_exception}")
        return None

    def store_stocks(self, market_data: dict) -> int:
        """Store stock data from live market response."""
        if not market_data or "data" not in market_data:
            return 0

        count = 0
        for stock_info in market_data.get("data", []):
            try:
                symbol = stock_info.get("symbol")
                if not symbol:
                    continue

                # Update or create stock record
                stock = self.db.query(Stock).filter(Stock.symbol == symbol).first()
                if not stock:
                    stock = Stock(symbol=symbol)
                    self.db.add(stock)

                stock.name = stock_info.get("companyName", symbol)
                stock.current_price = stock_info.get("ltp")
                stock.open_price = stock_info.get("open")
                stock.high_price = stock_info.get("high")
                stock.low_price = stock_info.get("low")
                stock.volume = stock_info.get("volume")
                stock.updated_at = datetime.utcnow()

                # Store market data snapshot
                market_snapshot = MarketData(
                    symbol=symbol,
                    price=stock_info.get("ltp"),
                    volume=stock_info.get("volume")
                )
                self.db.add(market_snapshot)
                count += 1

            except Exception as e:
                logger.warning(f"Failed to store stock {symbol}: {e}")
                continue

        self.db.commit()
        logger.info(f"Stored {count} stock records")
        return count

    def store_indices(self, index_data: dict) -> int:
        """Store index data (NSE, Banking, Hydro, etc.)."""
        if not index_data:
            return 0

        count = 0
        indices_list = index_data.get("data", [])

        for idx_info in indices_list:
            try:
                symbol = idx_info.get("index")
                if not symbol:
                    continue

                # Update or create index record
                index = self.db.query(Index).filter(Index.symbol == symbol).first()
                if not index:
                    index = Index(symbol=symbol)
                    self.db.add(index)

                index.name = idx_info.get("name", symbol)
                index.current_value = idx_info.get("value")
                index.points_change = idx_info.get("pointChange")
                index.percent_change = idx_info.get("percentChange")
                index.updated_at = datetime.utcnow()

                # Store index history snapshot
                index_history = IndexHistory(
                    index_id=index.id,
                    value=idx_info.get("value"),
                    points_change=idx_info.get("pointChange"),
                    percent_change=idx_info.get("percentChange")
                )
                self.db.add(index_history)
                count += 1

            except Exception as e:
                logger.warning(f"Failed to store index {symbol}: {e}")
                continue

        self.db.commit()
        logger.info(f"Stored {count} index records")
        return count

    def run_once(self) -> dict:
        """Run pipeline once: fetch data and store, or use cached data if API unavailable."""
        try:
            market_data = self.fetch_live_market()
            index_data = self.fetch_nepse_index()

            # If both fetches failed, use cached data
            if not market_data and not index_data:
                cached_result = self._use_cached_data()
                if cached_result["status"] == "success":
                    logger.warning("Using cached market data due to API unavailability")
                    return cached_result
                else:
                    return {
                        "status": "error",
                        "message": f"API unavailable and no cached data available. Last error: {self.last_error}",
                        "api_status": self.api_status,
                        "last_successful_fetch": self.last_successful_fetch.isoformat() if self.last_successful_fetch else None,
                        "timestamp": datetime.utcnow().isoformat()
                    }

            stocks_count = self.store_stocks(market_data) if market_data else 0
            indices_count = self.store_indices(index_data) if index_data else 0

            result = {
                "status": "success",
                "stocks_stored": stocks_count,
                "indices_stored": indices_count,
                "api_status": self.api_status,
                "last_successful_fetch": self.last_successful_fetch.isoformat() if self.last_successful_fetch else None,
                "timestamp": datetime.utcnow().isoformat()
            }
            logger.info(f"Pipeline run successful: {result}")
            return result

        except Exception as e:
            logger.error(f"Pipeline run failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "api_status": self.api_status,
                "timestamp": datetime.utcnow().isoformat()
            }
        finally:
            self.db.close()

    def _use_cached_data(self) -> dict:
        """Verify that cached data exists (latest records in database)."""
        try:
            latest_stock = self.db.query(Stock).order_by(desc(Stock.updated_at)).first()
            latest_index = self.db.query(Index).order_by(desc(Index.updated_at)).first()

            if latest_stock or latest_index:
                return {
                    "status": "success",
                    "stocks_stored": 0,
                    "indices_stored": 0,
                    "cached": True,
                    "last_stock_update": latest_stock.updated_at.isoformat() if latest_stock else None,
                    "last_index_update": latest_index.updated_at.isoformat() if latest_index else None,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "message": "No cached data available",
                    "cached": False,
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            logger.error(f"Error checking cached data: {e}")
            return {
                "status": "error",
                "message": f"Error accessing cached data: {e}",
                "timestamp": datetime.utcnow().isoformat()
            }

    def get_api_health(self) -> dict:
        """Get current API health status."""
        return {
            "status": self.api_status,
            "last_successful_fetch": self.last_successful_fetch.isoformat() if self.last_successful_fetch else None,
            "last_error": self.last_error,
            "timestamp": datetime.utcnow().isoformat()
        }


def get_pipeline(db: Session = None) -> NEPSEPipeline:
    """Factory function for pipeline."""
    return NEPSEPipeline(db)
