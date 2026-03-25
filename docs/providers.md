# Data Providers

The FolioPP platform is designed with a **Provider-Agnostic Core**, allowing it to swap and scale data sources using standardized models and fetcher abstractions. Our architecture ensures that regardless of where the data comes from (NSE, YFinance, etc.), it is unified into a consistent schema for the frontend.

## Supported Providers

We currently support the following data providers, each specialized for different market segments and data types:

| Provider | Focus | Key Data Points | Documentation |
|----------|-------|-----------------|---------------|
| **NSE India** | Indian Equities | Deliverables, VIX, FII/DII, Market Movers | [NSE View](./nse.md) |
| **yfinance** | Global Equities | OHLCV History, Splits, Dividends | [yfinance View](./yfinance.md) |

## Standardized Pipeline

All FolioPP providers follow a standardized data flow defined in `foliopp_core`:

1.  **`QueryParams`**: Validates the incoming query (e.g., symbol, dates).
2.  **`Extract`**: Fetches raw data from the provider's API/library.
3.  **`Transform`**: Maps raw data to a **FolioPP Standard Model**.
4.  **`Model Validation`**: Ensures data integrity before reaching the UI.
