"""yfinance Equity Historical Price Model."""

from datetime import datetime
from typing import Any, Literal, TYPE_CHECKING
from warnings import warn

from pydantic import Field, PrivateAttr

from foliopp_core.provider.abstract.fetcher import Fetcher
from foliopp_core.provider.standard_models.equity_historical import (
    EquityHistoricalData,
    EquityHistoricalQueryParams,
)

if TYPE_CHECKING:
    from pandas import DataFrame


# Maps our interval names -> what yfinance actually expects
INTERVALS_DICT: dict[str, str] = {
    "1m":  "1m",
    "2m":  "2m",
    "5m":  "5m",
    "15m": "15m",
    "30m": "30m",
    "60m": "60m",
    "90m": "90m",
    "1h":  "1h",
    "1d":  "1d",
    "5d":  "5d",
    "1wk": "1wk",
    "1mo": "1mo",
    "3mo": "3mo",
}


class YFinanceEquityHistoricalQueryParams(EquityHistoricalQueryParams):
    """yfinance query params - extends standard with yfinance-specific options."""

    # Override interval with the full list yfinance supports
    interval: Literal[
        "1m", "2m", "5m", "15m", "30m", "60m", "90m",
        "1h", "1d", "5d", "1wk", "1mo", "3mo",
    ] = Field(
        default="1d",
        description="Data interval. Intraday: 1m/2m/5m/15m/30m/60m/90m/1h. Daily+: 1d/5d/1wk/1mo/3mo",
    )
    adjusted: bool = Field(
        default=False,
        description="Return adjusted close prices accounting for splits and dividends.",
    )
    include_actions: bool = Field(
        default=True,
        description="Include dividends and stock splits in results.",
    )

    # PrivateAttr - passed to yf_download internally, not exposed as user-facing params
    _progress: bool = PrivateAttr(default=False)
    _ignore_tz: bool = PrivateAttr(default=True)


class YFinanceEquityHistoricalData(EquityHistoricalData):
    """yfinance output - extends standard fields with split/dividend info."""

    split_ratio: float | None = Field(default=None, description="Stock split ratio if a split occurred.")
    dividend: float | None = Field(default=None, description="Dividend paid on this date in INR.")


class YFinanceEquityHistoricalFetcher(
    Fetcher[
        YFinanceEquityHistoricalQueryParams,
        list[YFinanceEquityHistoricalData],
    ]
):
    """Fetches equity historical OHLCV from yfinance."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> YFinanceEquityHistoricalQueryParams:
        """Fill default dates if missing, then validate."""
        from dateutil.relativedelta import relativedelta

        now = datetime.now().date()
        if not params.get("start_date"):
            params["start_date"] = now - relativedelta(years=1)
        if not params.get("end_date"):
            params["end_date"] = now

        return YFinanceEquityHistoricalQueryParams(**params)

    @staticmethod
    def extract_data(
        query: YFinanceEquityHistoricalQueryParams,
        credentials: dict[str, str] | None = None,
        **kwargs,
    ) -> "DataFrame":
        """Call yfinance helper and return clean standardized DataFrame.
        
        Column renaming is handled inside yf_download so this always
        returns lowercase standard field names - no COLUMN_MAP needed here.
        """
        from foliopp_yfinance.utils.helpers import yf_download

        return yf_download(
            symbol=query.symbol,
            exchange=query.exchange,
            start_date=query.start_date,
            end_date=query.end_date,
            interval=INTERVALS_DICT[query.interval],
            actions=query.include_actions,
            progress=query._progress,
            ignore_tz=query._ignore_tz,
            auto_adjust=query.adjusted,
        )

    @staticmethod
    def transform_data(
        query: YFinanceEquityHistoricalQueryParams,
        data: "DataFrame",
        **kwargs,
    ) -> list[YFinanceEquityHistoricalData]:
        """Map clean DataFrame -> YFinanceEquityHistoricalData.
        
        Columns are already renamed by yf_download so we just compute
        vwap, attach metadata, and validate into our model.
        """
        # Attach metadata
        data["symbol"] = query.symbol
        data["exchange"] = query.exchange
        data["currency"] = "INR"

        # Warn if any requested symbol returned no data (multi-symbol support)
        query_symbols = query.symbol.upper().split(",")
        if len(query_symbols) > 1:
            returned = data["symbol"].unique().tolist() if "symbol" in data.columns else []
            for sym in query_symbols:
                if sym not in returned:
                    warn(f"Data for '{sym}' was not found.")

        return [
            YFinanceEquityHistoricalData.model_validate(row)
            for row in data.to_dict("records")
        ]
