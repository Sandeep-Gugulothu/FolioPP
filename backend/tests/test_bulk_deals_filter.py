import asyncio
import pandas as pd
from io import BytesIO
from unittest.mock import patch, MagicMock
from foliopp_nse.models.bulk_block_deals import NSEBulkBlockDealFetcher

# Mock the CSV response from NSE
MOCK_CSV = """Date,Symbol,SecurityName,ClientName,Buy/Sell,QuantityTraded,TradePrice/Wght.Avg.Price
28-Mar-2026,RELIANCE,Reliance Industries,PROMOTER GROUP,BUY,1000000,2850.50
28-Mar-2026,SBIN,State Bank of India,HDFC MUTUAL FUND,SELL,500000,750.25
28-Mar-2026,RELIANCE,Reliance Industries,JPMORGAN,SELL,200000,2855.00
28-Mar-2026,TATASTEEL,Tata Steel,RATA TATA,BUY,100000,150.00
"""

async def test_bulk_deals_filtering():
    fetcher = NSEBulkBlockDealFetcher()
    
    # Mock return value for nse_fetch
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.content = MOCK_CSV.encode('utf-8')
    
    with patch('foliopp_nse.utils.helpers.nse_fetch', return_value=mock_resp):
        print("\n--- Testing Holistic Fetch (No Symbol) ---")
        params_all = {"deal_type": "bulk", "period": "1D"}
        results_all = await fetcher.fetch_data(params_all, {})
        print(f"Total results: {len(results_all)}")
        for r in results_all:
            print(f"  {r.symbol}: {r.client_name} - {r.buy_sell}")
        
        assert len(results_all) == 4, "Should return all 4 deals"

        print("\n--- Testing Surgical Fetch (RELIANCE) ---")
        params_rel = {"symbol": "RELIANCE", "deal_type": "bulk", "period": "1D"}
        results_rel = await fetcher.fetch_data(params_rel, {})
        print(f"Total RELIANCE results: {len(results_rel)}")
        for r in results_rel:
            print(f"  {r.symbol}: {r.client_name}")
            assert r.symbol == "RELIANCE", "Should only contain RELIANCE"
        
        assert len(results_rel) == 2, "Should return exactly 2 RELIANCE deals"

        print("\n--- Testing Surgical Fetch (SBIN) ---")
        params_sbi = {"symbol": "SBIN", "deal_type": "bulk", "period": "1D"}
        results_sbi = await fetcher.fetch_data(params_sbi, {})
        print(f"Total SBIN results: {len(results_sbi)}")
        assert len(results_sbi) == 1, "Should return exactly 1 SBIN deal"
        assert results_sbi[0].symbol == "SBIN"

        print("\n✅ Filter Test Passed!")

if __name__ == "__main__":
    asyncio.run(test_bulk_deals_filtering())
