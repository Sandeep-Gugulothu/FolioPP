"""Institutional Database Direct Viewer."""

import asyncio
from sqlalchemy import select
from backend.clients.postgres import AsyncSessionLocal
from backend.core.foliopp_core.database.models import (
    User, PortfolioEntry, NSETicker
)

async def view_raw_data():
    print("\n" + "🚀" + "="*80 + "🚀")
    print("🧠 FOLIO-PP RAW POSTGRES DATA EXPORTER")
    print("="*84)
    
    async with AsyncSessionLocal() as db:
        # 👤 USERS
        res = await db.execute(select(User))
        users = res.scalars().all()
        print(f"\n[👤 USERS TABLE] ({len(users)} records)")
        print(f"{'ID':<5} | {'USERNAME':<15} | {'EMAIL':<25} | {'CREATED AT'}")
        print("-" * 84)
        for u in users:
            print(f"{u.id:<5} | {u.username:<15} | {u.email:<25} | {u.created_at}")

        # 💼 PORTFOLIO
        res = await db.execute(select(PortfolioEntry))
        holdings = res.scalars().all()
        print(f"\n[💼 PORTFOLIO_ENTRIES TABLE] ({len(holdings)} records)")
        print(f"{'SYMBOL':<10} | {'UNITS':<8} | {'AVG PRICE':<12} | {'SECTOR'}")
        print("-" * 84)
        for h in holdings:
            print(f"{h.symbol:<10} | {h.units:<8} | ₹{h.avg_price:<11.2f} | {h.sector}")

        # 📈 TICKERS (Limited to top 10 for visibility)
        res = await db.execute(select(NSETicker).limit(10))
        tickers = res.scalars().all()
        print(f"\n[📈 NSE_TICKERS TABLE] (Showing first 10 of 206+ records)")
        print(f"{'SYMBOL':<15} | {'NAME'}")
        print("-" * 84)
        for t in tickers:
            print(f"{t.symbol:<15} | {t.name}")

    print("\n" + "="*84)
    print("✅ END OF RAW DATA - Verified from localhost:5432/etdb")
    print("="*84 + "\n")

if __name__ == "__main__":
    asyncio.run(view_raw_data())
