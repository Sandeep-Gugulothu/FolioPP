"""Indian Equity Income Statement Standard Model."""

from datetime import date as dateType
from typing import Literal

from pydantic import Field, field_validator

from foliopp_core.provider.abstract.data import Data
from foliopp_core.provider.abstract.query_params import QueryParams


class IncomeStatementQueryParams(QueryParams):
    """Standard query params for equity income statement."""

    symbol: str = Field(description="NSE/BSE ticker symbol e.g. RELIANCE, TCS")
    period: Literal["annual", "quarter"] = Field(default="annual", description="Reporting period")
    limit: int = Field(default=5, description="Number of periods to return (max 15)", le=15)

    @field_validator("symbol", mode="before")
    @classmethod
    def to_upper(cls, v: str) -> str:
        return v.upper().strip()


class IncomeStatementData(Data):
    """Standard output fields for equity income statement. All values in INR."""

    period_ending: dateType = Field(description="End date of the reporting period")
    # Revenue
    total_revenue: float | None = Field(default=None)
    operating_revenue: float | None = Field(default=None)
    # Interest (banks)
    net_interest_income: float | None = Field(default=None)
    interest_income: float | None = Field(default=None)
    interest_expense: float | None = Field(default=None)
    # Expenses
    operating_expense: float | None = Field(default=None)
    other_operating_expenses: float | None = Field(default=None)
    sga_expense: float | None = Field(default=None)
    selling_marketing_expense: float | None = Field(default=None)
    general_admin_expense: float | None = Field(default=None)
    insurance_and_claims: float | None = Field(default=None)
    rent_and_landing_fees: float | None = Field(default=None)
    depreciation_amortization: float | None = Field(default=None)
    depreciation: float | None = Field(default=None)
    reconciled_depreciation: float | None = Field(default=None)
    # Income
    pretax_income: float | None = Field(default=None)
    tax_provision: float | None = Field(default=None)
    tax_rate: float | None = Field(default=None)
    tax_effect_unusual_items: float | None = Field(default=None)
    net_income: float | None = Field(default=None)
    net_income_common: float | None = Field(default=None)
    net_income_incl_minority: float | None = Field(default=None)
    net_income_continuous_ops: float | None = Field(default=None)
    net_income_continuing_net_minority: float | None = Field(default=None)
    net_income_continuing_discontinued: float | None = Field(default=None)
    net_income_extraordinary: float | None = Field(default=None)
    minority_interests: float | None = Field(default=None)
    normalized_income: float | None = Field(default=None)
    diluted_ni_avail_to_com: float | None = Field(default=None)
    # Special items
    special_income_charges: float | None = Field(default=None)
    other_special_charges: float | None = Field(default=None)
    gain_on_sale_of_security: float | None = Field(default=None)
    total_unusual_items: float | None = Field(default=None)
    total_unusual_items_ex_goodwill: float | None = Field(default=None)
    # Per share
    basic_eps: float | None = Field(default=None)
    diluted_eps: float | None = Field(default=None)
    basic_shares: float | None = Field(default=None)
    diluted_shares: float | None = Field(default=None)
