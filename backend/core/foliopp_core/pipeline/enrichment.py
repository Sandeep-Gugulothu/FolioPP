"""Phase 2: Signal Enrichment Engine (Autonomous Synthesis)."""

from typing import List
from foliopp_core.provider.standard_models.nse_models import BulkBlockDealData
from foliopp_nse.models.price_volume import NSEPriceVolumeFetcher
from foliopp_yfinance.models.equity_quote import YFinanceEquityQuoteFetcher

class SignalEnricher:
    """
    Transforms raw 'Dumb' data into 'Agent-Ready' Intelligence.
    Matches the Track 6 Scenario 1: Promoter Stake Sale Analysis.
    """
    
    @staticmethod
    async def enrich_bulk_deal(deal: BulkBlockDealData):
        """
        Calculates % Equity and Detects Promoter without human input.
        """
        symbol = deal.symbol
        
        # 1. Fetch Total Equity (issuedSize) using the verified Quote API
        # We use YFinance as a stable secondary or NSE Quote
        quote_data = await YFinanceEquityQuoteFetcher.fetch_data({"symbol": symbol}, {})
        total_shares = quote_data.shares_outstanding if hasattr(quote_data, "shares_outstanding") else None
        
        if not total_shares:
            # Fallback to NSE Equity Quote (issuedSize)
            from foliopp_nse.utils.helpers import nse_fetch, nse_json
            url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
            resp = nse_fetch(url)
            if resp.status_code == 200:
                meta = nse_json(resp)
                total_shares = meta.get("securityInfo", {}).get("issuedSize")
        
        # 2. Perform the Math (The 'Alpha' Calculation)
        if total_shares and deal.quantity:
            deal.pct_equity = (deal.quantity / total_shares) * 100
            
        # 3. Promoter Scrutiny (Pattern Matching + Remarks)
        # Note: Future versions will check the Knowledge Graph (Neo4j)
        if deal.client_name:
            client_upper = str(deal.client_name).upper()
            if any(x in client_upper for x in ["PROMOTER", "PROMOTERS", "TRUST", "FAMILY"]):
                deal.is_promoter = True
        
        # 4. Final Flagging: The 3-Step Sequence requirement for Track 6
        # Logic: If Promoter + Sell + >2% Equity = HIGH PRIORITY
        if deal.deal_type == "bulk" and deal.buy_sell == "SELL" and deal.is_promoter:
            if deal.pct_equity and deal.pct_equity > 2.0:
                deal.priority = 1 # SIGNAL DETECTED
                
        return deal

    @classmethod
    async def enrich_batch(cls, deals: List[BulkBlockDealData]):
        """Batch processing for the Ingestion Pipeline."""
        return [await cls.enrich_bulk_deal(d) for d in deals]

enricher = SignalEnricher()
