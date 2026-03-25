"""Indian Equity Balance Sheet Standard Model."""

from datetime import date as dateType
from typing import Literal

from pydantic import Field, field_validator

from foliopp_core.provider.abstract.data import Data
from foliopp_core.provider.abstract.query_params import QueryParams


class BalanceSheetQueryParams(QueryParams):
    symbol: str = Field(description="NSE/BSE ticker symbol")
    period: Literal["annual", "quarter"] = Field(default="annual")
    limit: int = Field(default=4, le=15)
    exchange: Literal["NSE", "BSE"] = Field(default="NSE")

    @field_validator("symbol", mode="before")
    @classmethod
    def to_upper(cls, v: str) -> str:
        return v.upper().strip()


class BalanceSheetData(Data):
    """All values in INR."""

    period_ending: dateType = Field(description="End date of the reporting period")
    # Cash & equivalents
    cash_and_cash_equivalents: float | None = Field(default=None)
    cash_equivalents: float | None = Field(default=None)
    cash_financial: float | None = Field(default=None)
    cash_cash_equivalents_and_federal_funds_sold: float | None = Field(default=None)
    # Receivables & current assets
    receivables: float | None = Field(default=None)
    prepaid_assets: float | None = Field(default=None)
    # Investments
    investments_and_advances: float | None = Field(default=None)
    investment_in_financial_assets: float | None = Field(default=None)
    available_for_sale_securities: float | None = Field(default=None)
    long_term_equity_investment: float | None = Field(default=None)
    investments_in_associates_at_cost: float | None = Field(default=None)
    investments_in_subsidiaries_at_cost: float | None = Field(default=None)
    # Fixed assets
    gross_ppe: float | None = Field(default=None)
    accumulated_depreciation: float | None = Field(default=None)
    net_ppe: float | None = Field(default=None)
    construction_in_progress: float | None = Field(default=None)
    properties: float | None = Field(default=None)
    other_properties: float | None = Field(default=None)
    # Intangibles
    goodwill: float | None = Field(default=None)
    goodwill_and_other_intangible_assets: float | None = Field(default=None)
    # Total assets
    total_assets: float | None = Field(default=None)
    # Liabilities
    accounts_payable: float | None = Field(default=None)
    payables: float | None = Field(default=None)
    derivative_product_liabilities: float | None = Field(default=None)
    long_term_debt_and_capital_lease_obligation: float | None = Field(default=None)
    total_liabilities_net_minority_interest: float | None = Field(default=None)
    # Equity
    common_stock: float | None = Field(default=None)
    capital_stock: float | None = Field(default=None)
    additional_paid_in_capital: float | None = Field(default=None)
    retained_earnings: float | None = Field(default=None)
    fixed_assets_revaluation_reserve: float | None = Field(default=None)
    stockholders_equity: float | None = Field(default=None)
    minority_interest: float | None = Field(default=None)
    total_equity_gross_minority_interest: float | None = Field(default=None)
    # Summary
    total_capitalization: float | None = Field(default=None)
    common_stock_equity: float | None = Field(default=None)
    net_tangible_assets: float | None = Field(default=None)
    invested_capital: float | None = Field(default=None)
    tangible_book_value: float | None = Field(default=None)
    total_debt: float | None = Field(default=None)
    net_debt: float | None = Field(default=None)
    # Share counts
    share_issued: float | None = Field(default=None)
    ordinary_shares_number: float | None = Field(default=None)
    treasury_shares_number: float | None = Field(default=None)
