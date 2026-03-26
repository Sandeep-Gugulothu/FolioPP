import asyncio
from typing import Any
from foliopp_core.provider.abstract.fetcher import Fetcher
from foliopp_core.provider.standard_models.nse_models import (
    ShareholdingPatternData, ShareholdingPatternQueryParams,
)

class NSEShareholdingPatternFetcher(
    Fetcher[ShareholdingPatternQueryParams, list[ShareholdingPatternData]]
):
    @staticmethod
    def transform_query(params: dict[str, Any]) -> ShareholdingPatternQueryParams:
        return ShareholdingPatternQueryParams(**params)

    @staticmethod
    def extract_data(query, credentials=None, **kwargs) -> list[dict]:
        from foliopp_nse.utils.helpers import nse_fetch, nse_json, NSE_BASE
        from foliopp_core.provider.utils.errors import EmptyDataError

        symbol = query.symbol
        url = f"{NSE_BASE}/api/corporate-share-holdings-master"
        origin = f"{NSE_BASE}/companies-listing/corporate-filings-shareholding-pattern"
        params = {"index": "equities", "symbol": symbol}
        
        resp = nse_fetch(url, origin=origin, params=params)
        if resp.status_code != 200:
            raise EmptyDataError(f"No shareholding pattern for {symbol}")
        
        data = nse_json(resp)
        return data if isinstance(data, list) else data.get("data", [])

    @staticmethod
    def transform_data(query, data: list[dict], **kwargs) -> list[ShareholdingPatternData]:
        results = []
        for row in data:
            try:
                # NSE returns multiple quarters, take the most recent OR all
                results.append(ShareholdingPatternData.model_validate({
                    "symbol": row.get("symbol", ""),
                    "company_name": row.get("name") or row.get("companyName"),
                    "quarter_ending": row.get("date") or row.get("period"),
                    "promoter_holding": row.get("pr_and_prgrp"),
                    "public_holding": row.get("public_val"),
                    "other_holding": row.get("employeeTrusts"),
                    "total_shares": row.get("totalShares") or row.get("total"),
                    "details_url": row.get("xbrl") or row.get("submissionUrl"),
                }))
            except Exception:
                continue
        return results
