"""NSE Short Selling Data Model."""

from datetime import date, datetime, timedelta
from io import BytesIO
from typing import Any

from pydantic import field_validator

from foliopp_core.provider.abstract.fetcher import Fetcher
from foliopp_core.provider.standard_models.nse_models import (
    ShortSellingData, ShortSellingQueryParams,
)


def _resolve_dates(query) -> tuple[date, date]:
    if query.from_date and query.to_date:
        return query.from_date, query.to_date
    today = date.today()
    period_map = {"1D": 1, "1W": 7, "1M": 30, "3M": 90, "6M": 180, "1Y": 365}
    delta = period_map.get(query.period or "1M", 30)
    return today - timedelta(days=delta), today


class NSEShortSellingData(ShortSellingData):
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


class NSEShortSellingFetcher(Fetcher[ShortSellingQueryParams, list[NSEShortSellingData]]):
    @staticmethod
    def transform_query(params: dict[str, Any]) -> ShortSellingQueryParams:
        return ShortSellingQueryParams(**params)

    @staticmethod
    def extract_data(query, credentials=None, **kwargs) -> list[dict]:
        import pandas as pd
        from foliopp_nse.utils.helpers import nse_fetch, to_nse_date, date_range_chunks, NSE_BASE
        from foliopp_core.provider.utils.errors import EmptyDataError

        from_date, to_date = _resolve_dates(query)
        url = f"{NSE_BASE}/api/historicalOR/bulk-block-short-deals"
        origin = f"{NSE_BASE}/market-data/short-selling"

        frames = []
        for start, end in date_range_chunks(from_date, to_date):
            params = {
                "optionType": "short_selling",
                "from": to_nse_date(start),
                "to": to_nse_date(end),
                "csv": "true",
            }
            resp = nse_fetch(url, origin=origin, params=params)
            if resp.status_code != 200 or not resp.content:
                continue
            try:
                df = pd.read_csv(BytesIO(resp.content), encoding="utf-8-sig")
                df.columns = [c.strip() for c in df.columns]
                frames.append(df)
            except Exception:
                continue

        if not frames:
            raise EmptyDataError("No short selling data")
        import pandas as pd
        return pd.concat(frames, ignore_index=True).to_dict("records")

    @staticmethod
    def transform_data(query, data: list[dict], **kwargs) -> list[NSEShortSellingData]:
        _COL_MAP = {
            "Date": "date",
            "Symbol": "symbol",
            "SecurityName": "security_name",
            "Quantity": "quantity",
        }
        results = []
        for row in data:
            mapped = {}
            for k, v in row.items():
                col = str(k).strip()
                std = _COL_MAP.get(col)
                if std:
                    mapped[std] = str(v).strip() if v not in (None, "-", "") else None
            try:
                results.append(NSEShortSellingData.model_validate(mapped))
            except Exception:
                continue
        return results
