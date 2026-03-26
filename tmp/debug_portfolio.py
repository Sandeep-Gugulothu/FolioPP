
import asyncio
from backend.clients.postgres import AsyncSessionLocal
from sqlalchemy import select
from backend.core.foliopp_core.database.models import PortfolioEntry
from foliopp_yfinance.models.equity_quote import YFinanceEquityQuoteFetcher

async def test_portfolio():
    try:
        async with AsyncSessionLocal() as db:
            print("📡 Fetching portfolio entries...")
            stmt = select(PortfolioEntry)
            result = await db.execute(stmt)
            holdings = result.scalars().all()
            print(f"✅ Found {len(holdings)} holdings.")
            
            for h in holdings:
                print(f"📊 Processing {h.symbol}...")
                quote = await YFinanceEquityQuoteFetcher.fetch_data({"symbol": h.symbol}, {})
                print(f"✅ Quote for {h.symbol}: {quote.price}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_portfolio())
