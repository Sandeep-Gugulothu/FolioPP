import asyncio
import sys
import os
import json

# Set root to allow backend imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from foliopp_yfinance.models.equity_quote import YFinanceEquityQuoteFetcher
from foliopp_yfinance.models.equity_profile import YFinanceEquityProfileFetcher
from foliopp_yfinance.models.equity_historical import YFinanceEquityHistoricalFetcher
from foliopp_yfinance.models.company_news import YFinanceCompanyNewsFetcher
from foliopp_yfinance.models.key_metrics import YFinanceKeyMetricsFetcher

from foliopp_yfinance.models.income_statement import YFinanceIncomeStatementFetcher
from foliopp_yfinance.models.balance_sheet import YFinanceBalanceSheetFetcher
from foliopp_yfinance.models.cash_flow import YFinanceCashFlowFetcher

async def audit_yfinance_data(symbol="RELIANCE.NS"):
    print(f"--- [yfinance] Full 8-Point Data Audit: {symbol} ---")
    
    tasks = {
        "1. Quote": YFinanceEquityQuoteFetcher.fetch_data({"symbol": symbol, "exchange": "NSE"}, {}),
        "2. Profile": YFinanceEquityProfileFetcher.fetch_data({"symbol": symbol, "exchange": "NSE"}, {}),
        "3. Historical": YFinanceEquityHistoricalFetcher.fetch_data({"symbol": symbol, "period": "5d"}, {}),
        "4. News": YFinanceCompanyNewsFetcher.fetch_data({"symbol": symbol, "exchange": "NSE"}, {}),
        "5. Metrics": YFinanceKeyMetricsFetcher.fetch_data({"symbol": symbol}, {}),
        "6. IncomeStmt": YFinanceIncomeStatementFetcher.fetch_data({"symbol": symbol, "period": "annual", "limit": 1}, {}),
        "7. BalanceSheet": YFinanceBalanceSheetFetcher.fetch_data({"symbol": symbol, "period": "annual", "limit": 1}, {}),
        "8. CashFlow": YFinanceCashFlowFetcher.fetch_data({"symbol": symbol, "period": "annual", "limit": 1}, {})
    }
    
    results = await asyncio.gather(*(tasks.values()), return_exceptions=True)
    
    audit_log = {}
    for (name, task), result in zip(tasks.items(), results):
        if isinstance(result, Exception):
            print(f"[ERROR] {name}: {str(result)}")
            audit_log[name] = {"error": str(result)}
        else:
            # Handle list vs object
            if isinstance(result, list):
                sample = [r.model_dump() if hasattr(r, 'model_dump') else r for r in result[:1]]
                audit_log[name] = {"count": len(result), "sample_keys": list(sample[0].keys()) if sample else []}
                print(f"[OK] {name}: Received {len(result)} items.")
            else:
                dump = result.model_dump() if hasattr(result, 'model_dump') else result
                audit_log[name] = {"keys": list(dump.keys())}
                print(f"[OK] {name}: Received full metadata.")

    # Deep Dive into all 8
    print("\n--- [Deep Dive] All 8 Institutional Data Points ---")
    for (name, task), result in zip(tasks.items(), results):
        print(f"\n[{name.upper()}]")
        if isinstance(result, Exception):
            print(f"Error: {str(result)}")
        elif isinstance(result, list):
            if result:
                sample = result[0]
                data = sample.model_dump() if hasattr(sample, 'model_dump') else sample
                # If historical, truncate for space
                if "Historical" in name:
                    print(json.dumps(data, indent=2, default=str)[:500] + "...")
                else:
                    print(json.dumps(data, indent=2, default=str))
            else:
                print("Empty List")
        else:
            data = result.model_dump() if hasattr(result, 'model_dump') else result
            print(json.dumps(data, indent=2, default=str))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default="RELIANCE.NS")
    args = parser.parse_args()
    asyncio.run(audit_yfinance_data(args.symbol))
