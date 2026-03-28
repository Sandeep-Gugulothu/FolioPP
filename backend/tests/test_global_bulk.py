import asyncio
import sys
import os
from datetime import date, timedelta
import pandas as pd
from io import BytesIO

# Set root and package paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, "providers", "nse"))
sys.path.append(os.path.join(BASE_DIR, "core"))

from foliopp_nse.models.bulk_block_deals import NSEBulkBlockDealFetcher
from foliopp_nse.utils.helpers import nse_fetch, to_nse_date, NSE_BASE

async def test_global_bulk_deals():
    print("--- Testing GLOBAL Market Bulk Deals (Multi-Stock) ---")
    
    # 1. Fetch data for the last 3 days (ensuring we catch the last Friday trading day)
    today = date.today()
    from_date = today - timedelta(days=3)
    
    url = f"{NSE_BASE}/api/historicalOR/bulk-block-short-deals"
    params = {
        "optionType": "bulk_deals",
        "from": to_nse_date(from_date),
        "to": to_nse_date(today),
        "csv": "true",
    }
    
    print(f"Window: {from_date} to {today}")
    resp = nse_fetch(url, params=params)
    
    if resp.status_code == 200 and resp.content:
        # Load into Pandas for quick analysis
        df = pd.read_csv(BytesIO(resp.content))
        # Clear spaces from columns
        df.columns = [c.strip() for c in df.columns]
        
        # Sort by Quantity (Top institutional moves)
        # Note: Quantity in CSV sometimes has commas, let's clean it
        df['Quantity Traded'] = df['Quantity Traded'].astype(str).str.replace(',', '').astype(float)
        top_moves = df.sort_values(by='Quantity Traded', ascending=False).head(10)
        
        print(f"\n✅ SUCCESS: Found {len(df)} total market bulk deals.")
        print("-" * 100)
        print(f"{'Date':<12} | {'Symbol':<10} | {'Client':<35} | {'Buy/Sell':<8} | {'Quantity':<12}")
        print("-" * 100)
        
        for _, row in top_moves.iterrows():
            print(f"{row['Date']:<12} | {row['Symbol']:<10} | {row['Client Name'][:33]:<35} | {row['Buy / Sell']:<8} | {int(row['Quantity Traded']):,}")
            
    else:
        print(f"❌ FAILED: Status {resp.status_code}. No data received.")

if __name__ == "__main__":
    asyncio.run(test_global_bulk_deals())
