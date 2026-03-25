"""yfinance Indian Equity Quote Model."""

from typing import Any

from foliopp_core.provider.abstract.fetcher import Fetcher
from foliopp_core.provider.standard_models.equity_quote import (
    EquityQuoteData,
    EquityQuoteQueryParams,
)


class YFinanceEquityQuoteQueryParams(EquityQuoteQueryParams):
    """yfinance quote query params. No extra fields needed beyond standard."""


class YFinanceEquityQuoteData(EquityQuoteData):
    """yfinance quote output. Same as standard for now."""


class YFinanceEquityQuoteFetcher(
    Fetcher[
        YFinanceEquityQuoteQueryParams,
        YFinanceEquityQuoteData,
    ]
):
    """Fetches live Indian equity quote from yfinance."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> YFinanceEquityQuoteQueryParams:
        return YFinanceEquityQuoteQueryParams(**params)

    @staticmethod
    def extract_data(
        query: YFinanceEquityQuoteQueryParams,
        credentials: dict[str, str] | None = None,
        **kwargs,
    ) -> dict:
        """Fetch raw info dict from yfinance."""
        from foliopp_yfinance.utils.helpers import yf_get_info

        return yf_get_info(symbol=query.symbol, exchange=query.exchange)

    @staticmethod
    def transform_data(
        query: YFinanceEquityQuoteQueryParams,
        data: dict,
        **kwargs,
    ) -> YFinanceEquityQuoteData:
        """Map yfinance info dict → YFinanceEquityQuoteData.

        yfinance keys:  regularMarketPrice, regularMarketOpen, regularMarketDayHigh,
                        regularMarketDayLow, regularMarketPreviousClose,
                        regularMarketVolume, regularMarketChange,
                        regularMarketChangePercent, marketCap, shortName
        we produce:     price, open, high, low, prev_close, volume,
                        change, change_pct, market_cap, name, symbol, exchange, currency
        """
        return YFinanceEquityQuoteData.model_validate({
            "symbol": query.symbol,
            "name": data.get("shortName") or data.get("longName"),
            "price": data.get("regularMarketPrice") or data.get("currentPrice"),
            "open": data.get("regularMarketOpen"),
            "high": data.get("regularMarketDayHigh"),
            "low": data.get("regularMarketDayLow"),
            "prev_close": data.get("regularMarketPreviousClose"),
            "change": data.get("regularMarketChange"),
            "change_pct": data.get("regularMarketChangePercent"),
            "volume": data.get("regularMarketVolume"),
            "market_cap": data.get("marketCap"),
            "exchange": query.exchange,
            "currency": "INR",
        })
