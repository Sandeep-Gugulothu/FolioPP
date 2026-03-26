"""News Collector Worker - Phase 1: Ingestion.
Crawls top Indian market context periodically and saves to MinIO 'raw-data' bucket.
"""

import asyncio
import logging
from typing import List
from datetime import datetime

from backend.config import settings
from backend.core.foliopp_core.pipeline.ingestion import DataIngestionPipeline
from foliopp_yfinance.models.company_news import YFinanceCompanyNewsFetcher

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("NewsCollector")

# 🏛 Focus tickers for Indian market research
INDIAN_FOCUS_TICKERS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "SBIN.NS", 
    "INFY.NS", "NIFTY_50", "BANK_NIFTY"
]

class NewsCollectorWorker:
    def __init__(self, tickers: List[str]):
        self.tickers = tickers
        self.pipeline = DataIngestionPipeline(provider="yfinance", fetcher_name="company_news")
        self.is_running = False

    async def fetch_and_ingest(self, ticker: str):
        """Fetch news for a ticker and save it into the Phase 1 Ingestion bucket."""
        logger.info(f"📡 Collecting news for {ticker}...")
        try:
            # 1. Fetch RAW data from provider
            news_items = await YFinanceCompanyNewsFetcher.fetch_data(
                {"symbol": ticker, "exchange": "NSE"}, {}
            )
            
            if not news_items:
                logger.warning(f"⚠️ No new news found for {ticker}.")
                return

            # 2. Trigger Ingestion Pipeline (MinIO + Postgres)
            batch_id = await self.pipeline.ingest(
                query={"symbol": ticker, "timestamp": datetime.now().isoformat()},
                data=news_items
            )
            logger.info(f"✅ Ingested {len(news_items)} items for {ticker}. Batch: {batch_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to collect news for {ticker}: {str(e)}")

    async def run_forever(self, interval_seconds: int = 1800):
        """Main loop: crawls the focus list every 30 minutes."""
        self.is_running = True
        logger.info(f"🚀 News Collector Worker started (Interval: {interval_seconds}s)")
        
        while self.is_running:
            tasks = [self.fetch_and_ingest(ticker) for ticker in self.tickers]
            await asyncio.gather(*tasks)
            
            logger.info(f"💤 Sleeping for {interval_seconds} seconds...")
            await asyncio.sleep(interval_seconds)

if __name__ == "__main__":
    worker = NewsCollectorWorker(INDIAN_FOCUS_TICKERS)
    try:
        asyncio.run(worker.run_forever())
    except KeyboardInterrupt:
        logger.info("🛑 News Collector Worker stopped by user.")
