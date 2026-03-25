"""NSE Most Active Equities Model."""

from typing import Any

from foliopp_core.provider.abstract.fetcher import Fetcher
from foliopp_core.provider.standard_models.nse_models import MostActiveData, MostActiveQueryParams


def _safe_float(v) -> float | None:
    try:
        return float(str(v).replace(",", "")) if v not in (None, "-", "") else None
    except (ValueError, TypeError):
        return None


class NSEMostActiveFetcher(Fetcher[MostActiveQueryParams, list[MostActiveData]]):
    @staticmethod
    def transform_query(params: dict[str, Any]) -> MostActiveQueryParams:
        return MostActiveQueryParams(**params)

    @staticmethod
    def extract_data(query, credentials=None, **kwargs) -> list[dict]:
        from foliopp_nse.utils.helpers import nse_fetch, nse_json, NSE_BASE
        from foliopp_core.provider.utils.errors import EmptyDataError

        # NSE uses "active-volume" or "active-value"
        nse_type = f"active-{query.fetch_by}"
        url = f"{NSE_BASE}/api/live-analysis-variations"
        origin = f"{NSE_BASE}/market-data/most-active-equities"
        resp = nse_fetch(url, origin=origin, params={"index": nse_type})
        if resp.status_code != 200:
            raise EmptyDataError("No most active equities data")
        raw = nse_json(resp)
        rows = []
        for item in raw.get("data", []):
            item["_fetch_by"] = query.fetch_by
            rows.append(item)
        return rows

    @staticmethod
    def transform_data(query, data: list[dict], **kwargs) -> list[MostActiveData]:
        results = []
        for row in data:
            try:
                results.append(MostActiveData.model_validate({
                    "symbol": row.get("symbol", ""),
                    "company_name": row.get("companyName") or row.get("meta", {}).get("companyName"),
                    "ltp": _safe_float(row.get("lastPrice") or row.get("ltp")),
                    "change": _safe_float(row.get("change") or row.get("netPrice")),
                    "change_pct": _safe_float(row.get("pChange") or row.get("perChange")),
                    "volume": _safe_float(row.get("totalTradedVolume") or row.get("tradedQuantity")),
                    "value": _safe_float(row.get("totalTradedValue")),
                    "fetch_by": row.get("_fetch_by"),
                }))
            except Exception:
                continue
        return results
