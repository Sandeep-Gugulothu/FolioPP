"""NSE FII/DII Trading Activity Model."""

from typing import Any
from pydantic import field_validator
from datetime import datetime

from foliopp_core.provider.abstract.fetcher import Fetcher
from foliopp_core.provider.standard_models.nse_models import (
    FiiDiiData, FiiDiiQueryParams,
)


class NSEFiiDiiData(FiiDiiData):
    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, v):
        if isinstance(v, str):
            for fmt in ("%d-%b-%Y", "%Y-%m-%d", "%d-%m-%Y", "%b %d, %Y"):
                try:
                    return datetime.strptime(v.strip(), fmt).date()
                except ValueError:
                    continue
        return v


class NSEFiiDiiFetcher(Fetcher[FiiDiiQueryParams, list[NSEFiiDiiData]]):
    @staticmethod
    def transform_query(params: dict[str, Any]) -> FiiDiiQueryParams:
        return FiiDiiQueryParams(**params)

    @staticmethod
    def extract_data(query: FiiDiiQueryParams, credentials=None, **kwargs) -> list[dict]:
        from foliopp_nse.utils.helpers import nse_fetch, NSE_BASE
        from foliopp_core.provider.utils.errors import EmptyDataError

        url = f"{NSE_BASE}/api/fiidiiTradeReact"
        resp = nse_fetch(url)
        if resp.status_code != 200:
            raise EmptyDataError("No FII/DII data available")
        from foliopp_nse.utils.helpers import nse_json
        return nse_json(resp)

    @staticmethod
    def transform_data(query, data: list[dict], **kwargs) -> list[NSEFiiDiiData]:
        results = []
        for row in data:
            try:
                results.append(NSEFiiDiiData.model_validate({
                    "date": row.get("date"),
                    "category": row.get("category", ""),
                    "buy_value": _safe_float(row.get("buyValue")),
                    "sell_value": _safe_float(row.get("sellValue")),
                    "net_value": _safe_float(row.get("netValue")),
                }))
            except Exception:
                continue
        return results


def _safe_float(v) -> float | None:
    try:
        return float(str(v).replace(",", "")) if v not in (None, "-", "") else None
    except (ValueError, TypeError):
        return None
