"""yfinance helpers for Indian equities.

Indian tickers on yfinance use exchange suffixes:
  NSE -> RELIANCE.NS
  BSE -> RELIANCE.BO
"""

from datetime import date
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from pandas import DataFrame

EXCHANGE_SUFFIX = {"NSE": ".NS", "BSE": ".BO", "NASDAQ": "", "NYSE": ""}

# yfinance raw column names -> our standard field names
# Done here so extract_data always returns clean columns regardless of interval
COLUMN_MAP = {
    "Date": "date",       # daily data
    "Datetime": "date",   # intraday data
    "Open": "open",
    "High": "high",
    "Low": "low",
    "Close": "close",
    "Adj Close": "adj_close",
    "Volume": "volume",
    "Dividends": "dividend",
    "Stock Splits": "split_ratio",
}


def build_yf_symbol(symbol: str, exchange: Literal["NSE", "BSE", "NASDAQ", "NYSE"]) -> str:
    """Append .NS or .BO suffix, or return as is for US exchanges."""
    suffix = EXCHANGE_SUFFIX.get(exchange, "")
    if not suffix:
        return symbol
    return symbol if symbol.endswith(suffix) else f"{symbol}{suffix}"


def yf_download(
    symbol: str,
    exchange: Literal["NSE", "BSE", "NASDAQ", "NYSE"] = "NSE",
    start_date: date | str | None = None,
    end_date: date | str | None = None,
    interval: str = "1d",
    actions: bool = True,
    progress: bool = False,
    ignore_tz: bool = True,
    auto_adjust: bool = False,
) -> "DataFrame":
    """Download OHLCV from yfinance and return clean standardized columns.

    Column renaming happens here so extract_data always returns consistent
    lowercase field names regardless of what yfinance internally uses.
    """
    import yfinance as yf

    yf_symbol = build_yf_symbol(symbol, exchange)

    data = yf.download(
        tickers=yf_symbol,
        start=str(start_date) if start_date else None,
        end=str(end_date) if end_date else None,
        interval=interval,
        actions=actions,
        progress=progress,
        ignore_tz=ignore_tz,
        auto_adjust=auto_adjust,
    )

    if data.empty:
        from foliopp_core.provider.utils.errors import EmptyDataError
        raise EmptyDataError(f"No data from yfinance for {yf_symbol}")

    # Flatten MultiIndex columns yfinance sometimes produces
    if hasattr(data.columns, "levels"):
        data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]

    data = data.reset_index()

    # Rename to our standard field names - extract_data returns clean columns from here
    data = data.rename(columns=COLUMN_MAP)

    # Drop adj_close - we use close as canonical price
    if "adj_close" in data.columns:
        data = data.drop(columns=["adj_close"])

    # Drop zero-value action columns (no splits/dividends on most days)
    for col in ["dividend", "split_ratio"]:
        if col in data.columns and data[col].sum() == 0:
            data = data.drop(columns=[col])

    return data


def yf_get_info(symbol: str, exchange: Literal["NSE", "BSE", "NASDAQ", "NYSE"] = "NSE") -> dict:
    """Fetch raw ticker info dict from yfinance for a live quote."""
    import yfinance as yf

    yf_symbol = build_yf_symbol(symbol, exchange)
    info = yf.Ticker(yf_symbol).info

    if not info or not info.get("regularMarketPrice"):
        from foliopp_core.provider.utils.errors import EmptyDataError
        raise EmptyDataError(f"No quote data from yfinance for {yf_symbol}")

    return info


PROFILE_FIELDS = [
    "symbol", "longName", "exchange", "currency", "sector", "industry",
    "country", "city", "address1", "zip", "phone", "website",
    "longBusinessSummary", "fullTimeEmployees", "marketCap",
    "sharesOutstanding", "floatShares", "yield", "beta",
    "firstTradeDateEpochUtc",
]


def yf_get_profile(symbol: str, exchange: Literal["NSE", "BSE", "NASDAQ", "NYSE"] = "NSE") -> dict:
    """Fetch company profile fields from yfinance info dict."""
    import yfinance as yf
    from datetime import timezone
    from datetime import datetime

    yf_symbol = build_yf_symbol(symbol, exchange)
    info = yf.Ticker(yf_symbol).info

    if not info or not info.get("longName"):
        from foliopp_core.provider.utils.errors import EmptyDataError
        raise EmptyDataError(f"No profile data from yfinance for {yf_symbol}")

    result = {"symbol": symbol, "exchange": exchange}
    field_map = {
        "longName": "name",
        "address1": "address",
        "zip": "zip_code",
        "longBusinessSummary": "description",
        "fullTimeEmployees": "employees",
        "marketCap": "market_cap",
        "sharesOutstanding": "shares_outstanding",
        "floatShares": "shares_float",
        "yield": "dividend_yield",
    }
    passthrough = ["currency", "sector", "industry", "country", "city", "phone", "website", "beta"]

    for raw, clean in field_map.items():
        val = info.get(raw)
        if val is not None and val != "N/A":
            result[clean] = val
    for field in passthrough:
        val = info.get(field)
        if val is not None and val != "N/A":
            result[field] = val

    epoch = info.get("firstTradeDateEpochUtc")
    if epoch:
        result["first_trade_date"] = datetime.fromtimestamp(epoch, tz=timezone.utc).date()

    return result
