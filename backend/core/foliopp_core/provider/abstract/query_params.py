"""Base QueryParams model."""

from pydantic import BaseModel, ConfigDict


class QueryParams(BaseModel):
    """Base class for all query input parameters. Every provider's query must inherit from this."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)
