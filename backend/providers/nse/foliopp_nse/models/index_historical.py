"""NSE Index Historical Data Model."""

from datetime import date, datetime, timedelta
from typing import Any

from pydantic import field_validator

from foliopp_core.provider.abstract.fetcher import Fetcher
from foliopp_core.provider.standard_models.nse_models import (
    IndexHistoricalData, IndexHistoricalQueryParams,
)


def _resolve_dates(query) -> tuple[date, date]:
    if query.from_date and query.to_date:
        return query.from_date, query.to_date
    today = date.today()
    period_map = {"1D": 1, "1W": 7, "1M": 30, "3M": 90, "6M": 180, "1Y": 365}
    delta = period_map.get(query.period or "1M", 30)
    return today - timedelta(days=delta), today


class NSEIndexHistoricalData(IndexHistoricalData):
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


class NSEIndexHistoricalFetcher(Fetcher[IndexHistoricalQueryParams, list[NSEIndexHistoricalData]]):
    @staticmethod
    def transform_query(params: dict[str, Any]) -> IndexHistoricalQueryParams:
        return IndexHistoricalQueryParams(**params)

    @staticmethod
    def extract_data(query: IndexHistoricalQueryParams, credentials=None, **kwargs) -> list[dict]:
        from foliopp_nse.utils.helpers import nse_fetch, to_nse_date, date_range_chunks, NSE_BASE, nse_json
        from foliopp_core.provider.utils.errors import EmptyDataError

        from_date, to_date = _resolve_dates(query)
        origin = f"{NSE_BASE}/reports-indices-historical-index-data"
        all_rows = []

        # Convert index name to URL format
        idx = query.index_name.replace(" ", "%20").upper()

        for start, end in date_range_chunks(from_date, to_date):
            url = f"{NSE_BASE}/api/historicalOR/indicesHistory"
            params = {
                "indexType": idx,
                "from": to_nse_date(start),
                "to": to_nse_date(end),
            }
            resp = nse_fetch(url, origin=origin, params=params)
            print(f"  Fetching Index: {url} {params} -> {resp.status_code}")
            if resp.status_code != 200:
                continue
            try:
                raw_json = nse_json(resp)
                all_rows.extend(raw_json.get("data", []))
            except Exception:
                continue

        if not all_rows:
            raise EmptyDataError(f"No historical index data for {query.index_name}")
        return all_rows

    @staticmethod
    def transform_data(query: IndexHistoricalQueryParams, data: list[dict], **kwargs) -> list[NSEIndexHistoricalData]:
        from foliopp_nse.utils.helpers import safe_float
        results = []
        for row in data:
            try:
                results.append(NSEIndexHistoricalData.model_validate({
                    "index_name": row.get("INDEX_NAME") or query.index_name,
                    "date": row.get("TIMESTAMP"),
                    "open": safe_float(row.get("OPEN_INDEX_VAL")),
                    "high": safe_float(row.get("HIGH_INDEX_VAL")),
                    "low": safe_float(row.get("LOW_INDEX_VAL")),
                    "close": safe_float(row.get("CLOSE_INDEX_VAL")),
                    "volume": safe_float(row.get("TRADED_QTY")),
                    "turnover": safe_float(row.get("TURN_OVER")),
                }))
            except Exception:
                continue
        return results
