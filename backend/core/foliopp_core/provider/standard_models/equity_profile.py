"""Indian Equity Profile Standard Model."""

from datetime import date as dateType

from pydantic import Field, field_validator

from foliopp_core.provider.abstract.data import Data
from foliopp_core.provider.abstract.query_params import QueryParams


class EquityProfileQueryParams(QueryParams):
    """Standard query params for Indian equity profile."""

    symbol: str = Field(description="NSE/BSE ticker symbol e.g. RELIANCE, TCS")

    @field_validator("symbol", mode="before")
    @classmethod
    def to_upper(cls, v: str) -> str:
        return v.upper().strip()


class EquityProfileData(Data):
    """Standard output fields for Indian equity profile/company info."""

    symbol: str = Field(description="Ticker symbol")
    name: str | None = Field(default=None, description="Company full name")
    exchange: str | None = Field(default=None, description="Exchange (NSE/BSE)")
    currency: str | None = Field(default=None, description="Trading currency")
    sector: str | None = Field(default=None, description="Sector")
    industry: str | None = Field(default=None, description="Industry")
    country: str | None = Field(default=None, description="Country of headquarters")
    city: str | None = Field(default=None, description="City of headquarters")
    address: str | None = Field(default=None, description="Street address")
    zip_code: str | None = Field(default=None, description="Postal code")
    phone: str | None = Field(default=None, description="Company phone number")
    website: str | None = Field(default=None, description="Company website URL")
    description: str | None = Field(default=None, description="Business description")
    employees: int | None = Field(default=None, description="Full-time employees")
    market_cap: int | None = Field(default=None, description="Market capitalization in INR")
    shares_outstanding: int | None = Field(default=None, description="Shares outstanding")
    shares_float: int | None = Field(default=None, description="Float shares")
    dividend_yield: float | None = Field(default=None, description="Dividend yield as decimal")
    beta: float | None = Field(default=None, description="Beta vs broad market")
    first_trade_date: dateType | None = Field(default=None, description="First trading date")
