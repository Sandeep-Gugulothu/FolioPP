"""Provider class - registers a provider and its fetchers."""

from foliopp_core.provider.abstract.fetcher import Fetcher


class Provider:
    """Entry point for a data provider. Registers its name and all its fetchers.

    Example:
        yfinance_provider = Provider(
            name="yfinance",
            description="Yahoo Finance",
            fetcher_dict={
                "EquityHistorical": YFinanceEquityHistoricalFetcher,
                "EquityQuote": YFinanceEquityQuoteFetcher,
            },
        )
    """

    def __init__(
        self,
        name: str,
        description: str,
        website: str | None = None,
        credentials: list[str] | None = None,
        fetcher_dict: dict[str, type[Fetcher]] | None = None,
    ) -> None:
        self.name = name
        self.description = description
        self.website = website
        self.credentials = credentials or []
        self.fetcher_dict = fetcher_dict or {}
