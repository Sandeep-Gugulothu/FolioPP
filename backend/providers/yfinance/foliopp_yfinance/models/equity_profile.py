"""YFinance Equity Profile Model."""

from typing import Any, Literal

from pydantic import Field

from foliopp_core.provider.abstract.fetcher import Fetcher
from foliopp_core.provider.standard_models.equity_profile import (
    EquityProfileData,
    EquityProfileQueryParams,
)


class YFinanceEquityProfileQueryParams(EquityProfileQueryParams):
    """YFinance-specific query params for equity profile."""

    exchange: Literal["NSE", "BSE", "NASDAQ", "NYSE"] = Field(default="NSE", description="NSE, BSE, NASDAQ or NYSE")


class YFinanceEquityProfileData(EquityProfileData):
    """YFinance equity profile data - no extra fields beyond standard."""


class YFinanceEquityProfileFetcher(
    Fetcher[YFinanceEquityProfileQueryParams, list[YFinanceEquityProfileData]]
):
    """YFinance Equity Profile Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> YFinanceEquityProfileQueryParams:
        return YFinanceEquityProfileQueryParams(**params)

    @staticmethod
    def extract_data(
        query: YFinanceEquityProfileQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        from foliopp_yfinance.utils.helpers import yf_get_profile
        return [yf_get_profile(query.symbol, query.exchange)]

    @staticmethod
    def transform_data(
        query: YFinanceEquityProfileQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[YFinanceEquityProfileData]:
        return [YFinanceEquityProfileData.model_validate(d) for d in data]
