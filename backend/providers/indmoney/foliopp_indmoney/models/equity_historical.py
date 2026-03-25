"""INDmoney Equity Historical Fetcher."""

from datetime import datetime, time
from typing import Any

from foliopp_core.provider.abstract.fetcher import Fetcher
from foliopp_core.provider.standard_models.equity_historical import (
    EquityHistoricalData,
    EquityHistoricalQueryParams,
)

class INDmoneyEquityHistoricalFetcher(
    Fetcher[EquityHistoricalQueryParams, list[EquityHistoricalData]]
):
    @staticmethod
    def transform_query(params: dict[str, Any]) -> EquityHistoricalQueryParams:
        return EquityHistoricalQueryParams(**params)

    @staticmethod
    def extract_data(
        query: EquityHistoricalQueryParams,
        credentials: dict[str, str] | None = None,
        **kwargs,
    ) -> dict:
        from foliopp_indmoney.utils.helpers import indmoney_fetch, indmoney_json, get_scrip_code, INDMONEY_BASE
        
        token = (credentials or {}).get("access_token")
        if not token:
             import config
             token = getattr(config.settings, "INDMONEY_ACCESS_TOKEN", None)
        
        if not token:
            from foliopp_core.provider.utils.errors import EmptyDataError
            raise EmptyDataError("INDmoney token required")
        
        scrip_code = get_scrip_code(query.symbol, token, query.exchange)
        start_dt = datetime.combine(query.start_date or datetime.now().date(), time.min)
        end_dt = datetime.combine(query.end_date or datetime.now().date(), time.max)
        
        # Capping at now prevents Bad Request on some intervals
        now = datetime.now()
        if end_dt > now: end_dt = now
            
        start_ms = int(start_dt.timestamp() * 1000)
        end_ms = int(end_dt.timestamp() * 1000)
        
        interval_map = {"1d": "1day", "1wk": "1week", "1mo": "1month"}
        interval = interval_map.get(query.interval, "1day")
        
        url = f"{INDMONEY_BASE}/market/historical/{interval}"
        params = {
            "scrip-codes": scrip_code,
            "start_time": start_ms,
            "end_time": end_ms
        }
        
        resp = indmoney_fetch(url, token, params=params)
        json_data = indmoney_json(resp)
        return json_data.get("data", {})

    @staticmethod
    def transform_data(
        query: EquityHistoricalQueryParams,
        data: dict,
        **kwargs,
    ) -> list[EquityHistoricalData]:
        # Support both direct candles and nested-by-scrip candles
        candles = data.get("candles")
        if candles is None:
            # Look for the scrip key (e.g., 'NSE_2885')
            for v in data.values():
                if isinstance(v, dict) and "candles" in v:
                    candles = v["candles"]
                    break
        
        if not candles: return []
            
        results = []
        for c in candles:
            if isinstance(c, dict):
                results.append(EquityHistoricalData(
                    symbol=query.symbol,
                    date=datetime.fromtimestamp(c['ts']),
                    open=float(c['o']),
                    high=float(c['h']),
                    low=float(c['l']),
                    close=float(c['c']),
                    volume=int(c['v']) if 'v' in c else None,
                    exchange=query.exchange
                ))
            else:
                results.append(EquityHistoricalData(
                    symbol=query.symbol,
                    date=datetime.fromtimestamp(c[0] / 1000.0),
                    open=float(c[1]),
                    high=float(c[2]),
                    low=float(c[3]),
                    close=float(c[4]),
                    volume=int(c[5]) if len(c) > 5 else None,
                    exchange=query.exchange
                ))
        return results
