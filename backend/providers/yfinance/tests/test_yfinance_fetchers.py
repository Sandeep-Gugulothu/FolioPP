"""Smoke test for FolioPP yfinance provider.

Run:
    python backend/providers/yfinance/tests/test_yfinance_fetchers.py
"""

from foliopp_yfinance.models.equity_historical import YFinanceEquityHistoricalFetcher
from foliopp_yfinance.models.equity_quote import YFinanceEquityQuoteFetcher


def test_equity_historical_fetcher():
    print("\n-- Testing Historical Fetcher --")
    results = YFinanceEquityHistoricalFetcher.fetch_data_sync({
        "symbol": "RELIANCE",
        "exchange": "NSE",
        "start_date": "2024-01-01",
        "end_date": "2024-01-10",
    })
    assert isinstance(results, list)
    assert len(results) > 0
    row = results[0]
    assert row.symbol == "RELIANCE"
    assert row.exchange == "NSE"
    assert row.currency == "INR"
    assert row.open > 0
    assert row.close > 0
    print(f"  {row.date}  O:{row.open}  H:{row.high}  L:{row.low}  C:{row.close}  V:{row.volume}")


def test_equity_quote_fetcher():
    print("\n-- Testing Quote Fetcher --")
    quote = YFinanceEquityQuoteFetcher.fetch_data_sync({
        "symbol": "TCS",
        "exchange": "NSE",
    })
    assert quote.symbol == "TCS"
    assert quote.price > 0
    assert quote.currency == "INR"
    print(f"  {quote.symbol} | {quote.name} | INR {quote.price} | {quote.change_pct:.2f}%")


if __name__ == "__main__":
    test_equity_historical_fetcher()
    test_equity_quote_fetcher()
