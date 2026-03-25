"""NSE India HTTP helpers.

NSE requires a valid session cookie obtained by first hitting the homepage.
All API calls must include this cookie + proper headers to avoid 403s.
"""

import time
from datetime import date, datetime, timedelta
from typing import Any

import requests

_SESSION: requests.Session | None = None
_SESSION_TS: float = 0
_SESSION_TTL = 300  # refresh session every 5 minutes

NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.nseindia.com/",
    "Connection": "keep-alive",
    "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
}

NSE_BASE = "https://www.nseindia.com"
NSE_ARCHIVES = "https://nsearchives.nseindia.com"

def _get_session() -> requests.Session:
    """Return a session with valid NSE cookies, refreshing if stale."""
    global _SESSION, _SESSION_TS
    now = time.time()
    if _SESSION is None or (now - _SESSION_TS) > _SESSION_TTL:
        import time as pytime
        s = requests.Session()
        s.headers.update(NSE_HEADERS)
        # Hit homepage to get cookies with increased timeout
        s.get(NSE_BASE, timeout=30)
        pytime.sleep(1) # Small delay to ensure cookies are set
        _SESSION = s
        _SESSION_TS = now
    return _SESSION

def nse_fetch(url: str, origin: str | None = None, params: dict | None = None) -> requests.Response:
    """Fetch a URL using the NSE session. Retries once on 403."""
    session = _get_session()
    headers = {"Accept-Encoding": "gzip, deflate, br"}
    if origin:
        headers["Referer"] = origin
    else:
        # Default referer for standard equity APIs
        headers["Referer"] = "https://www.nseindia.com/get-quote/equity/RELIANCE"
        
    resp = session.get(url, params=params, headers=headers, timeout=30)
    if resp.status_code == 403:
        # Session expired — force refresh and retry once
        global _SESSION_TS
        _SESSION_TS = 0
        session = _get_session()
        resp = session.get(url, params=params, headers=headers, timeout=30)
    return resp


def nse_json(resp: requests.Response) -> dict | list:
    """Parse JSON from NSE response. Handles UTF-8-SIG to avoid BOM issues."""
    import json
    content = resp.content
    try:
        # NSE sometimes includes a BOM or weird encoding
        return json.loads(content.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        pass
    try:
        import brotli
        return json.loads(brotli.decompress(content).decode("utf-8-sig"))
    except Exception:
        pass
    import gzip
    try:
        return json.loads(gzip.decompress(content).decode("utf-8-sig"))
    except Exception:
        # Fallback to plain bytes if everything else fails
        return resp.json()


def safe_float(v: Any) -> float | None:
    """Parse Indian-formatted numbers like '1,77,48,625' or '1,048.90'."""
    if v is None or str(v).strip() in ("-", "", "None"):
        return None
    try:
        return float(str(v).replace(",", "").strip())
    except (ValueError, TypeError):
        return None


def to_nse_date(d: date | str) -> str:
    """Convert date to NSE's dd-mm-YYYY format."""
    if isinstance(d, str):
        d = datetime.strptime(d, "%Y-%m-%d").date()
    return d.strftime("%d-%m-%Y")


def date_range_chunks(from_date: date, to_date: date, chunk_days: int = 364):
    """Yield (start, end) date pairs in chunks — NSE limits to ~1 year per request."""
    current = from_date
    while current <= to_date:
        end = min(current + timedelta(days=chunk_days), to_date)
        yield current, end
        current = end + timedelta(days=1)
