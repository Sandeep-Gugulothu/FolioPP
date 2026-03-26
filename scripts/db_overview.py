"""FolioPP Database Overview Tool."""

import asyncio
from sqlalchemy import select, func
from backend.clients.postgres import AsyncSessionLocal
from backend.core.foliopp_core.database.models import (
    User, PortfolioEntry, NSETicker, BulkDeal, IngestedBatch, AuditLog
)

async def print_overview():
    print("\n" + "="*50)
    print("🧠 FOLIO-PP REAL-TIME DATABASE OVERVIEW")
    print("="*50)
    
    async with AsyncSessionLocal() as db:
        # Table counts
        tables = [
            ("👤 Users (Institutional)", User),
            ("💼 Active Portfolios", PortfolioEntry),
            ("📈 Market Tickers (NSE)", NSETicker),
            ("🤝 Multi-Million Bulk Deals", BulkDeal),
            ("📦 Ingested Raw Batches", IngestedBatch),
            ("📜 System Audit Logs", AuditLog)
        ]
        
        for name, model in tables:
            stmt = select(func.count()).select_from(model)
            res = await db.execute(stmt)
            count = res.scalar()
            print(f"- {name:<30} : {count:>5} records")

    print("\n✅ STORAGE PERSISTENCE: PostgreSQL @ localhost:5432/etdb")
    print("="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(print_overview())
