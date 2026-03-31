"""NEPSE data pipeline: fetch live data and store in PostgreSQL."""

import requests
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models import Index, Stock, MarketData, IndexHistory
from app.database import SessionLocal

logger = logging.getLogger(__name__)

NEPSE_API = "https://nepseapi.surajrimal.dev"
TIMEOUT = 10


class NEPSEPipeline:
    """Fetch live NEPSE data and persist to database."""

    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()
        self.api = NEPSE_API

    def fetch_live_market(self) -> dict:
        """Fetch live market data from NEPSE API."""
        try:
            r = requests.get(f"{self.api}/LiveMarket", timeout=TIMEOUT)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.error(f"Failed to fetch live market: {e}")
            return None

    def fetch_nepse_index(self) -> dict:
        """Fetch NEPSE index data."""
        try:
            r = requests.get(f"{self.api}/NepseIndex", timeout=TIMEOUT)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.error(f"Failed to fetch NEPSE index: {e}")
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
        """Run pipeline once: fetch data and store."""
        try:
            market_data = self.fetch_live_market()
            index_data = self.fetch_nepse_index()

            stocks_count = self.store_stocks(market_data)
            indices_count = self.store_indices(index_data)

            result = {
                "status": "success",
                "stocks_stored": stocks_count,
                "indices_stored": indices_count,
                "timestamp": datetime.utcnow().isoformat()
            }
            logger.info(f"Pipeline run successful: {result}")
            return result

        except Exception as e:
            logger.error(f"Pipeline run failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        finally:
            self.db.close()


def get_pipeline(db: Session = None) -> NEPSEPipeline:
    """Factory function for pipeline."""
    return NEPSEPipeline(db)
