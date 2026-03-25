"""Company News Standard Model.

Mirrors OpenBB's CompanyNewsData/CompanyNewsQueryParams, adapted for Indian equities.
"""

from datetime import date as dateType, datetime
from typing import Any

from pydantic import Field, NonNegativeInt, field_validator

from foliopp_core.provider.abstract.data import Data
from foliopp_core.provider.abstract.query_params import QueryParams


class CompanyNewsQueryParams(QueryParams):
    """Company News Query."""

    symbol: str | None = Field(default=None, description="NSE/BSE ticker symbol e.g. RELIANCE, TCS")
    start_date: dateType | None = Field(default=None, description="Start date of the news search (YYYY-MM-DD)")
    end_date: dateType | None = Field(default=None, description="End date of the news search (YYYY-MM-DD)")
    limit: NonNegativeInt | None = Field(default=None, description="Maximum number of results to return")

    @field_validator("symbol", mode="before")
    @classmethod
    def symbols_validate(cls, v):
        """Validate and uppercase the symbol."""
        return v.upper() if v else None


class CompanyNewsData(Data):
    """Company News Data."""

    date: datetime = Field(description="Publication date and time of the article.")
    title: str = Field(description="Title of the article.")
    author: str | None = Field(default=None, description="Author of the article.")
    excerpt: str | None = Field(default=None, description="Excerpt of the article text.")
    body: str | None = Field(default=None, description="Body of the article text.")
    images: Any | None = Field(default=None, description="Images associated with the article.")
    url: str = Field(description="URL to the article.")
    symbols: str | None = Field(default=None, description="Symbols associated with the article.")
