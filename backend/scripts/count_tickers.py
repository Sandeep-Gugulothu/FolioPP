import asyncio
import sys
import os

# Set root to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.clients.postgres import AsyncSessionLocal
from backend.core.foliopp_core.database.models import NSETicker, PortfolioEntry
from sqlalchemy import select

async def count_tickers():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(NSETicker))
        tickers = res.scalars().all()
        print(f"Total NSE Tickers: {len(tickers)}")
        
        res = await db.execute(select(PortfolioEntry))
        portfolio = res.scalars().all()
        print(f"Total Portfolio Tickers: {len(portfolio)}")

if __name__ == "__main__":
    asyncio.run(count_tickers())
