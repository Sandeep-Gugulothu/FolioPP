"""YFinance Income Statement Model."""

from datetime import datetime
from typing import Any, Literal

from pydantic import Field, field_validator

from foliopp_core.provider.abstract.fetcher import Fetcher
from foliopp_core.provider.standard_models.income_statement import (
    IncomeStatementData,
    IncomeStatementQueryParams,
)


class YFinanceIncomeStatementQueryParams(IncomeStatementQueryParams):
    """YFinance-specific query params for income statement."""

    exchange: Literal["NSE", "BSE"] = Field(default="NSE", description="NSE or BSE")


class YFinanceIncomeStatementData(IncomeStatementData):
    """YFinance income statement data."""

    @field_validator("period_ending", mode="before")
    @classmethod
    def parse_date(cls, v):
        if isinstance(v, str):
            return datetime.strptime(v.split(" ")[0], "%Y-%m-%d").date()
        return v


# Maps yfinance PascalCase -> our standard field names (all fields yfinance returns)
_FIELD_MAP = {
    "Total Revenue": "total_revenue",
    "Operating Revenue": "operating_revenue",
    "Net Interest Income": "net_interest_income",
    "Interest Income": "interest_income",
    "Interest Expense": "interest_expense",
    "Operating Expense": "operating_expense",
    "Other Operating Expenses": "other_operating_expenses",
    "Selling General And Administration": "sga_expense",
    "Selling And Marketing Expense": "selling_marketing_expense",
    "General And Administrative Expense": "general_admin_expense",
    "Insurance And Claims": "insurance_and_claims",
    "Rent And Landing Fees": "rent_and_landing_fees",
    "Depreciation And Amortization In Income Statement": "depreciation_amortization",
    "Depreciation Income Statement": "depreciation",
    "Reconciled Depreciation": "reconciled_depreciation",
    "Pretax Income": "pretax_income",
    "Tax Provision": "tax_provision",
    "Tax Rate For Calcs": "tax_rate",
    "Tax Effect Of Unusual Items": "tax_effect_unusual_items",
    "Net Income": "net_income",
    "Net Income Common Stockholders": "net_income_common",
    "Net Income Including Noncontrolling Interests": "net_income_incl_minority",
    "Net Income Continuous Operations": "net_income_continuous_ops",
    "Net Income From Continuing Operation Net Minority Interest": "net_income_continuing_net_minority",
    "Net Income From Continuing And Discontinued Operation": "net_income_continuing_discontinued",
    "Net Income Extraordinary": "net_income_extraordinary",
    "Minority Interests": "minority_interests",
    "Normalized Income": "normalized_income",
    "Diluted NI Availto Com Stockholders": "diluted_ni_avail_to_com",
    "Special Income Charges": "special_income_charges",
    "Other Special Charges": "other_special_charges",
    "Gain On Sale Of Security": "gain_on_sale_of_security",
    "Total Unusual Items": "total_unusual_items",
    "Total Unusual Items Excluding Goodwill": "total_unusual_items_ex_goodwill",
    "Basic EPS": "basic_eps",
    "Diluted EPS": "diluted_eps",
    "Basic Average Shares": "basic_shares",
    "Diluted Average Shares": "diluted_shares",
}


class YFinanceIncomeStatementFetcher(
    Fetcher[YFinanceIncomeStatementQueryParams, list[YFinanceIncomeStatementData]]
):
    """YFinance Income Statement Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> YFinanceIncomeStatementQueryParams:
        return YFinanceIncomeStatementQueryParams(**params)

    @staticmethod
    def extract_data(
        query: YFinanceIncomeStatementQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        import json
        from numpy import nan
        from yfinance import Ticker
        from foliopp_yfinance.utils.helpers import build_yf_symbol
        from foliopp_core.provider.utils.errors import EmptyDataError

        symbol = build_yf_symbol(query.symbol, query.exchange)
        ticker = Ticker(symbol)
        raw = ticker.quarterly_income_stmt if query.period == "quarter" else ticker.income_stmt
        if raw is None or raw.empty:
            raise EmptyDataError(f"No income statement data for {symbol}")

        raw = raw.iloc[:, : query.limit]
        raw = raw.replace({nan: None})
        records = [{"period_ending": str(col.date()), **raw[col].to_dict()} for col in raw.columns]
        return json.loads(json.dumps(records, default=str))

    @staticmethod
    def transform_data(
        query: YFinanceIncomeStatementQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[YFinanceIncomeStatementData]:
        results = []
        for record in data:
            mapped = {"period_ending": record["period_ending"]}
            for yf_key, std_key in _FIELD_MAP.items():
                val = record.get(yf_key)
                if val is not None:
                    mapped[std_key] = val
            results.append(YFinanceIncomeStatementData.model_validate(mapped))
        return results
