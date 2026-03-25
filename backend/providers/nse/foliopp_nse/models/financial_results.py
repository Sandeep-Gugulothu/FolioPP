"""NSE Financial Results for Equity Model."""

from datetime import date, datetime, timedelta
from typing import Any

from foliopp_core.provider.abstract.fetcher import Fetcher
from foliopp_core.provider.standard_models.nse_models import (
    FinancialResultData, FinancialResultQueryParams,
)


def _resolve_dates(query) -> tuple[date, date]:
    if query.from_date and query.to_date:
        return query.from_date, query.to_date
    today = date.today()
    period_map = {"1D": 1, "1W": 7, "1M": 30, "3M": 90, "6M": 180, "1Y": 365}
    delta = period_map.get(query.period or "1M", 30)
    return today - timedelta(days=delta), today


def _parse_date(v):
    if not v or v in ("-", ""):
        return None
    for fmt in ("%d-%b-%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(str(v).strip(), fmt).date()
        except ValueError:
            continue
    return None


def _safe_float(v) -> float | None:
    if v is None or str(v).strip() in ("-", "", "None"):
        return None
    try:
        return float(str(v).replace(",", "").strip())
    except (ValueError, TypeError):
        return None


class NSEFinancialResultFetcher(Fetcher[FinancialResultQueryParams, list[FinancialResultData]]):
    @staticmethod
    def transform_query(params: dict[str, Any]) -> FinancialResultQueryParams:
        return FinancialResultQueryParams(**params)

    @staticmethod
    def extract_data(query, credentials=None, **kwargs) -> list[dict]:
        from foliopp_nse.utils.helpers import nse_fetch, nse_json, to_nse_date, NSE_BASE
        from foliopp_core.provider.utils.errors import EmptyDataError

        from_date, to_date = _resolve_dates(query)
        url = f"{NSE_BASE}/api/corporates-financial-results"
        origin = f"{NSE_BASE}/companies-listing/corporate-filings-financial-results"
        params = {
            "index": "equities",
            "period": query.fin_period,
            "from_date": to_nse_date(from_date),
            "to_date": to_nse_date(to_date),
        }
        if query.fno_only:
            params["fo_sec"] = "true"

        resp = nse_fetch(url, origin=origin, params=params)
        if resp.status_code != 200:
            raise EmptyDataError("No financial results data")
        data = nse_json(resp)
        return data if isinstance(data, list) else data.get("data", [])

    @staticmethod
    def transform_data(query, data: list[dict], **kwargs) -> list[FinancialResultData]:
        results = []
        for row in data:
            try:
                results.append(FinancialResultData.model_validate({
                    "symbol": row.get("symbol", ""),
                    "company_name": row.get("companyName") or row.get("comp"),
                    "series": row.get("series"),
                    "fin_period": row.get("period") or row.get("finPeriod"),
                    "from_date": _parse_date(row.get("fromDate")),
                    "to_date": _parse_date(row.get("toDate")),
                    "expenditure": _safe_float(row.get("expenditure") or row.get("totalExpenditure")),
                    "income": _safe_float(row.get("income") or row.get("totalIncome")),
                    "profit_before_tax": _safe_float(row.get("profitBeforeTax") or row.get("pbt")),
                    "profit_after_tax": _safe_float(row.get("profitAfterTax") or row.get("pat")),
                    "eps": _safe_float(row.get("eps") or row.get("dilutedEps")),
                    "broadcast_date": _parse_date(row.get("broadcastDate") or row.get("brdDt")),
                    "xbrl_link": row.get("xbrl") or row.get("xbrlLink"),
                }))
            except Exception:
                continue
        return results
