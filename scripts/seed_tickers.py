"""Seed Script - Populates the NSETicker table from NSE F&O list."""

import asyncio
import logging
from sqlalchemy.dialects.postgresql import insert

from backend.clients.postgres import AsyncSessionLocal
from backend.core.foliopp_core.database.models import NSETicker
from foliopp_nse.models.fno_equity_list import NSEFnoEquityListFetcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SeedTickers")

async def seed():
    logger.info("📡 Fetching NSE F&O Ticker List...")
    try:
        # F&O list is a good proxy for most actively traded stocks (Nifty 200 approx)
        tickers = await NSEFnoEquityListFetcher.fetch_data({}, {})
        
        async with AsyncSessionLocal() as db:
            for t in tickers:
                # Use UPSERT logic
                stmt = insert(NSETicker).values(
                    symbol=t.symbol,
                    name=t.symbol, # Fallback to symbol for name if not in data
                    sector="Various"
                ).on_conflict_do_nothing()
                await db.execute(stmt)
            
            await db.commit()
            logger.info(f"✅ Successfully seeded {len(tickers)} tickers to Postgres.")
            
    except Exception as e:
        logger.error(f"❌ Seed failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(seed())
