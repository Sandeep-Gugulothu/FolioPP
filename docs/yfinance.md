# yfinance Data Provider

The `yfinance` provider is our primary source for global equity historical data and financial statements. We've implemented **8 specialized fetchers** to provide comprehensive coverage:

1.  **Equity Quote**: Real-time snapshot of price, bid/ask, and volume.
2.  **Equity Profile**: Sector, industry, and detailed description.
3.  **Equity Historical**: OHLCV data with dividend and split tracking.
4.  **Company News**: Aggregated news feed for specific symbols.
5.  **Income Statement**: Annual and quarterly revenue, expenses, and margins.
6.  **Balance Sheet**: Assets, liabilities, and equity historical data.
7.  **Cash Flow**: Operating, investing, and financing activities.
8.  **Key Metrics**: Ratios like P/E, PEG, and other valuation metrics.

## Implementation Details

Our integration follows the `foliopp_core` provider pattern:

-   **Location**: `backend/providers/yfinance/foliopp_yfinance/`
-   **Standard Implementation**: `models/equity_historical.py`, `models/income_statement.py`, etc.
-   **Library**: [yfinance (yfinance-python)](https://github.com/ranaroussi/yfinance)

### Key Components

1.  **`YFinanceEquityHistoricalQueryParams`**: 
    -   Extends the standard `EquityHistoricalQueryParams`.
    -   Supports intraday intervals (`1m`, `2m`, `5m`, `15m`, `30m`, `1h`) and daily+ intervals (`1d`, `1wk`, `1mo`).
    -   Includes toggleable `adjusted` pricing and `include_actions` (splits/dividends).

2.  **`YFinanceEquityHistoricalData`**:
    -   Adds proprietary fields like `split_ratio` and `dividend` to the standard OHLCV schema.

3.  **`YFinanceEquityHistoricalFetcher`**:
    -   Handles the `extract_data` phase by calling a specialized `yf_download` helper.
    -   Implements `transform_query` to automatically fill default date ranges (last 1 year) if not provided.

### Usage Pattern

The fetcher can be invoked through the unified provider interface:

```python
from foliopp_yfinance.models.equity_historical import YFinanceEquityHistoricalFetcher

# Define parameters
params = {
    "symbol": "ADBE",
    "interval": "1d",
    "start_date": "2023-01-01",
    "end_date": "2024-01-01"
}

# Fetch and transform
processed_data = YFinanceEquityHistoricalFetcher().fetch_data_sync(params)
```

### Why yfinance?
-   **Free Tier Access**: Reliable historical data without a restrictive API key for development.
-   **Comprehensive Events**: Native support for dividends and splits, which are critical for our **Neural Performance** calculations.
-   **Multi-Interval Resolution**: High-precision intraday data for signal detection.
