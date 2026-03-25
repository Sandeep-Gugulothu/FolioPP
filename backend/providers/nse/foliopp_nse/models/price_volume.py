"""NSE Price Volume Data Model (without deliverable %)."""

from datetime import date, datetime, timedelta
from io import BytesIO
from typing import Any

from pydantic import field_validator

from foliopp_core.provider.abstract.fetcher import Fetcher
from foliopp_core.provider.standard_models.nse_models import (
    PriceVolumeData, NSESymbolDateRangeQueryParams,
)

_COL_MAP = {
    "Symbol": "symbol",
    "Series": "series",
    "Date": "date",
    "Prev Close": "prev_close",
    "Open Price": "open",
    "High Price": "high",
    "Low Price": "low",
    "Close Price": "close",
    "Average Price": "avg_price",
    "Total Traded Quantity": "total_traded_qty",
    "No. of Trades": "trades",
    "Deliverable Qty": "deliverable_qty",
    "% Dly Qt to Traded Qty": "pct_delivery",
}
_TURNOVER_PREFIX = "Turnover"
_NUMERIC = {"prev_close", "open", "high", "low", "close", "avg_price",
            "total_traded_qty", "trades", "deliverable_qty", "pct_delivery", "turnover"}


def _clean_num(v) -> float | None:
    if v is None or str(v).strip() in ("-", ""):
        return None
    try:
        return float(str(v).replace(",", "").strip())
    except (ValueError, TypeError):
        return None


def _resolve_dates(query) -> tuple[date, date]:
    if query.from_date and query.to_date:
        return query.from_date, query.to_date
    today = date.today()
    period_map = {"1D": 1, "1W": 7, "1M": 30, "3M": 90, "6M": 180, "1Y": 365}
    delta = period_map.get(query.period or "1M", 30)
    return today - timedelta(days=delta), today


class NSEPriceVolumeData(PriceVolumeData):
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


class NSEPriceVolumeFetcher(Fetcher[NSESymbolDateRangeQueryParams, list[NSEPriceVolumeData]]):
    @staticmethod
    def transform_query(params: dict[str, Any]) -> NSESymbolDateRangeQueryParams:
        return NSESymbolDateRangeQueryParams(**params)

    @staticmethod
    def extract_data(query, credentials=None, **kwargs) -> list[dict]:
        import pandas as pd
        from foliopp_nse.utils.helpers import nse_fetch, to_nse_date, date_range_chunks, NSE_BASE
        from foliopp_core.provider.utils.errors import EmptyDataError

        from_date, to_date = _resolve_dates(query)
        url = f"{NSE_BASE}/api/historicalOR/generateSecurityWiseHistoricalData"
        origin = f"{NSE_BASE}/report-detail/eq_security"

        frames = []
        for start, end in date_range_chunks(from_date, to_date):
            params = {
                "from": to_nse_date(start),
                "to": to_nse_date(end),
                "symbol": query.symbol,
                "type": "priceVolumeDeliverable",
                "series": "EQ",
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
            raise EmptyDataError(f"No price/volume data for {query.symbol}")
        return pd.concat(frames, ignore_index=True).to_dict("records")

    @staticmethod
    def transform_data(query, data: list[dict], **kwargs) -> list[NSEPriceVolumeData]:
        results = []
        for row in data:
            mapped: dict = {}
            for raw_col, val in row.items():
                col = str(raw_col).strip()
                if col.startswith(_TURNOVER_PREFIX):
                    mapped["turnover"] = _clean_num(val)
                    continue
                std = _COL_MAP.get(col)
                if std is None:
                    continue
                mapped[std] = _clean_num(val) if std in _NUMERIC else (str(val).strip() if val not in (None, "") else None)
            mapped.setdefault("symbol", query.symbol)
            try:
                results.append(NSEPriceVolumeData.model_validate(mapped))
            except Exception:
                continue
        return results
