"""NSE Corporate Actions Model."""

from datetime import date, datetime, timedelta
from typing import Any

from pydantic import field_validator

from foliopp_core.provider.abstract.fetcher import Fetcher
from foliopp_core.provider.standard_models.nse_models import (
    CorporateActionData, CorporateActionQueryParams,
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
    if isinstance(v, date):
        return v
    for fmt in ("%d-%b-%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(str(v).strip(), fmt).date()
        except ValueError:
            continue
    return None


class NSECorporateActionData(CorporateActionData):
    pass


class NSECorporateActionFetcher(
    Fetcher[CorporateActionQueryParams, list[NSECorporateActionData]]
):
    @staticmethod
    def transform_query(params: dict[str, Any]) -> CorporateActionQueryParams:
        return CorporateActionQueryParams(**params)

    @staticmethod
    def extract_data(query, credentials=None, **kwargs) -> list[dict]:
        from foliopp_nse.utils.helpers import nse_fetch, to_nse_date, NSE_BASE
        from foliopp_core.provider.utils.errors import EmptyDataError

        from_date, to_date = _resolve_dates(query)
        origin = f"{NSE_BASE}/companies-listing/corporate-filings-actions"
        url = f"{NSE_BASE}/api/corporates-corporateactions"
        params = {
            "index": "equities",
            "from_date": to_nse_date(from_date),
            "to_date": to_nse_date(to_date),
        }
        if query.fno_only:
            params["fo_sec"] = "true"

        resp = nse_fetch(url, origin=origin, params=params)
        if resp.status_code != 200:
            raise EmptyDataError("No corporate actions data")
        from foliopp_nse.utils.helpers import nse_json
        data = nse_json(resp)
        if query.symbol:
            data = [r for r in data if r.get("symbol", "").upper() == query.symbol]
        return data

    @staticmethod
    def transform_data(query, data: list[dict], **kwargs) -> list[NSECorporateActionData]:
        results = []
        for row in data:
            try:
                results.append(NSECorporateActionData.model_validate({
                    "symbol": row.get("symbol", ""),
                    "company_name": row.get("comp") or row.get("companyName"),
                    "series": row.get("series"),
                    "face_value": row.get("faceVal"),
                    "purpose": row.get("subject") or row.get("purpose"),
                    "ex_date": _parse_date(row.get("exDate")),
                    "record_date": _parse_date(row.get("recDate")),
                    "bc_start_date": _parse_date(row.get("bcStartDate")),
                    "bc_end_date": _parse_date(row.get("bcEndDate")),
                }))
            except Exception:
                continue
        return results
