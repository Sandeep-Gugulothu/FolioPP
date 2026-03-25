from backend.clients.postgres import AsyncSessionLocal
from backend.core.foliopp_core.database.models import BulkDeal, IngestedBatch
from backend.core.foliopp_core.pipeline.enrichment import SignalEnricher
from foliopp_nse.models.bulk_block_deals import NSEBulkBlockDealFetcher
from backend.config import settings

class NSEBulkIngestor:
    def __init__(self):
        self.fetcher = NSEBulkBlockDealFetcher()
        self.enricher = SignalEnricher()

    async def run(self, query_params: dict):
        """
        Executes the Phase 1 & 2 Workflow:
        1. Fetch Raw CSV (Deterministic Fetcher)
        2. Enrich with Equity Metrics (The Brain)
        3. Identify Priority Signals (Flagging Logic)
        4. Store in PostgreSQL
        """
        # 1. Fetching
        raw_deals = await self.fetcher.fetch_data(query_params, {})
        
        # 2. Enrichment (The 'Alpha' Layer)
        enriched_deals = await self.enricher.enrich_batch(raw_deals)
        
        # 3. Storage in PostgreSQL
        async with AsyncSessionLocal() as db:
            for deal in enriched_deals:
                bulk_deal = BulkDeal(
                    trade_date=deal.date,
                    symbol=deal.symbol,
                    client_name=deal.client_name,
                    deal_type=deal.deal_type,
                    quantity=deal.quantity,
                    price=deal.price,
                    is_promoter=deal.is_promoter,
                    pct_equity=deal.pct_equity,
                    priority=deal.priority,
                    raw_metadata={"client": deal.client_name, "security": deal.security_name}
                )
                db.add(bulk_deal)
            
            await db.commit()
            return enriched_deals # Return all for the UI

bulk_ingestor = NSEBulkIngestor()
