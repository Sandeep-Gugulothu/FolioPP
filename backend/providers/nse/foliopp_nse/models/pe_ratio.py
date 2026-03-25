"""NSE PE Ratio Data Model."""

from datetime import datetime
from typing import Any

from pydantic import field_validator

from foliopp_core.provider.abstract.fetcher import Fetcher
from foliopp_core.provider.standard_models.nse_models import PERatioData, PERatioQueryParams


class NSEPERatioData(PERatioData):
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


class NSEPERatioFetcher(Fetcher[PERatioQueryParams, list[NSEPERatioData]]):
    @staticmethod
    def transform_query(params: dict[str, Any]) -> PERatioQueryParams:
        return PERatioQueryParams(**params)

    @staticmethod
    def extract_data(query, credentials=None, **kwargs) -> list[dict]:
        from foliopp_nse.utils.helpers import nse_fetch, nse_json, NSE_BASE
        from foliopp_core.provider.utils.errors import EmptyDataError

        url = f"{NSE_BASE}/api/index-PE-PB-data"
        origin = f"{NSE_BASE}/market-data/PE-PB-ratio"
        resp = nse_fetch(url, origin=origin, params={"date": query.trade_date})
        if resp.status_code != 200:
            raise EmptyDataError(f"No PE ratio data for {query.trade_date}")
        return nse_json(resp).get("data", [])

    @staticmethod
    def transform_data(query, data: list[dict], **kwargs) -> list[NSEPERatioData]:
        from foliopp_nse.utils.helpers import safe_float
        results = []
        for row in data:
            try:
                results.append(NSEPERatioData.model_validate({
                    "index_name": row.get("indexName", ""),
                    "date": row.get("date") or query.trade_date,
                    "pe": safe_float(row.get("pe")),
                    "pb": safe_float(row.get("pb")),
                    "div_yield": safe_float(row.get("divYield")),
                }))
            except Exception:
                continue
        return results
