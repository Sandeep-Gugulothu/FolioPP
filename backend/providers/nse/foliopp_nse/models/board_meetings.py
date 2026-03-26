import asyncio
from datetime import date, datetime, timedelta
from typing import Any

from foliopp_core.provider.abstract.fetcher import Fetcher
from foliopp_core.provider.standard_models.nse_models import (
    BoardMeetingData, BoardMeetingQueryParams,
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

class NSEBoardMeetingFetcher(
    Fetcher[BoardMeetingQueryParams, list[BoardMeetingData]]
):
    @staticmethod
    def transform_query(params: dict[str, Any]) -> BoardMeetingQueryParams:
        return BoardMeetingQueryParams(**params)

    @staticmethod
    def extract_data(query, credentials=None, **kwargs) -> list[dict]:
        from foliopp_nse.utils.helpers import nse_fetch, to_nse_date, NSE_BASE, nse_json
        from foliopp_core.provider.utils.errors import EmptyDataError

        from_date, to_date = _resolve_dates(query)
        origin = f"{NSE_BASE}/companies-listing/corporate-filings-board-meetings"
        url = f"{NSE_BASE}/api/corporate-board-meetings"
        params = {
            "index": "equities",
            "from_date": to_nse_date(from_date),
            "to_date": to_nse_date(to_date),
        }
        if query.symbol:
            params["symbol"] = query.symbol

        resp = nse_fetch(url, origin=origin, params=params)
        if resp.status_code != 200:
            raise EmptyDataError("No board meetings data")
        
        data = nse_json(resp)
        return data

    @staticmethod
    def transform_data(query, data: list[dict], **kwargs) -> list[BoardMeetingData]:
        results = []
        for row in data:
            try:
                results.append(BoardMeetingData.model_validate({
                    "symbol": row.get("bm_symbol") or row.get("symbol", ""),
                    "company_name": row.get("sm_name"),
                    "bm_date": _parse_date(row.get("bm_date")),
                    "purpose": row.get("bm_purpose"),
                    "details": row.get("bm_desc"),
                }))
            except Exception:
                continue
        return results
