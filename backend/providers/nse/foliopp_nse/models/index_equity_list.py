"""NSE Index Equity List Model (e.g. NIFTY MIDCAP 150)."""

from typing import Any

from foliopp_core.provider.abstract.fetcher import Fetcher
from foliopp_core.provider.standard_models.nse_models import IndexEquityData, IndexEquityQueryParams


class NSEIndexEquityListFetcher(Fetcher[IndexEquityQueryParams, list[IndexEquityData]]):
    @staticmethod
    def transform_query(params: dict[str, Any]) -> IndexEquityQueryParams:
        return IndexEquityQueryParams(**params)

    @staticmethod
    def extract_data(query, credentials=None, **kwargs) -> list[dict]:
        from foliopp_nse.utils.helpers import nse_fetch, nse_json, NSE_BASE
        from foliopp_core.provider.utils.errors import EmptyDataError

        # NSE uses uppercase with spaces replaced by spaces (as-is)
        index = query.index_name.upper()
        url = f"{NSE_BASE}/api/equity-stockIndices"
        origin = f"{NSE_BASE}/market-data/index-constituents"
        resp = nse_fetch(url, origin=origin, params={"index": index})
        if resp.status_code != 200:
            raise EmptyDataError(f"No equity list for index: {query.index_name}")
        raw = nse_json(resp)
        return raw.get("data", [])

    @staticmethod
    def transform_data(query, data: list[dict], **kwargs) -> list[IndexEquityData]:
        results = []
        for row in data:
            try:
                meta = row.get("meta", {})
                results.append(IndexEquityData.model_validate({
                    "symbol": row.get("symbol", ""),
                    "company_name": row.get("companyName") or meta.get("companyName"),
                    "series": row.get("series") or meta.get("series"),
                    "isin": meta.get("isin"),
                    "industry": meta.get("industry"),
                }))
            except Exception:
                continue
        return results
