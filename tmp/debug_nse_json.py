import asyncio
import sys
import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
ROOT_DIR = os.path.dirname(BASE_DIR) 
sys.path.append(ROOT_DIR)
sys.path.append(os.path.join(BASE_DIR, "providers", "nse"))

from foliopp_nse.utils.helpers import nse_fetch, nse_json, NSE_BASE

async def debug():
    symbol = "RELIANCE"
    # Note: Using likely singular endpoints
    endpoints = {
        "SDD_Pattern": f"{NSE_BASE}/api/corporate-shareholding-pattern-sdd?symbol={symbol}",
        "Offer_Doc": f"{NSE_BASE}/api/corporate-issuer-offer-documents?companyName={symbol}",
        "Integrated_Fil": f"{NSE_BASE}/api/integrated-filing?index=equities&symbol={symbol}",
        "Scheme_Arr": f"{NSE_BASE}/api/corporate-schemes-of-arrangements?index=equities&symbol={symbol}"
    }
    
    for name, url in endpoints.items():
        print(f"\n--- {name} ---")
        try:
            resp = nse_fetch(url)
            data = nse_json(resp)
            if isinstance(data, dict) and "data" in data:
                data = data["data"]
            
            if data and len(data) > 0:
                print(f"Keys: {list(data[0].keys())}")
                print(f"Sample: {json.dumps(data[0], indent=2)}")
            else:
                print(f"No records found for {name} with url {url}")
        except Exception as e:
            print(f"Error in {name}: {e}")

if __name__ == "__main__":
    asyncio.run(debug())
