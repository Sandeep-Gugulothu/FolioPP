"""NSE Bulk/Block Deals Model."""

from datetime import date, datetime, timedelta
from typing import Any

from pydantic import field_validator

from foliopp_core.provider.abstract.fetcher import Fetcher
from foliopp_core.provider.standard_models.nse_models import (
    BulkBlockDealData,
    BulkBlockDealQueryParams,
)


def _resolve_dates(query) -> tuple[date, date]:
    if query.from_date and query.to_date:
        return query.from_date, query.to_date
    today = date.today()
    period_map = {"1D": 1, "1W": 7, "1M": 30, "3M": 90, "6M": 180, "1Y": 365}
    delta = period_map.get(query.period or "1M", 30)
    return today - timedelta(days=delta), today


class NSEBulkBlockDealData(BulkBlockDealData):
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


class NSEBulkBlockDealFetcher(
    Fetcher[BulkBlockDealQueryParams, list[NSEBulkBlockDealData]]
):
    @staticmethod
    def transform_query(params: dict[str, Any]) -> BulkBlockDealQueryParams:
        return BulkBlockDealQueryParams(**params)

    @staticmethod
    def extract_data(
        query: BulkBlockDealQueryParams,
        credentials: dict | None = None,
        **kwargs,
    ) -> list[dict]:
        import pandas as pd
        from io import BytesIO
        from foliopp_nse.utils.helpers import nse_fetch, to_nse_date, NSE_BASE, safe_float
        from foliopp_core.provider.utils.errors import EmptyDataError

        from_date, to_date = _resolve_dates(query)
        option = "bulk_deals" if query.deal_type == "bulk" else "block_deals"
        url = f"{NSE_BASE}/api/historicalOR/bulk-block-short-deals"
        params = {
            "optionType": option,
            "from": to_nse_date(from_date),
            "to": to_nse_date(to_date),
            "csv": "true",
        }
        resp = nse_fetch(url, params=params)
        if resp.status_code != 200 or not resp.content:
            raise EmptyDataError(f"No {query.deal_type} deal data")

        df = pd.read_csv(BytesIO(resp.content))
        df.columns = [c.strip().replace(' ', '') for c in df.columns]
        return df.to_dict("records")

    @staticmethod
    def transform_data(
        query: BulkBlockDealQueryParams,
        data: list[dict],
        **kwargs,
    ) -> list[NSEBulkBlockDealData]:
        col_map = {
            "Date": "date", "Symbol": "symbol", "SecurityName": "security_name",
            "ClientName": "client_name", "Buy/Sell": "buy_sell",
            "QuantityTraded": "quantity", "TradePrice/Wght.Avg.Price": "price",
        }
        results = []
        # --- Symbol Filtering ---
        target = query.symbol.upper() if getattr(query, "symbol", None) else None
        
        for row in data:
            mapped = {col_map.get(k, k): v for k, v in row.items() if v not in (None, "-", "")}
            
            # Clean numerical fields (Remove commas)
            if "quantity" in mapped: mapped["quantity"] = safe_float(mapped["quantity"])
            if "price" in mapped: mapped["price"] = safe_float(mapped["price"])
            
            # Filter by symbol if requested
            if target:
                row_sym = str(mapped.get("symbol", "")).upper()
                if target not in row_sym: # Supports partial match (e.g. SBIN matches SBIN.NS)
                    continue

            mapped["deal_type"] = query.deal_type
            
            # --- Track 6: Intelligence Signaling Logic ---
            # 1. Detect Promoter
            client_upper = str(mapped.get("client_name", "")).upper()
            is_promoter = any(x in client_upper for x in ["PROMOTER", "PROMOTERS"])
            mapped["is_promoter"] = is_promoter
            
            # 2. Priority Flagging (Deterministic Algorithm)
            # High Priority if SELL + PROMOTER
            if is_promoter and str(mapped.get("buy_sell", "")).upper() == "SELL":
                mapped["priority"] = 1
            else:
                mapped["priority"] = 0
            
            # 3. Pct Equity (Requires secondary lookups, currently placeholder)
            mapped["pct_equity"] = None 

            try:
                results.append(NSEBulkBlockDealData.model_validate(mapped))
            except Exception:
                continue
        return results
