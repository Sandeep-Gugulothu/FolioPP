"""Smoke tests for all NSE provider fetchers.

Run:
    python backend/providers/nse/tests/test_nse_fetchers.py
"""

import sys
import os
from datetime import date, timedelta

# Add provider and core to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from foliopp_nse.models.market_movers import NSEMarketMoverFetcher, NSEIndexSnapshotFetcher
from foliopp_nse.models.india_vix import NSEIndiaVixFetcher
from foliopp_nse.models.deliverable import NSEDeliverableFetcher
from foliopp_nse.models.index_historical import NSEIndexHistoricalFetcher
from foliopp_nse.models.pe_ratio import NSEPERatioFetcher
from foliopp_nse.models.fno_equity_list import NSEFnoEquityListFetcher
from foliopp_nse.models.index_equity_list import NSEIndexEquityListFetcher
from foliopp_nse.models.most_active import NSEMostActiveFetcher
from foliopp_nse.models.total_traded import NSETotalTradedFetcher
from foliopp_nse.models.short_selling import NSEShortSellingFetcher
from foliopp_nse.models.fii_dii import NSEFiiDiiFetcher
from foliopp_nse.models.corporate_actions import NSECorporateActionFetcher
from foliopp_nse.models.event_calendar import NSEEventCalendarFetcher
from foliopp_nse.models.financial_results import NSEFinancialResultFetcher
from foliopp_nse.models.price_volume import NSEPriceVolumeFetcher
from foliopp_nse.models.bulk_block_deals import NSEBulkBlockDealFetcher

def test_fetcher(name, fetcher, params):
    print(f"\n-- Testing {name} --")
    try:
        results = fetcher.fetch_data_sync(params, {})
        assert isinstance(results, list)
        if not results:
            print(f"  Warning: No results returned for {name}.")
            return
        row = results[0]
        # Use model_dump() if available (Pydantic models)
        summary = row.model_dump() if hasattr(row, "model_dump") else row
        print(f"  Success: {len(results)} rows. First: {summary}")
    except Exception as e:
        print(f"  Error in {name}: {e}")

if __name__ == "__main__":
    # 1. Market Movers & Snapshot
    test_fetcher("Market Mover (Gainer)", NSEMarketMoverFetcher, {"mover_type": "gainer"})
    test_fetcher("Index Snapshot", NSEIndexSnapshotFetcher, {})
    test_fetcher("India VIX (1M)", NSEIndiaVixFetcher, {"period": "1M"})
    test_fetcher("Deliverable (SBIN)", NSEDeliverableFetcher, {"symbol": "SBIN", "period": "1W"})
    
    # 5. Index Historical
    test_fetcher("Index Historical (NIFTY 50)", NSEIndexHistoricalFetcher, {"index_name": "NIFTY 50", "period": "1W"})
    
    # 6. PE Ratio (Try a recent weekday)
    target_date = date.today() - timedelta(days=4)
    test_fetcher("PE Ratio", NSEPERatioFetcher, {"trade_date": target_date.strftime("%Y-%m-%d")})
    
    # 7. Lists
    test_fetcher("FnO Equity List", NSEFnoEquityListFetcher, {})
    test_fetcher("Index Equity List", NSEIndexEquityListFetcher, {"index_name": "NIFTY MIDCAP 150"})
    
    # 9. Market Analysis
    test_fetcher("Most Active (Equities)", NSEMostActiveFetcher, {"fetch_by": "volume"})
    test_fetcher("Total Traded", NSETotalTradedFetcher, {})
    test_fetcher("Short Selling", NSEShortSellingFetcher, {"symbol": "SBIN", "period": "1M"})
    test_fetcher("FII/DII Activity", NSEFiiDiiFetcher, {})
    
    # 13. Corporates
    test_fetcher("Corporate Actions", NSECorporateActionFetcher, {"period": "1M"})
    test_fetcher("Event Calendar", NSEEventCalendarFetcher, {"period": "1M"})
    test_fetcher("Financial Results", NSEFinancialResultFetcher, {"period": "1M"})
    
    # 16. Price Volume
    test_fetcher("Price Volume (SBIN)", NSEPriceVolumeFetcher, {"symbol": "SBIN", "period": "1W"})
    test_fetcher("Bulk Deals", NSEBulkBlockDealFetcher, {"deal_type": "bulk", "period": "1M"})
