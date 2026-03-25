"""YFinance Balance Sheet Model."""

import re
from datetime import datetime
from typing import Any, Literal

from pydantic import Field, field_validator

from foliopp_core.provider.abstract.fetcher import Fetcher
from foliopp_core.provider.standard_models.balance_sheet import (
    BalanceSheetData,
    BalanceSheetQueryParams,
)


def _to_snake(s: str) -> str:
    s = re.sub(r'(?<=[a-z0-9])(?=[A-Z])', '_', s)
    s = re.sub(r'\s+', '_', s)
    return s.lower()


class YFinanceBalanceSheetQueryParams(BalanceSheetQueryParams):
    exchange: Literal["NSE", "BSE"] = Field(default="NSE")


class YFinanceBalanceSheetData(BalanceSheetData):
    @field_validator("period_ending", mode="before")
    @classmethod
    def parse_date(cls, v):
        if isinstance(v, str):
            return datetime.strptime(v.split(" ")[0], "%Y-%m-%d").date()
        return v


class YFinanceBalanceSheetFetcher(
    Fetcher[YFinanceBalanceSheetQueryParams, list[YFinanceBalanceSheetData]]
):
    @staticmethod
    def transform_query(params: dict[str, Any]) -> YFinanceBalanceSheetQueryParams:
        return YFinanceBalanceSheetQueryParams(**params)

    @staticmethod
    def extract_data(
        query: YFinanceBalanceSheetQueryParams,
        credentials: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> list[dict]:
        import json
        from numpy import nan
        from yfinance import Ticker
        from foliopp_yfinance.utils.helpers import build_yf_symbol
        from foliopp_core.provider.utils.errors import EmptyDataError

        symbol = build_yf_symbol(query.symbol, query.exchange)
        ticker = Ticker(symbol)
        raw = ticker.quarterly_balance_sheet if query.period == "quarter" else ticker.balance_sheet

        if raw is None or raw.empty:
            raise EmptyDataError(f"No balance sheet data for {symbol}")

        raw = raw.iloc[:, : query.limit]
        raw = raw.replace({nan: None})
        records = [{"period_ending": str(col.date()), **raw[col].to_dict()} for col in raw.columns]
        return json.loads(json.dumps(records, default=str))

    @staticmethod
    def transform_data(
        query: YFinanceBalanceSheetQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[YFinanceBalanceSheetData]:
        results = []
        for record in data:
            mapped = {"period_ending": record["period_ending"]}
            for raw_key, val in record.items():
                if raw_key == "period_ending" or val is None:
                    continue
                snake = _to_snake(raw_key)
                mapped[snake] = val
            results.append(YFinanceBalanceSheetData.model_validate(mapped))
        return results
