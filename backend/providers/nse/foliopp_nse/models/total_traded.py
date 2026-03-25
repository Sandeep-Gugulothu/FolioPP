"""NSE Total Traded Stocks Model."""

from typing import Any

from foliopp_core.provider.abstract.fetcher import Fetcher
from foliopp_core.provider.standard_models.nse_models import TotalTradedData, TotalTradedQueryParams


class NSETotalTradedFetcher(Fetcher[TotalTradedQueryParams, list[TotalTradedData]]):
    @staticmethod
    def transform_query(params: dict[str, Any]) -> TotalTradedQueryParams:
        return TotalTradedQueryParams(**params)

    @staticmethod
    def extract_data(query, credentials=None, **kwargs) -> list[dict]:
        from foliopp_nse.utils.helpers import nse_fetch, nse_json, NSE_BASE
        from foliopp_core.provider.utils.errors import EmptyDataError

        url = f"{NSE_BASE}/api/allIndices"
        resp = nse_fetch(url, origin=NSE_BASE)
        if resp.status_code != 200:
            raise EmptyDataError("No total traded data")
        raw = nse_json(resp)
        # The NIFTY 50 entry has advances/declines/unchanged for the broad market
        return raw.get("data", [])

    @staticmethod
    def transform_data(query, data: list[dict], **kwargs) -> list[TotalTradedData]:
        # Find the "NIFTY 50" or first entry with advances data
        for row in data:
            if row.get("index", "").upper() in ("NIFTY 50", "NIFTY50"):
                try:
                    return [TotalTradedData.model_validate({
                        "advances": row.get("advances"),
                        "declines": row.get("declines"),
                        "unchanged": row.get("unchanged"),
                        "total": (
                            (int(row.get("advances") or 0) +
                             int(row.get("declines") or 0) +
                             int(row.get("unchanged") or 0)) or None
                        ),
                    })]
                except Exception:
                    pass
        return []
