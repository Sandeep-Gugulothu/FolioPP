"""yfinance provider for FolioPP."""

from foliopp_core.provider.abstract.provider import Provider
from foliopp_yfinance.models.equity_historical import YFinanceEquityHistoricalFetcher
from foliopp_yfinance.models.equity_profile import YFinanceEquityProfileFetcher
from foliopp_yfinance.models.equity_quote import YFinanceEquityQuoteFetcher
from foliopp_yfinance.models.income_statement import YFinanceIncomeStatementFetcher

yfinance_provider = Provider(
    name="yfinance",
    description="Yahoo Finance data for Indian equities via .NS (NSE) and .BO (BSE) suffixes.",
    website="https://finance.yahoo.com",
    fetcher_dict={
        "EquityHistorical": YFinanceEquityHistoricalFetcher,
        "EquityProfile": YFinanceEquityProfileFetcher,
        "EquityQuote": YFinanceEquityQuoteFetcher,
        "IncomeStatement": YFinanceIncomeStatementFetcher,
    },
)
