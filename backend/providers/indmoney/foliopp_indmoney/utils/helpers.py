"""INDmoney HTTP helpers.

All API calls must include the access token in the Authorization header.
"""

import time
import requests
from typing import Any

INDMONEY_BASE = "https://api.indstocks.com"
INDMONEY_HEADERS = {
    "Accept": "*/*",
    "Content-Type": "application/json",
}

def indmoney_fetch(url: str, token: str, params: dict | None = None) -> requests.Response:
    """Fetch a URL using the INDmoney access token."""
    headers = INDMONEY_HEADERS.copy()
    headers["Authorization"] = token
    resp = requests.get(url, params=params, headers=headers, timeout=30)
    return resp

def indmoney_json(resp: requests.Response) -> dict:
    """Parse and validate INDmoney JSON response."""
    from foliopp_core.provider.utils.errors import EmptyDataError
    
    if resp.status_code in (401, 403):
        raise EmptyDataError(f"INDmoney Authentication Failed")
        
    try:
        data = resp.json()
    except Exception:
        raise EmptyDataError(f"INDmoney returned non-JSON response")
        
    # Support both 'status: success' and 'success: true'
    is_success = data.get("status") == "success" or data.get("success") is True
    if not is_success:
        msg = data.get("message") or data.get("error") or "Unknown INDmoney API Error"
        raise EmptyDataError(msg)
    return data

_SCRIP_MAP = {}

def get_scrip_code(symbol: str, token: str, exchange: str = "NSE") -> str:
    """Map a trading symbol to an INDmoney scrip-code (e.g. NSE_3045)."""
    global _SCRIP_MAP
    map_key = f"{exchange.upper()}_{symbol.upper()}"
    
    if map_key not in _SCRIP_MAP:
        url = f"{INDMONEY_BASE}/market/instruments?source=equity"
        resp = indmoney_fetch(url, token)
        if resp.status_code == 200:
            import pandas as pd
            from io import StringIO
            df = pd.read_csv(StringIO(resp.text))
            for _, row in df.iterrows():
                ex = str(row.get("EXCH", "")).upper()
                sym = str(row.get("TRADING_SYMBOL", "")).upper()
                sid = str(row.get("SECURITY_ID", ""))
                _SCRIP_MAP[f"{ex}_{sym}"] = sid
    
    scrip_id = _SCRIP_MAP.get(map_key)
    if not scrip_id:
        from foliopp_core.provider.utils.errors import EmptyDataError
        raise EmptyDataError(f"Scrip code not found for {symbol} on {exchange}")
    
    return f"{exchange.upper()}_{scrip_id}"
