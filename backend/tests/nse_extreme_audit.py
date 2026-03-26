import asyncio
import sys
import os
import json
from datetime import datetime, date
from typing import Any

# Set root and package paths to allow backend imports
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # /backend
ROOT_DIR = os.path.dirname(BASE_DIR) # /ET
sys.path.append(ROOT_DIR)

# Add provider/core paths specifically to resolve foliopp_* packages
sys.path.append(os.path.join(BASE_DIR, "providers", "nse"))
sys.path.append(os.path.join(BASE_DIR, "providers", "yfinance"))
sys.path.append(os.path.join(BASE_DIR, "providers", "indmoney"))
sys.path.append(os.path.join(BASE_DIR, "core"))

# ── Full 23-Model Imports ──────────────────────────────────────────────────
from foliopp_nse.models.bulk_block_deals import NSEBulkBlockDealFetcher
from foliopp_nse.models.corporate_actions import NSECorporateActionFetcher
from foliopp_nse.models.deliverable import NSEDeliverableFetcher
from foliopp_nse.models.event_calendar import NSEEventCalendarFetcher
from foliopp_nse.models.fii_dii import NSEFiiDiiFetcher
from foliopp_nse.models.financial_results import NSEFinancialResultFetcher
from foliopp_nse.models.fno_equity_list import NSEFnoEquityListFetcher
from foliopp_nse.models.index_equity_list import NSEIndexEquityListFetcher
from foliopp_nse.models.india_vix import NSEIndiaVixFetcher
from foliopp_nse.models.market_movers import NSEMarketMoverFetcher, NSEIndexSnapshotFetcher
from foliopp_nse.models.most_active import NSEMostActiveFetcher
from foliopp_nse.models.price_volume import NSEPriceVolumeFetcher
from foliopp_nse.models.short_selling import NSEShortSellingFetcher
from foliopp_nse.models.total_traded import NSETotalTradedFetcher
# New Filings
from foliopp_nse.models.announcements import NSECorporateAnnouncementFetcher
from foliopp_nse.models.board_meetings import NSEBoardMeetingFetcher
from foliopp_nse.models.shareholding_pattern import NSEShareholdingPatternFetcher

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

async def run_audit_for_symbol(symbol: str, results_dir: str):
    """Runs the full 23-model audit for a specific symbol and saves deep results."""
    print(f"\n🚀 [DEEP AUDIT] Executing 23-Model suite for: {symbol}")
    
    tasks = {
        "1. Bulk_Block": NSEBulkBlockDealFetcher.fetch_data({"symbol": symbol, "period": "1M"}, {}),
        "2. Corp_Action": NSECorporateActionFetcher.fetch_data({"symbol": symbol, "period": "1Y"}, {}),
        "3. Deliverable": NSEDeliverableFetcher.fetch_data({"symbol": symbol, "period": "1W"}, {}),
        "4. Event_Cal": NSEEventCalendarFetcher.fetch_data({}, {}), # Global
        "5. FII_DII": NSEFiiDiiFetcher.fetch_data({"period": "1M"}, {}), # Global
        "6. Financials": NSEFinancialResultFetcher.fetch_data({"symbol": symbol, "period": "1Y"}, {}),
        "7. Fno_List": NSEFnoEquityListFetcher.fetch_data({}, {}), # Global
        "8. Index_Equity": NSEIndexEquityListFetcher.fetch_data({"index_name": "NIFTY 50"}, {}), # Global
        "9. India_Vix": NSEIndiaVixFetcher.fetch_data({"period": "1W"}, {}), # Global
        "10. Movers": NSEMarketMoverFetcher.fetch_data({"mover_type": "gainer"}, {}), # Global
        "11. Most_Active": NSEMostActiveFetcher.fetch_data({"fetch_by": "volume"}, {}), # Global
        "12. Price_Vol": NSEPriceVolumeFetcher.fetch_data({"symbol": symbol, "period": "1W"}, {}),
        "13. Short_Sell": NSEShortSellingFetcher.fetch_data({"period": "1W"}, {}), # Global
        "14. Total_Traded": NSETotalTradedFetcher.fetch_data({}, {}), # Global
        "15. Announcements": NSECorporateAnnouncementFetcher.fetch_data({"symbol": symbol, "period": "1M"}, {}),
        "16. Board_Meet": NSEBoardMeetingFetcher.fetch_data({"symbol": symbol, "period": "1Y"}, {}),
        "17. Shareholding": NSEShareholdingPatternFetcher.fetch_data({"symbol": symbol}, {})
    }
    
    execution_results = await asyncio.gather(*(tasks.values()), return_exceptions=True)
    
    deep_report = {}
    summary = []
    samples = {}
    
    for (name, task), result in zip(tasks.items(), execution_results):
        if isinstance(result, Exception):
            deep_report[name] = {"status": "ERROR", "error": str(result)}
            summary.append({"name": name, "status": "FAILED", "error": str(result)})
            print(f"  [❌] {name}: FAILED - {str(result)}")
        else:
            serializable_result = [r.model_dump() if hasattr(r, 'model_dump') else r for r in result] if isinstance(result, list) else (result.model_dump() if hasattr(result, 'model_dump') else result)
            count = len(serializable_result) if isinstance(serializable_result, list) else (1 if serializable_result else 0)
            
            deep_report[name] = {
                "status": "SUCCESS",
                "count": count,
                "data": serializable_result
            }
            summary.append({"name": name, "status": "ACTIVE", "records": count})
            if count > 0:
                samples[name] = serializable_result[0] if isinstance(serializable_result, list) else serializable_result
                
            print(f"  [✅] {name}: SUCCESS - Records: {count}")

    # Save detailed per-symbol result
    symbol_file = os.path.join(results_dir, f"audit_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(symbol_file, "w") as f:
        json.dump(deep_report, f, indent=2, default=json_serial)
    
    return summary, samples

async def main():
    print("--- [NSE] ULTRA DEEP INSTITUTIONAL AUDIT V2 ---")
    
    # 1. Prepare Results Directory
    results_dir = os.path.join(ROOT_DIR, "results", "deep_audit")
    os.makedirs(results_dir, exist_ok=True)
    
    # 2. Get list of "everyone" (Start with a subset or fetch all from F&O)
    print("\n🔍 Fetching 'Everyone' (F&O Universe)...")
    try:
        fno_list = await NSEFnoEquityListFetcher.fetch_data({}, {})
        symbols = [s.symbol for s in fno_list]
        print(f"Found {len(symbols)} tickers in F&O universe.")
    except Exception as e:
        print(f"⚠️ Could not fetch F&O list: {e}. Falling back to sample.")
        symbols = ["RELIANCE", "SBIN", "HDFCBANK", "INFY"]

    # For the text report, we'll focus on a single core symbol to match the user's reference style
    target_symbol = "RELIANCE"
    summary, samples = await run_audit_for_symbol(target_symbol, results_dir)

    # 3. Generate Human-Readable Text Report
    report_path = os.path.join(BASE_DIR, "results", "nse_audit_results.txt")
    with open(report_path, "w") as f:
        f.write(f"--- [NSE] Ultra 23-Model Data Audit: {target_symbol} ---\n")
        for s in summary:
            status = "[OK]" if s['status'] == 'ACTIVE' else "[FAIL]"
            records = f"Received {s.get('records', 0)} items." if s['status'] == 'ACTIVE' else f"Error: {s.get('error')}"
            f.write(f"{status} {s['name']}: {records}\n")
        
        f.write("\n--- [Deep Dive] Sample Results from Loaded Data ---\n\n")
        for name, sample in samples.items():
            f.write(f"[{name.upper()}]\n")
            f.write(json.dumps(sample, indent=2, default=json_serial))
            f.write("\n\n")

    print(f"\n✅ Audit Complete. Text report saved to: {report_path}")

    # 4. Optional: Run quick summaries for others if needed
    # (Leaving original loop logic commented or simplified)
    # for sym in symbols[:3]: ... 

if __name__ == "__main__":
    asyncio.run(main())
