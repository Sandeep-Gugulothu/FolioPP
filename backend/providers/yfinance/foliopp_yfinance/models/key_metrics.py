"""YFinance Key Metrics Model."""

from typing import Any

from foliopp_core.provider.abstract.fetcher import Fetcher
from foliopp_core.provider.standard_models.key_metrics import (
    KeyMetricsData,
    KeyMetricsQueryParams,
)

# yfinance info key -> our standard field name
_FIELD_MAP = {
    "marketCap": "market_cap",
    "enterpriseValue": "enterprise_value",
    "trailingPE": "pe_ratio",
    "forwardPE": "forward_pe",
    "pegRatio": "peg_ratio",
    "trailingPegRatio": "peg_ratio_ttm",
    "trailingEps": "eps_ttm",
    "forwardEps": "eps_forward",
    "bookValue": "book_value",
    "priceToBook": "price_to_book",
    "revenuePerShare": "revenue_per_share",
    "totalCashPerShare": "cash_per_share",
    "quickRatio": "quick_ratio",
    "currentRatio": "current_ratio",
    "debtToEquity": "debt_to_equity",
    "grossMargins": "gross_margin",
    "operatingMargins": "operating_margin",
    "ebitdaMargins": "ebitda_margin",
    "profitMargins": "profit_margin",
    "returnOnAssets": "return_on_assets",
    "returnOnEquity": "return_on_equity",
    "revenueGrowth": "revenue_growth",
    "earningsGrowth": "earnings_growth",
    "earningsQuarterlyGrowth": "earnings_growth_quarterly",
    "enterpriseToRevenue": "enterprise_to_revenue",
    "enterpriseToEbitda": "enterprise_to_ebitda",
    "dividendYield": "dividend_yield",
    "fiveYearAvgDividendYield": "dividend_yield_5y_avg",
    "payoutRatio": "payout_ratio",
    "beta": "beta",
    "52WeekChange": "price_return_1y",
    "overallRisk": "overall_risk",
    "auditRisk": "audit_risk",
    "boardRisk": "board_risk",
    "compensationRisk": "compensation_risk",
    "shareHolderRightsRisk": "shareholder_rights_risk",
    "financialCurrency": "currency",
}


class YFinanceKeyMetricsQueryParams(KeyMetricsQueryParams):
    pass


class YFinanceKeyMetricsData(KeyMetricsData):
    pass


class YFinanceKeyMetricsFetcher(
    Fetcher[YFinanceKeyMetricsQueryParams, list[YFinanceKeyMetricsData]]
):
    @staticmethod
    def transform_query(params: dict[str, Any]) -> YFinanceKeyMetricsQueryParams:
        return YFinanceKeyMetricsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: YFinanceKeyMetricsQueryParams,
        credentials: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> list[dict]:
        import asyncio
        from warnings import warn
        from yfinance import Ticker
        from foliopp_yfinance.utils.helpers import build_yf_symbol
        from foliopp_core.provider.utils.errors import EmptyDataError

        symbols = [s.strip() for s in query.symbol.split(",") if s.strip()]
        results = []

        async def get_one(sym: str) -> None:
            try:
                yf_sym = build_yf_symbol(sym, query.exchange)
                info = await asyncio.to_thread(lambda: Ticker(yf_sym).info)
                if not info:
                    warn(f"No data for {sym}")
                    return
                mapped = {"symbol": sym}
                for yf_key, std_key in _FIELD_MAP.items():
                    val = info.get(yf_key)
                    if val is not None:
                        mapped[std_key] = val
                results.append(mapped)
            except Exception as e:
                warn(f"Error fetching key metrics for {sym}: {e}")

        await asyncio.gather(*(get_one(sym) for sym in symbols))

        if not results:
            raise EmptyDataError("No key metrics data returned for the given symbol(s)")

        return results

    @staticmethod
    def transform_data(
        query: YFinanceKeyMetricsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[YFinanceKeyMetricsData]:
        return [YFinanceKeyMetricsData.model_validate(d) for d in data]
