"""NSE Most Active Securities (Volume/Value) Model."""

from typing import Any

from foliopp_core.provider.abstract.fetcher import Fetcher
from foliopp_core.provider.standard_models.nse_models import MostActiveData, MostActiveQueryParams


class NSEMostActiveFetcher(Fetcher[MostActiveQueryParams, list[MostActiveData]]):
    @staticmethod
    def transform_query(params: dict[str, Any]) -> MostActiveQueryParams:
        return MostActiveQueryParams(**params)

    @staticmethod
    def extract_data(query, credentials=None, **kwargs) -> list[dict]:
        from foliopp_nse.utils.helpers import nse_fetch, nse_json, NSE_BASE
        from foliopp_core.provider.utils.errors import EmptyDataError

        # NSE index can be "volume" or "value"
        url = f"{NSE_BASE}/api/live-analysis-most-active-securities"
        origin = f"{NSE_BASE}/market-data/most-active-securities"
        resp = nse_fetch(url, origin=origin, params={"index": query.fetch_by})
        if resp.status_code != 200:
            raise EmptyDataError(f"No most active data for {query.fetch_by}")
        raw = nse_json(resp)
        return raw.get("data", [])

    @staticmethod
    def transform_data(query, data: list[dict], **kwargs) -> list[MostActiveData]:
        from foliopp_nse.utils.helpers import safe_float
        results = []
        for row in data:
            try:
                results.append(MostActiveData.model_validate({
                    "symbol": row.get("symbol", ""),
                    "company_name": row.get("companyName"),
                    "ltp": safe_float(row.get("lastPrice") or row.get("ltp")),
                    "change": safe_float(row.get("pChange")), 
                    "change_pct": safe_float(row.get("pChange")),
                    "volume": safe_float(row.get("quantity") or row.get("tradedQuantity")),
                    "value": safe_float(row.get("value") or row.get("totalTradedValue")),
                    "fetch_by": query.fetch_by
                }))
            except Exception:
                continue
        return results
