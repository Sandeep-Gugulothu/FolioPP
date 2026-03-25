"""Indian Equity Quote Standard Model.

Guaranteed fields every provider must return for a live/latest quote.
All prices are in INR.
"""

from typing import Literal

from pydantic import Field, field_validator

from foliopp_core.provider.abstract.data import Data
from foliopp_core.provider.abstract.query_params import QueryParams


class EquityQuoteQueryParams(QueryParams):
    """Standard query params for Indian equity live quote."""

    symbol: str = Field(description="NSE/BSE ticker symbol")
    exchange: Literal["NSE", "BSE"] = Field(default="NSE", description="NSE or BSE")

    @field_validator("symbol", mode="before")
    @classmethod
    def to_upper(cls, v: str) -> str:
        return v.upper().strip()


class EquityQuoteData(Data):
    """Standard output fields for Indian equity live quote.

    All prices are in INR.
    """

    symbol: str = Field(description="Ticker symbol")
    name: str | None = Field(default=None, description="Company name")
    price: float = Field(description="Last traded price in INR")
    open: float | None = Field(default=None, description="Day open in INR")
    high: float | None = Field(default=None, description="Day high in INR")
    low: float | None = Field(default=None, description="Day low in INR")
    prev_close: float | None = Field(default=None, description="Previous close in INR")
    change: float | None = Field(default=None, description="Price change in INR")
    change_pct: float | None = Field(default=None, description="Price change in percent")
    volume: int | None = Field(default=None, description="Volume traded today")
    market_cap: float | None = Field(default=None, description="Market cap in INR")
    exchange: str = Field(default="NSE", description="NSE or BSE")
    currency: str = Field(default="INR", description="Always INR")
