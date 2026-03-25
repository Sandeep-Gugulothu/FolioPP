"""NSE India VIX Model."""

from datetime import date, datetime, timedelta
from typing import Any

from pydantic import field_validator

from foliopp_core.provider.abstract.fetcher import Fetcher
from foliopp_core.provider.standard_models.nse_models import (
    IndiaVixData, NSEDateRangeQueryParams,
)


def _resolve_dates(query) -> tuple[date, date]:
    if query.from_date and query.to_date:
        return query.from_date, query.to_date
    today = date.today()
    period_map = {"1D": 1, "1W": 7, "1M": 30, "3M": 90, "6M": 180, "1Y": 365}
    delta = period_map.get(query.period or "1M", 30)
    return today - timedelta(days=delta), today


class NSEIndiaVixData(IndiaVixData):
    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, v):
        if isinstance(v, str):
            for fmt in ("%d-%b-%Y", "%Y-%m-%d", "%d-%m-%Y"):
                try:
                    return datetime.strptime(v.strip(), fmt).date()
                except ValueError:
                    continue
        return v


class NSEIndiaVixFetcher(Fetcher[NSEDateRangeQueryParams, list[NSEIndiaVixData]]):
    @staticmethod
    def transform_query(params: dict[str, Any]) -> NSEDateRangeQueryParams:
        return NSEDateRangeQueryParams(**params)

    @staticmethod
    def extract_data(query, credentials=None, **kwargs) -> list[dict]:
        from foliopp_nse.utils.helpers import nse_fetch, to_nse_date, date_range_chunks, NSE_BASE
        from foliopp_core.provider.utils.errors import EmptyDataError

        from_date, to_date = _resolve_dates(query)
        origin = f"{NSE_BASE}/report-detail/eq_security"
        all_rows = []

        for start, end in date_range_chunks(from_date, to_date):
            url = f"{NSE_BASE}/api/historicalOR/vixhistory"
            params = {"from": to_nse_date(start), "to": to_nse_date(end), "csv": "false"}
            resp = nse_fetch(url, origin=origin, params=params)
            if resp.status_code != 200:
                continue
            try:
                from foliopp_nse.utils.helpers import nse_json
                raw_json = nse_json(resp)
                all_rows.extend(raw_json.get("data", []))
            except Exception as e:
                print(f"  VIX JSON Error: {e}")
                continue

        if not all_rows:
            raise EmptyDataError("No India VIX data")
        return all_rows

    @staticmethod
    def transform_data(query, data: list[dict], **kwargs) -> list[NSEIndiaVixData]:
        from foliopp_nse.utils.helpers import safe_float
        results = []
        for row in data:
            try:
                # NSE VIX response has multiple internal key variations
                results.append(NSEIndiaVixData.model_validate({
                    "date": row.get("TIMESTAMP") or row.get("EOD_TIMESTAMP"),
                    "open": safe_float(row.get("OPEN_INDEX_VAL") or row.get("EOD_OPEN_INDEX_VAL") or row.get("VIX_OPEN")),
                    "high": safe_float(row.get("HIGH_INDEX_VAL") or row.get("EOD_HIGH_INDEX_VAL") or row.get("VIX_HIGH")),
                    "low": safe_float(row.get("LOW_INDEX_VAL") or row.get("EOD_LOW_INDEX_VAL") or row.get("VIX_LOW")),
                    "close": safe_float(row.get("CLOSE_INDEX_VAL") or row.get("EOD_CLOSE_INDEX_VAL") or row.get("VIX_CLOSE")),
                    "prev_close": safe_float(row.get("PREV_CLOSE") or row.get("EOD_PREV_CLOSE")),
                    "change": safe_float(row.get("VIX_PTS_CHG")),
                    "change_pct": safe_float(row.get("VIX_PERC_CHG")),
                }))
            except Exception:
                continue
        return results
