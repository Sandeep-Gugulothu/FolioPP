"""INDmoney provider for FolioPP."""

from foliopp_core.provider.abstract.provider import Provider
from foliopp_indmoney.models.equity_historical import INDmoneyEquityHistoricalFetcher

indmoney_provider = Provider(
    name="indmoney",
    description="INDmoney (INDstocks) Algo Trading API for Indian Equities.",
    website="https://api-docs.indstocks.com",
    credentials=["access_token"],
    fetcher_dict={
        "EquityHistorical": INDmoneyEquityHistoricalFetcher,
    },
)
