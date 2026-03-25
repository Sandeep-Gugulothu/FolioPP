# NSE India Data Provider

The `nse` provider is a specialized integration for the Indian Equity Market, offering deep insights into domestic exchange data. We have implemented **17 specialized fetchers** to cover the full spectrum of NSE's data reports:

### 1. Market Snapshot & Core Data
-   **Market Movers**: Real-time Top Gainers, Losers, and Volume Shockers.
-   **Index Snapshot**: Current levels, changes, and advance/decline ratios for all major indices.
-   **India VIX**: The "Fear Gauge" representing market volatility expectations.
-   **Total Traded**: Market-wide advance/decline and total volume stats.

### 2. Security-Level Analysis
-   **Deliverable Position**: Detailed Price-Volume-Delivery data to distinguish between speculative and delivery trades.
-   **Price Volume**: Basic high-resolution OHLCV data for equity symbols.
-   **Short Selling**: Daily reports on short selling activity for individual securities.

### 3. Institutional & Large Trades
-   **Bulk & Block Deals**: Real-time and historical tracking of large institutional transactions.
-   **FII/DII Activity**: Daily net buy/sell values for Foreign and Domestic Institutional Investors.
-   **Most Active**: Equities with the highest trading activity by value or volume.

### 4. Corporate Context & Results
-   **Financial Results**: Quarterly and annual financial results filings directly from corporates.
-   **Corporate Actions**: Automated tracking of dividends, splits, and board meetings.
-   **Event Calendar**: A specialized feed of upcoming key corporate events and results dates.

### 5. Index & Historical Intelligence
-   **Index Historical**: Comprehensive OHLCV history for all NSE indices (NIFTY 50, MIDCAP, etc.).
-   **PE Ratio**: Historical Price-to-Earnings and Price-to-Book ratios for indices.
-   **Index Constituents**: Live list of symbols belonging to specific indices (e.g. NIFTY 100).
-   **F&O Equity List**: The official list of securities available for trading in the Derivatives segment.

## Overview

The FolioPP platform uses the NSE provider as the primary source for all India-specific financial signals. Unlike global aggregators, this provider hits NSE's official API endpoints directly to extract high-fidelity metadata.

### Implementation Details

The NSE integration is one of our most robust, featuring over 17 distinct fetchers for specialized reports.

-   **Location**: `backend/providers/nse/foliopp_nse/`
-   **Methodology**: Direct HTTP calls to NSE's authenticated API endpoints using a managed session pattern to handle cookies and headers.

## Key Components

### 1. Session Management
Located in `utils/helpers.py`, this component handles the tricky authentication required by NSE:
-   **Automated Refresh**: Hits the NSE homepage to obtain valid cookies before API calls.
-   **Session Persistence**: Reuses cookies across multiple fetchers to avoid rate limits.
-   **Encoding**: Uses `utf-8-sig` to handle Byte Order Marks (BOM) in raw data responses.

### 2. Specialized Fetchers
The provider implements standardized fetchers for:
-   **`NSEDeliverableFetcher`**: Provides "Deliverable Quantity" percentages for accumulation/distribution analysis.
-   **`NSEIndiaVixFetcher`**: Tracks the market's "Fear Gauge."
-   **`NSEMarketMoverFetcher`**: Real-time Top Gainers, Losers, and Volume Shockers.
-   **`NSECorporateActionFetcher`**: Tracking board meetings, dividends, and results.
-   **`NSEFiiDiiFetcher`**: Daily Institutional Investment activity.

### 3. Data Reliability
-   **Numeric Cleaning**: Implements `safe_float` to handle Indian lakh/crore number formatting and commas.
-   **Historical Chunking**: NSE restricts specific historical requests (e.g., Price/Volume) to roughly 1 year per call. The fetcher automatically chunks date ranges and merges the results.

## Usage Pattern

NSE fetchers utilize the standardized `foliopp_core` pipeline:

```python
from foliopp_nse.models.deliverable import NSEDeliverableFetcher

# Fetch deliverable position data for State Bank of India
results = NSEDeliverableFetcher.fetch_data_sync({
    "symbol": "SBIN",
    "period": "1M"
})

for row in results:
    print(f"Date: {row.date} | Delivery %: {row.pct_delivery}")
```

## Why NSE?
1.  **Primary Source**: Direct exchange-level data ensures accuracy.
2.  **Unique Metadata**: Access to "Number of Trades" and daily "Deliverable Quantity" not available elsewhere.
3.  **Regional Signals**: FII/DII flows and India VIX are essential for local volatility scoring.
