"""Abstract Fetcher - the TET pipeline every provider must implement.
- Providers implement either extract_data (sync) or aextract_data (async).
- If aextract_data is defined, it is aliased as extract_data automatically.
- fetch_data() is async; use fetch_data_sync() for synchronous callers.
"""

import asyncio
from typing import Any, Generic, TypeVar

from foliopp_core.provider.abstract.data import Data
from foliopp_core.provider.abstract.query_params import QueryParams

Q = TypeVar("Q", bound=QueryParams)
R = TypeVar("R")


async def _maybe_coroutine(fn, *args, **kwargs):
    """Call fn; if the result is a coroutine, await it."""
    result = fn(*args, **kwargs)
    if asyncio.iscoroutine(result):
        return await result
    return result


class Fetcher(Generic[Q, R]):
    """Abstract base class for all data fetchers.

    Every provider+datatype combination subclasses this and implements:
        1. transform_query()            - raw params dict → typed QueryParams
        2. extract_data() OR
           aextract_data() (async)      - hit the data source → raw data
        3. transform_data()             - raw data → our standard Data model

    If aextract_data is defined it takes precedence and is aliased to extract_data.

    Usage (async):
        result = await MyFetcher.fetch_data({"symbol": "RELIANCE", "exchange": "NSE"})

    Usage (sync):
        result = MyFetcher.fetch_data_sync({"symbol": "RELIANCE", "exchange": "NSE"})
    """

    require_credentials: bool = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> Q:
        """Validate and convert raw params dict into a typed QueryParams object."""
        raise NotImplementedError

    @staticmethod
    async def aextract_data(query: Q, credentials: dict[str, str] | None = None, **kwargs) -> Any:
        """Asynchronously hit the data source. Override this for async providers."""

    @staticmethod
    def extract_data(query: Q, credentials: dict[str, str] | None = None, **kwargs) -> Any:
        """Synchronously hit the data source. Override this for sync providers."""

    @staticmethod
    def transform_data(query: Q, data: Any, **kwargs) -> R:
        """Map raw provider data into our standard Data model."""
        raise NotImplementedError

    def __init_subclass__(cls, **kwargs):
        """If aextract_data is overridden, alias it as extract_data."""
        super().__init_subclass__(**kwargs)
        if cls.aextract_data is not Fetcher.aextract_data:
            # async provider - alias so extract_data always works
            cls.extract_data = cls.aextract_data  # type: ignore[method-assign]
        elif cls.extract_data is Fetcher.extract_data:
            raise NotImplementedError(
                f"{cls.__name__} must implement either extract_data() or aextract_data()"
            )

    @classmethod
    async def fetch_data(
        cls,
        params: dict[str, Any],
        credentials: dict[str, str] | None = None,
        **kwargs,
    ) -> R:
        """Run the full TET pipeline (async)."""
        query = cls.transform_query(params=params)
        data = await _maybe_coroutine(cls.extract_data, query=query, credentials=credentials, **kwargs)
        return cls.transform_data(query=query, data=data, **kwargs)

    @classmethod
    def fetch_data_sync(
        cls,
        params: dict[str, Any],
        credentials: dict[str, str] | None = None,
        **kwargs,
    ) -> R:
        """Run the full TET pipeline synchronously (convenience wrapper)."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # Inside an existing event loop (e.g. Jupyter) - run in a thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(asyncio.run, cls.fetch_data(params, credentials, **kwargs))
                return future.result()
        return asyncio.run(cls.fetch_data(params, credentials, **kwargs))
