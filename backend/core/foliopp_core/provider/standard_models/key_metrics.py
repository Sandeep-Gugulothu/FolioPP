"""Indian Equity Key Metrics Standard Model."""

from pydantic import Field, field_validator

from foliopp_core.provider.abstract.data import Data
from foliopp_core.provider.abstract.query_params import QueryParams


class KeyMetricsQueryParams(QueryParams):
    symbol: str = Field(description="NSE/BSE ticker symbol")
    exchange: str = Field(default="NSE")

    @field_validator("symbol", mode="before")
    @classmethod
    def to_upper(cls, v: str) -> str:
        return v.upper().strip()


class KeyMetricsData(Data):
    symbol: str = Field(description="Ticker symbol")
    market_cap: float | None = Field(default=None)
    enterprise_value: float | None = Field(default=None)
    pe_ratio: float | None = Field(default=None, description="Trailing P/E")
    forward_pe: float | None = Field(default=None)
    peg_ratio: float | None = Field(default=None)
    peg_ratio_ttm: float | None = Field(default=None)
    eps_ttm: float | None = Field(default=None)
    eps_forward: float | None = Field(default=None)
    book_value: float | None = Field(default=None)
    price_to_book: float | None = Field(default=None)
    revenue_per_share: float | None = Field(default=None)
    cash_per_share: float | None = Field(default=None)
    quick_ratio: float | None = Field(default=None)
    current_ratio: float | None = Field(default=None)
    debt_to_equity: float | None = Field(default=None)
    gross_margin: float | None = Field(default=None)
    operating_margin: float | None = Field(default=None)
    ebitda_margin: float | None = Field(default=None)
    profit_margin: float | None = Field(default=None)
    return_on_assets: float | None = Field(default=None)
    return_on_equity: float | None = Field(default=None)
    revenue_growth: float | None = Field(default=None)
    earnings_growth: float | None = Field(default=None)
    earnings_growth_quarterly: float | None = Field(default=None)
    enterprise_to_revenue: float | None = Field(default=None)
    enterprise_to_ebitda: float | None = Field(default=None)
    dividend_yield: float | None = Field(default=None)
    dividend_yield_5y_avg: float | None = Field(default=None)
    payout_ratio: float | None = Field(default=None)
    beta: float | None = Field(default=None)
    price_return_1y: float | None = Field(default=None, description="52-week price return")
    overall_risk: float | None = Field(default=None)
    audit_risk: float | None = Field(default=None)
    board_risk: float | None = Field(default=None)
    compensation_risk: float | None = Field(default=None)
    shareholder_rights_risk: float | None = Field(default=None)
    currency: str | None = Field(default=None)
