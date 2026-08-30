"""YFinance Company News Model -  Equities.
- Multi-symbol support via comma-separated symbols
- aextract_data (async) with asyncio.gather for concurrent fetching
- _normalize_news_item helper to flatten yfinance's nested content dict
- NSE/BSE exchange suffix via build_yf_symbol
"""

# pylint: disable=unused-argument

from typing import Any, Literal

from pydantic import Field, field_validator

from foliopp_core.provider.abstract.fetcher import Fetcher
from foliopp_core.provider.standard_models.company_news import (
    CompanyNewsData,
    CompanyNewsQueryParams,
)


class YFinanceCompanyNewsQueryParams(CompanyNewsQueryParams):
    """YFinance Company News Query.

    Source: https://finance.yahoo.com/news/
    """

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}

    exchange: Literal["NSE", "BSE"] = Field(default="NSE", description="NSE or BSE")

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def _symbol_mandatory(cls, v):
        """Symbol mandatory validator."""
        if not v:
            raise ValueError("Required field missing -> symbol")
        return v


class YFinanceCompanyNewsData(CompanyNewsData):
    """YFinance Company News Data."""

    source: str | None = Field(default=None, description="Source of the news article.")


class YFinanceCompanyNewsFetcher(
    Fetcher[
        YFinanceCompanyNewsQueryParams,
        list[YFinanceCompanyNewsData],
    ]
):
    """Transform the query, extract and transform the data from the Yahoo Finance endpoints."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> YFinanceCompanyNewsQueryParams:
        """Transform query params."""
        return YFinanceCompanyNewsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: YFinanceCompanyNewsQueryParams,
        credentials=None,
        **kwargs,
    ) -> list[dict]:
        """Extract the raw data from YFinance and normalize to CompanyNewsData schema."""
        # pylint: disable=import-outside-toplevel
        import asyncio
        from warnings import warn

        from yfinance import Ticker

        from foliopp_core.provider.utils.errors import EmptyDataError
        from foliopp_yfinance.utils.helpers import build_yf_symbol

        symbols = [s.strip() for s in query.symbol.split(",") if s.strip()]
        results: list[dict] = []

        def _normalize_news_item(item: dict, sym: str) -> dict | None:
            """Flatten the yfinance nested content response."""
            if not isinstance(item, dict):
                return None

            content = item.get("content")
            if not isinstance(content, dict):
                return None

            title = content.get("title") or content.get("summary")

            # Prefer clickThroughUrl; fallback to canonicalUrl; fallback to previewUrl
            url = None
            ctu = content.get("clickThroughUrl")
            if isinstance(ctu, dict):
                url = ctu.get("url")
            if not url:
                can = content.get("canonicalUrl")
                if isinstance(can, dict):
                    url = can.get("url")
            if not url:
                url = content.get("previewUrl")

            date = content.get("pubDate") or content.get("displayTime")

            provider = content.get("provider")
            source = provider.get("displayName") if isinstance(provider, dict) else None
            body = content.get("body") or content.get("summary") or content.get("description") or ""
            excerpt = content.get("summary") or content.get("description") or ""
            author = content.get("byline") or content.get("author")
            images = content.get("thumbnail") or content.get("images")

            if not (sym and title and url and date):
                return None

            normalized: dict[str, Any] = {
                "symbols": sym,
                "title": title,
                "url": url,
                "date": date,
                "source": source,
                "author": author,
                "images": images,
            }
            if body:
                normalized["body"] = body
            if excerpt:
                normalized["excerpt"] = excerpt

            return normalized

        def _fetch_news(sym: str) -> list[dict]:
            """Fetch news for one symbol in a worker thread."""
            yf_symbol = build_yf_symbol(sym, query.exchange)
            raw = Ticker(yf_symbol).get_news() or []
            out: list[dict] = []
            for item in raw:
                norm = _normalize_news_item(item, sym)
                if norm:
                    out.append(norm)
            return out

        async def get_one(sym: str) -> None:
            """Get news for one ticker symbol."""
            try:
                items = await asyncio.to_thread(_fetch_news, sym)
            except Exception as e:
                warn(f"Error getting news for {sym}: {e}")
                return
            if items:
                results.extend(items)

        await asyncio.gather(*(get_one(sym) for sym in symbols))

        if not results:
            raise EmptyDataError("No data was returned for the given symbol(s)")

        return results

    @staticmethod
    def transform_data(
        query: YFinanceCompanyNewsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[YFinanceCompanyNewsData]:
        """Transform data."""
        return [YFinanceCompanyNewsData.model_validate(d) for d in data]
