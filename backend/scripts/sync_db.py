"""Table Schema Creation Script - Initializes Database Models."""

import asyncio
from backend.clients.postgres import engine, Base
from backend.core.foliopp_core.database.models import IngestedBatch, BulkDeal, KnowledgeNode, PortfolioEntry, NSETicker

async def sync_schema():
    print("📡 Synchronizing PostgreSQL schema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ All tables (including nse_tickers) are now active in the DB.")

if __name__ == "__main__":
    asyncio.run(sync_schema())
