"""NSE FnO Equity List (Securities in F&O) Model."""

from typing import Any

from foliopp_core.provider.abstract.fetcher import Fetcher
from foliopp_core.provider.standard_models.nse_models import FnoEquityData, FnoEquityQueryParams


class NSEFnoEquityListFetcher(Fetcher[FnoEquityQueryParams, list[FnoEquityData]]):
    @staticmethod
    def transform_query(params: dict[str, Any]) -> FnoEquityQueryParams:
        return FnoEquityQueryParams(**params)

    @staticmethod
    def extract_data(query, credentials=None, **kwargs) -> list[dict]:
        from foliopp_nse.utils.helpers import nse_fetch, nse_json, NSE_BASE
        from foliopp_core.provider.utils.errors import EmptyDataError

        # NSE's specific index for F&O securities
        url = f"{NSE_BASE}/api/equity-stockIndices"
        origin = f"{NSE_BASE}/market-data/index-constituents"
        resp = nse_fetch(url, origin=origin, params={"index": "SECURITIES IN F&O"})
        if resp.status_code != 200:
            raise EmptyDataError("No securities in F&O list found")
        raw = nse_json(resp)
        return raw.get("data", [])

    @staticmethod
    def transform_data(query, data: list[dict], **kwargs) -> list[FnoEquityData]:
        results = []
        for row in data:
            try:
                meta = row.get("meta", {})
                results.append(FnoEquityData.model_validate({
                    "symbol": row.get("symbol", ""),
                    "company_name": row.get("companyName") or meta.get("companyName"),
                    "series": row.get("series") or meta.get("series"),
                    "isin": meta.get("isin"),
                }))
            except Exception:
                continue
        return results
