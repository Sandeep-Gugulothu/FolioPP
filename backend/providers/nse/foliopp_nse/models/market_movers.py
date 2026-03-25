"""NSE Market Movers (Top Gainers/Losers) Model."""

from typing import Any

from foliopp_core.provider.abstract.fetcher import Fetcher
from foliopp_core.provider.standard_models.nse_models import (
    MarketMoverData, MarketMoverQueryParams,
    IndexSnapshotData, IndexSnapshotQueryParams,
)


def _safe_float(v) -> float | None:
    try:
        return float(str(v).replace(",", "")) if v not in (None, "-", "") else None
    except (ValueError, TypeError):
        return None


class NSEMarketMoverFetcher(Fetcher[MarketMoverQueryParams, list[MarketMoverData]]):
    @staticmethod
    def transform_query(params: dict[str, Any]) -> MarketMoverQueryParams:
        return MarketMoverQueryParams(**params)

    @staticmethod
    def extract_data(query, credentials=None, **kwargs) -> list[dict]:
        from foliopp_nse.utils.helpers import nse_fetch, NSE_BASE
        from foliopp_core.provider.utils.errors import EmptyDataError

        # gainers -> "gainers", losers -> "loosers" (NSE's typo)
        nse_type = "gainers" if query.mover_type == "gainer" else "loosers"
        url = f"{NSE_BASE}/api/live-analysis-variations"
        origin = f"{NSE_BASE}/market-data/top-gainers-losers"
        resp = nse_fetch(url, origin=origin, params={"index": nse_type})
        if resp.status_code != 200:
            raise EmptyDataError("No market movers data")
        from foliopp_nse.utils.helpers import nse_json
        raw = nse_json(resp)
        legends = {item[0]: item[1] for item in raw.get("legends", [])}
        rows = []
        for key, label in legends.items():
            for item in raw.get(key, {}).get("data", []):
                item["_category"] = label
                rows.append(item)
        return rows

    @staticmethod
    def transform_data(query, data: list[dict], **kwargs) -> list[MarketMoverData]:
        results = []
        for row in data:
            try:
                results.append(MarketMoverData.model_validate({
                    "symbol": row.get("symbol", ""),
                    "company_name": row.get("companyName") or row.get("meta", {}).get("companyName"),
                    "ltp": _safe_float(row.get("lastPrice") or row.get("ltp")),
                    "change": _safe_float(row.get("change") or row.get("netPrice")),
                    "change_pct": _safe_float(row.get("pChange") or row.get("perChange")),
                    "volume": _safe_float(row.get("totalTradedVolume") or row.get("tradedQuantity")),
                    "value": _safe_float(row.get("totalTradedValue")),
                    "category": row.get("_category"),
                    "mover_type": query.mover_type,
                }))
            except Exception:
                continue
        return results


class NSEIndexSnapshotFetcher(Fetcher[IndexSnapshotQueryParams, list[IndexSnapshotData]]):
    @staticmethod
    def transform_query(params: dict[str, Any]) -> IndexSnapshotQueryParams:
        return IndexSnapshotQueryParams(**params)

    @staticmethod
    def extract_data(query, credentials=None, **kwargs) -> list[dict]:
        from foliopp_nse.utils.helpers import nse_fetch, NSE_BASE
        from foliopp_core.provider.utils.errors import EmptyDataError

        url = f"{NSE_BASE}/api/allIndices"
        resp = nse_fetch(url, origin=NSE_BASE)
        if resp.status_code != 200:
            raise EmptyDataError("No index snapshot data")
        from foliopp_nse.utils.helpers import nse_json
        return nse_json(resp).get("data", [])

    @staticmethod
    def transform_data(query, data: list[dict], **kwargs) -> list[IndexSnapshotData]:
        results = []
        for row in data:
            try:
                results.append(IndexSnapshotData.model_validate({
                    "index_name": row.get("index") or row.get("indexSymbol", ""),
                    "last": _safe_float(row.get("last")),
                    "change": _safe_float(row.get("variation")),
                    "change_pct": _safe_float(row.get("percentChange")),
                    "open": _safe_float(row.get("open")),
                    "high": _safe_float(row.get("high")),
                    "low": _safe_float(row.get("low")),
                    "prev_close": _safe_float(row.get("previousClose")),
                    "year_high": _safe_float(row.get("yearHigh")),
                    "year_low": _safe_float(row.get("yearLow")),
                    "advances": row.get("advances"),
                    "declines": row.get("declines"),
                    "unchanged": row.get("unchanged"),
                    "pe": _safe_float(row.get("pe")),
                    "pb": _safe_float(row.get("pb")),
                    "div_yield": _safe_float(row.get("dy")),
                }))
            except Exception:
                continue
        return results
