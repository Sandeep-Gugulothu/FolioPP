"""Indian Equity Historical Price Standard Model.

This defines the guaranteed fields every provider must return for historical OHLCV data.
Providers extend these classes to add their own extra fields on top.
All prices are in INR.
"""

from datetime import date as dateType, datetime
from typing import Literal

from pydantic import Field, field_validator

from foliopp_core.provider.abstract.data import Data
from foliopp_core.provider.abstract.query_params import QueryParams


class EquityHistoricalQueryParams(QueryParams):
    """Standard query params for Indian equity historical price data."""

    symbol: str = Field(description="NSE/BSE ticker symbol e.g. RELIANCE, TCS, INFY")
    start_date: dateType | None = Field(default=None, description="Start date YYYY-MM-DD")
    end_date: dateType | None = Field(default=None, description="End date YYYY-MM-DD")
    interval: Literal["1d", "1wk", "1mo"] = Field(
        default="1d",
        description="Data interval. 1d=daily, 1wk=weekly, 1mo=monthly",
    )
    exchange: Literal["NSE", "BSE"] = Field(default="NSE", description="NSE or BSE")

    @field_validator("symbol", mode="before")
    @classmethod
    def to_upper(cls, v: str) -> str:
        return v.upper().strip()


class EquityHistoricalData(Data):
    """Standard output fields for Indian equity historical OHLCV.

    Every provider must map their raw data to these fields.
    All prices are in INR.
    """

    symbol: str = Field(description="Ticker symbol")
    date: dateType | datetime = Field(description="Trading date")
    open: float = Field(description="Opening price in INR")
    high: float = Field(description="Day high in INR")
    low: float = Field(description="Day low in INR")
    close: float = Field(description="Closing price in INR")
    volume: int | None = Field(default=None, description="Shares traded")
    exchange: str = Field(default="NSE", description="NSE or BSE")
    currency: str = Field(default="INR", description="Always INR")

    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, v):
        from dateutil import parser
        if isinstance(v, (dateType, datetime)):
            return v
        if ":" in str(v):
            return parser.isoparse(str(v))
        return parser.parse(str(v)).date()
