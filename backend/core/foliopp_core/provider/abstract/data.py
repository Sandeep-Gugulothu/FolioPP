"""Base Data model."""

from pydantic import BaseModel, ConfigDict


class Data(BaseModel):
    """Base class for all output data models. Every provider's data must inherit from this."""

    __alias_dict__: dict[str, str] = {}

    model_config = ConfigDict(extra="allow", populate_by_name=True)
