import asyncio
from datetime import date, datetime, timedelta
from typing import Any

from foliopp_core.provider.abstract.fetcher import Fetcher
from foliopp_core.provider.standard_models.nse_models import (
    CorporateAnnouncementData, CorporateAnnouncementQueryParams,
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
    for fmt in ("%d-%b-%Y", "%Y-%m-%d", "%d-%m-%Y", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(str(v).strip(), fmt)
        except ValueError:
            continue
    return None

class NSECorporateAnnouncementFetcher(
    Fetcher[CorporateAnnouncementQueryParams, list[CorporateAnnouncementData]]
):
    @staticmethod
    def transform_query(params: dict[str, Any]) -> CorporateAnnouncementQueryParams:
        return CorporateAnnouncementQueryParams(**params)

    @staticmethod
    def extract_data(query, credentials=None, **kwargs) -> list[dict]:
        from foliopp_nse.utils.helpers import nse_fetch, to_nse_date, NSE_BASE, nse_json
        from foliopp_core.provider.utils.errors import EmptyDataError

        from_date, to_date = _resolve_dates(query)
        origin = f"{NSE_BASE}/companies-listing/corporate-filings-announcements"
        url = f"{NSE_BASE}/api/corporate-announcements"
        params = {
            "index": "equities",
            "from_date": to_nse_date(from_date),
            "to_date": to_nse_date(to_date),
        }
        if query.symbol:
            params["symbol"] = query.symbol

        resp = nse_fetch(url, origin=origin, params=params)
        if resp.status_code != 200:
            raise EmptyDataError("No corporate announcements data")
        
        data = nse_json(resp)
        return data

    @staticmethod
    def transform_data(query, data: list[dict], **kwargs) -> list[CorporateAnnouncementData]:
        results = []
        for row in data:
            try:
                results.append(CorporateAnnouncementData.model_validate({
                    "symbol": row.get("symbol", ""),
                    "company_name": row.get("sm_name"),
                    "subject": row.get("attchmntText") or row.get("subject"),
                    "details": row.get("desc") or row.get("details"),
                    "broadcast_date": _parse_date(row.get("an_dt")),
                    "attainment_date": _parse_date(row.get("attchmntBindngDt")),
                    "attachment_link": row.get("attchmntFile") or row.get("attachment"),
                }))
            except Exception:
                continue
        return results
