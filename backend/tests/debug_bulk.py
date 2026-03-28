import asyncio
import sys
import os
from datetime import date, timedelta

# Set root and package paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, "providers", "nse"))
sys.path.append(os.path.join(BASE_DIR, "core"))

from foliopp_nse.models.bulk_block_deals import NSEBulkBlockDealFetcher
from foliopp_nse.utils.helpers import nse_fetch, to_nse_date, NSE_BASE

async def debug_bulk_deals(symbol: str):
    print(f"--- Debugging Bulk Deals for {symbol} ---")
    
    # 1. Manual API Hit
    today = date.today()
    from_date = today - timedelta(days=2)
    
    url = f"{NSE_BASE}/api/historicalOR/bulk-block-short-deals"
    params = {
        "optionType": "bulk_deals",
        "from": to_nse_date(from_date),
        "to": to_nse_date(today),
        "csv": "true",
    }
    
    print(f"Requesting URL: {url}")
    print(f"Params: {params}")
    
    resp = nse_fetch(url, params=params)
    print(f"Status: {resp.status_code}")
    print(f"Has Content: {bool(resp.content)}")
    
    if resp.content:
        # Check first 500 chars of content
        content_sample = resp.content[:500].decode('utf-8', errors='ignore')
        print(f"Content Sample:\n{content_sample}")
        
        # Check if symbol is in content
        if symbol.upper() in content_sample:
            print(f"SUCCESS: Found {symbol} in the raw CSV content.")
        else:
            print(f"WARNING: {symbol} NOT found in the first 500 chars.")
            
    # 2. Run Fetcher
    try:
        results = await NSEBulkBlockDealFetcher.fetch_data({"symbol": symbol, "period": "1M"}, {})
        print(f"Fetcher Results: {len(results)} records")
        for r in results[:2]:
            print(f"- {r.date}: {r.client_name} ({r.buy_sell}) {r.quantity}")
    except Exception as e:
        print(f"Fetcher Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_bulk_deals("GTPL"))
