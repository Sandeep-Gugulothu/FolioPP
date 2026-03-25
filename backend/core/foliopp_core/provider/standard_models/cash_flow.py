"""Indian Equity Cash Flow Statement Standard Model."""

from datetime import date as dateType
from typing import Literal

from pydantic import Field, field_validator

from foliopp_core.provider.abstract.data import Data
from foliopp_core.provider.abstract.query_params import QueryParams


class CashFlowQueryParams(QueryParams):
    symbol: str = Field(description="NSE/BSE ticker symbol")
    period: Literal["annual", "quarter"] = Field(default="annual")
    limit: int = Field(default=4, le=15)
    exchange: Literal["NSE", "BSE"] = Field(default="NSE")

    @field_validator("symbol", mode="before")
    @classmethod
    def to_upper(cls, v: str) -> str:
        return v.upper().strip()


class CashFlowData(Data):
    """All values in INR."""

    period_ending: dateType = Field(description="End date of the reporting period")
    # Operating
    operating_cash_flow: float | None = Field(default=None)
    net_income_from_continuing_operations: float | None = Field(default=None)
    depreciation_and_amortization: float | None = Field(default=None)
    depreciation: float | None = Field(default=None)
    gain_loss_on_investment_securities: float | None = Field(default=None)
    gain_loss_on_sale_of_ppe: float | None = Field(default=None)
    gain_loss_on_sale_of_business: float | None = Field(default=None)
    provision_and_write_off_of_assets: float | None = Field(default=None)
    other_non_cash_items: float | None = Field(default=None)
    change_in_working_capital: float | None = Field(default=None)
    change_in_other_current_assets: float | None = Field(default=None)
    change_in_other_current_liabilities: float | None = Field(default=None)
    taxes_refund_paid: float | None = Field(default=None)
    # Investing
    investing_cash_flow: float | None = Field(default=None)
    capital_expenditure: float | None = Field(default=None)
    purchase_of_ppe: float | None = Field(default=None)
    sale_of_ppe: float | None = Field(default=None)
    net_ppe_purchase_and_sale: float | None = Field(default=None)
    purchase_of_business: float | None = Field(default=None)
    sale_of_business: float | None = Field(default=None)
    net_business_purchase_and_sale: float | None = Field(default=None)
    net_intangibles_purchase_and_sale: float | None = Field(default=None)
    dividends_received_cfi: float | None = Field(default=None)
    # Financing
    financing_cash_flow: float | None = Field(default=None)
    long_term_debt_issuance: float | None = Field(default=None)
    long_term_debt_payments: float | None = Field(default=None)
    net_long_term_debt_issuance: float | None = Field(default=None)
    net_issuance_payments_of_debt: float | None = Field(default=None)
    issuance_of_debt: float | None = Field(default=None)
    repayment_of_debt: float | None = Field(default=None)
    common_stock_issuance: float | None = Field(default=None)
    common_stock_payments: float | None = Field(default=None)
    net_common_stock_issuance: float | None = Field(default=None)
    issuance_of_capital_stock: float | None = Field(default=None)
    repurchase_of_capital_stock: float | None = Field(default=None)
    cash_dividends_paid: float | None = Field(default=None)
    common_stock_dividend_paid: float | None = Field(default=None)
    interest_paid_cff: float | None = Field(default=None)
    net_other_financing_charges: float | None = Field(default=None)
    # Summary
    free_cash_flow: float | None = Field(default=None)
    changes_in_cash: float | None = Field(default=None)
    effect_of_exchange_rate_changes: float | None = Field(default=None)
    beginning_cash_position: float | None = Field(default=None)
    end_cash_position: float | None = Field(default=None)
