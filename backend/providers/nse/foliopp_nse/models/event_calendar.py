"""NSE Event Calendar Model."""

from datetime import date, datetime, timedelta
from typing import Any

from foliopp_core.provider.abstract.fetcher import Fetcher
from foliopp_core.provider.standard_models.nse_models import (
    EventCalendarData, EventCalendarQueryParams,
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


class NSEEventCalendarFetcher(
    Fetcher[EventCalendarQueryParams, list[EventCalendarData]]
):
    @staticmethod
    def transform_query(params: dict[str, Any]) -> EventCalendarQueryParams:
        return EventCalendarQueryParams(**params)

    @staticmethod
    def extract_data(query, credentials=None, **kwargs) -> list[dict]:
        from foliopp_nse.utils.helpers import nse_fetch, to_nse_date, NSE_BASE
        from foliopp_core.provider.utils.errors import EmptyDataError

        from_date, to_date = _resolve_dates(query)
        origin = f"{NSE_BASE}/companies-listing/corporate-filings-event-calendar"
        url = f"{NSE_BASE}/api/event-calendar"
        params = {
            "index": "equities",
            "from_date": to_nse_date(from_date),
            "to_date": to_nse_date(to_date),
        }
        if query.fno_only:
            params["fo_sec"] = "true"

        resp = nse_fetch(url, origin=origin, params=params)
        if resp.status_code != 200:
            raise EmptyDataError("No event calendar data")
        from foliopp_nse.utils.helpers import nse_json
        data = nse_json(resp)
        if query.symbol:
            data = [r for r in data if r.get("symbol", "").upper() == query.symbol]
        return data

    @staticmethod
    def transform_data(query, data: list[dict], **kwargs) -> list[EventCalendarData]:
        results = []
        for row in data:
            try:
                results.append(EventCalendarData.model_validate({
                    "symbol": row.get("symbol", ""),
                    "company_name": row.get("companyName") or row.get("comp"),
                    "purpose": row.get("purpose") or row.get("subject"),
                    "date": _parse_date(row.get("date") or row.get("bm_date")),
                    "description": row.get("description") or row.get("details"),
                }))
            except Exception:
                continue
        return results
