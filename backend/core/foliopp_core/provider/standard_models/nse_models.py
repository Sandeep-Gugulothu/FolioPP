"""NSE India Standard Models."""

from datetime import date as dateType, datetime
from typing import Literal

from pydantic import Field, field_validator

from foliopp_core.provider.abstract.data import Data
from foliopp_core.provider.abstract.query_params import QueryParams


# ── Shared base ──────────────────────────────────────────────────────────────

class NSEDateRangeQueryParams(QueryParams):
    from_date: dateType | None = Field(default=None, description="Start date YYYY-MM-DD")
    to_date: dateType | None = Field(default=None, description="End date YYYY-MM-DD")
    period: Literal["1D", "1W", "1M", "3M", "6M", "1Y"] | None = Field(
        default="1M", description="Shorthand period if from/to not provided"
    )


class NSESymbolDateRangeQueryParams(NSEDateRangeQueryParams):
    symbol: str = Field(description="NSE ticker symbol e.g. SBIN")

    @field_validator("symbol", mode="before")
    @classmethod
    def to_upper(cls, v: str) -> str:
        return v.upper().strip()


# ── Price Volume & Deliverable ────────────────────────────────────────────────

class DeliverablePositionData(Data):
    symbol: str
    series: str | None = Field(default=None)
    date: dateType
    prev_close: float | None = Field(default=None)
    open: float | None = Field(default=None)
    high: float | None = Field(default=None)
    low: float | None = Field(default=None)
    close: float | None = Field(default=None)
    avg_price: float | None = Field(default=None)
    total_traded_qty: float | None = Field(default=None)
    turnover: float | None = Field(default=None)
    trades: float | None = Field(default=None)
    deliverable_qty: float | None = Field(default=None)
    pct_delivery: float | None = Field(default=None, description="% of traded qty that was delivered")


# ── Bulk & Block Deals ────────────────────────────────────────────────────────

class BulkBlockDealData(Data):
    date: dateType
    symbol: str
    security_name: str | None = Field(default=None)
    client_name: str | None = Field(default=None)
    buy_sell: str | None = Field(default=None)
    quantity: float | None = Field(default=None)
    price: float | None = Field(default=None)
    deal_type: Literal["bulk", "block"] = Field(default="bulk")
    # Signal fields for Track 6
    is_promoter: bool = Field(default=False)
    pct_equity: float | None = Field(default=None)
    priority: int = Field(default=0) # 1 for high priority


class BulkBlockDealQueryParams(NSEDateRangeQueryParams):
    deal_type: Literal["bulk", "block"] = Field(default="bulk")


# ── Short Selling ─────────────────────────────────────────────────────────────

class ShortSellingData(Data):
    date: dateType
    symbol: str
    security_name: str | None = Field(default=None)
    quantity: float | None = Field(default=None)


class ShortSellingQueryParams(NSEDateRangeQueryParams):
    pass


# ── PE Ratio ──────────────────────────────────────────────────────────────────

class PERatioData(Data):
    index_name: str
    date: dateType
    pe: float | None = Field(default=None)
    pb: float | None = Field(default=None)
    div_yield: float | None = Field(default=None)


class PERatioQueryParams(QueryParams):
    trade_date: str = Field(description="Trade date in dd-mm-YYYY format")


# ── Price Volume Data ─────────────────────────────────────────────────────────

class PriceVolumeData(Data):
    symbol: str
    series: str | None = Field(default=None)
    date: dateType
    prev_close: float | None = Field(default=None)
    open: float | None = Field(default=None)
    high: float | None = Field(default=None)
    low: float | None = Field(default=None)
    close: float | None = Field(default=None)
    avg_price: float | None = Field(default=None)
    total_traded_qty: float | None = Field(default=None)
    turnover: float | None = Field(default=None)
    trades: float | None = Field(default=None)
    deliverable_qty: float | None = Field(default=None)
    pct_delivery: float | None = Field(default=None)


# ── Financial Results ─────────────────────────────────────────────────────────

class FinancialResultData(Data):
    symbol: str
    company_name: str | None = Field(default=None)
    series: str | None = Field(default=None)
    fin_period: str | None = Field(default=None)
    from_date: dateType | None = Field(default=None)
    to_date: dateType | None = Field(default=None)
    expenditure: float | None = Field(default=None)
    income: float | None = Field(default=None)
    profit_before_tax: float | None = Field(default=None)
    profit_after_tax: float | None = Field(default=None)
    eps: float | None = Field(default=None)
    broadcast_date: dateType | None = Field(default=None)
    xbrl_link: str | None = Field(default=None)


class FinancialResultQueryParams(NSEDateRangeQueryParams):
    fno_only: bool = Field(default=False)
    fin_period: Literal["Quarterly", "Annual", "Half-Yearly", "Others"] = Field(default="Quarterly")


# ── Most Active Equities ──────────────────────────────────────────────────────

class MostActiveData(Data):
    symbol: str
    company_name: str | None = Field(default=None)
    ltp: float | None = Field(default=None)
    change: float | None = Field(default=None)
    change_pct: float | None = Field(default=None)
    volume: float | None = Field(default=None)
    value: float | None = Field(default=None)
    fetch_by: str | None = Field(default=None)


class MostActiveQueryParams(QueryParams):
    fetch_by: Literal["volume", "value"] = Field(default="volume")


# ── Total Traded Stocks ───────────────────────────────────────────────────────

class TotalTradedData(Data):
    advances: int | None = Field(default=None)
    declines: int | None = Field(default=None)
    unchanged: int | None = Field(default=None)
    total: int | None = Field(default=None)


class TotalTradedQueryParams(QueryParams):
    pass


# ── FnO Equity List ───────────────────────────────────────────────────────────

class FnoEquityData(Data):
    symbol: str
    company_name: str | None = Field(default=None)
    series: str | None = Field(default=None)
    isin: str | None = Field(default=None)


class FnoEquityQueryParams(QueryParams):
    pass


# ── Index Equity List ─────────────────────────────────────────────────────────

class IndexEquityData(Data):
    symbol: str
    company_name: str | None = Field(default=None)
    series: str | None = Field(default=None)
    isin: str | None = Field(default=None)
    industry: str | None = Field(default=None)


class IndexEquityQueryParams(QueryParams):
    index_name: str = Field(description="Index name e.g. NIFTY MIDCAP 150")


# ── India VIX ─────────────────────────────────────────────────────────────────

class IndiaVixData(Data):
    date: dateType
    open: float | None = Field(default=None)
    high: float | None = Field(default=None)
    low: float | None = Field(default=None)
    close: float | None = Field(default=None)
    prev_close: float | None = Field(default=None)
    change: float | None = Field(default=None)
    change_pct: float | None = Field(default=None)


# ── FII / DII Activity ────────────────────────────────────────────────────────

class FiiDiiData(Data):
    date: dateType | None = Field(default=None)
    category: str = Field(description="FII or DII")
    buy_value: float | None = Field(default=None, description="Buy value in Cr")
    sell_value: float | None = Field(default=None, description="Sell value in Cr")
    net_value: float | None = Field(default=None, description="Net buy/sell in Cr")


class FiiDiiQueryParams(QueryParams):
    pass


# ── Corporate Actions ─────────────────────────────────────────────────────────

class CorporateActionData(Data):
    symbol: str
    company_name: str | None = Field(default=None)
    series: str | None = Field(default=None)
    face_value: float | None = Field(default=None)
    purpose: str | None = Field(default=None, description="Dividend/Bonus/Split etc.")
    ex_date: dateType | None = Field(default=None)
    record_date: dateType | None = Field(default=None)
    bc_start_date: dateType | None = Field(default=None)
    bc_end_date: dateType | None = Field(default=None)


class CorporateActionQueryParams(NSEDateRangeQueryParams):
    symbol: str | None = Field(default=None, description="Filter by symbol (optional)")
    fno_only: bool = Field(default=False)

    @field_validator("symbol", mode="before")
    @classmethod
    def to_upper(cls, v):
        return v.upper().strip() if v else None


# ── Event Calendar ────────────────────────────────────────────────────────────

class EventCalendarData(Data):
    symbol: str
    company_name: str | None = Field(default=None)
    purpose: str | None = Field(default=None, description="Board meeting/Results/AGM etc.")
    date: dateType | None = Field(default=None)
    description: str | None = Field(default=None)


class EventCalendarQueryParams(NSEDateRangeQueryParams):
    symbol: str | None = Field(default=None)
    fno_only: bool = Field(default=False)

    @field_validator("symbol", mode="before")
    @classmethod
    def to_upper(cls, v):
        return v.upper().strip() if v else None


# ── Market Movers ─────────────────────────────────────────────────────────────

class MarketMoverData(Data):
    symbol: str
    company_name: str | None = Field(default=None)
    ltp: float | None = Field(default=None, description="Last traded price")
    change: float | None = Field(default=None)
    change_pct: float | None = Field(default=None)
    volume: float | None = Field(default=None)
    value: float | None = Field(default=None)
    category: str | None = Field(default=None, description="NIFTY50/NIFTYNEXT50 etc.")
    mover_type: Literal["gainer", "loser"] = Field(default="gainer")


class MarketMoverQueryParams(QueryParams):
    mover_type: Literal["gainer", "loser"] = Field(default="gainer")


# ── Index Snapshot ────────────────────────────────────────────────────────────

class IndexSnapshotData(Data):
    index_name: str
    last: float | None = Field(default=None)
    change: float | None = Field(default=None)
    change_pct: float | None = Field(default=None)
    open: float | None = Field(default=None)
    high: float | None = Field(default=None)
    low: float | None = Field(default=None)
    prev_close: float | None = Field(default=None)
    year_high: float | None = Field(default=None)
    year_low: float | None = Field(default=None)
    advances: int | None = Field(default=None)
    declines: int | None = Field(default=None)
    unchanged: int | None = Field(default=None)
    pe: float | None = Field(default=None)
    pb: float | None = Field(default=None)
    div_yield: float | None = Field(default=None)


class IndexSnapshotQueryParams(QueryParams):
    pass


# ── Index Historical Data ─────────────────────────────────────────────────────

class IndexHistoricalData(Data):
    index_name: str
    date: dateType
    open: float | None = Field(default=None)
    high: float | None = Field(default=None)
    low: float | None = Field(default=None)
    close: float | None = Field(default=None)
    volume: float | None = Field(default=None)
    turnover: float | None = Field(default=None)


class IndexHistoricalQueryParams(NSEDateRangeQueryParams):
    index_name: str = Field(description="NSE Index Name e.g. NIFTY 50")

# ── Corporate Announcements ───────────────────────────────────────────────────

class CorporateAnnouncementData(Data):
    symbol: str
    company_name: str | None = Field(default=None)
    subject: str | None = Field(default=None)
    details: str | None = Field(default=None)
    broadcast_date: dateType | datetime | None = Field(default=None)
    attainment_date: dateType | datetime | None = Field(default=None)
    attachment_link: str | None = Field(default=None)


class CorporateAnnouncementQueryParams(NSEDateRangeQueryParams):
    symbol: str | None = Field(default=None)


# ── Board Meetings ────────────────────────────────────────────────────────────

class BoardMeetingData(Data):
    symbol: str
    company_name: str | None = Field(default=None)
    bm_date: dateType | None = Field(default=None)
    purpose: str | None = Field(default=None)
    details: str | None = Field(default=None)


class BoardMeetingQueryParams(NSEDateRangeQueryParams):
    symbol: str | None = Field(default=None)


# ── Shareholding Pattern ───────────────────────────────────────────────────────

class ShareholdingPatternData(Data):
    symbol: str
    company_name: str | None = Field(default=None)
    quarter_ending: str | None = Field(default=None)
    promoter_holding: float | None = Field(default=None)
    public_holding: float | None = Field(default=None)
    other_holding: float | None = Field(default=None)
    total_shares: float | None = Field(default=None)
    details_url: str | None = Field(default=None)


class ShareholdingPatternQueryParams(QueryParams):
    symbol: str


# ── Shareholding Pattern SDD ───────────────────────────────────────────────────

class ShareholdingPatternSDDData(Data):
    symbol: str
    company_name: str | None = Field(default=None)
    pan_number: str | None = Field(default=None)
    shares_held: float | None = Field(default=None)
    percentage_holding: float | None = Field(default=None)
    date_of_reporting: dateType | None = Field(default=None)
    is_promoter_group: bool = Field(default=False)


class ShareholdingPatternSDDQueryParams(QueryParams):
    symbol: str


# ── Issuer Offer Documents ──────────────────────────────────────────────────────

class IssuerOfferDocumentData(Data):
    symbol: str | None = Field(default=None)
    company_name: str | None = Field(default=None)
    issue_type: str | None = Field(default=None)
    issue_period: str | None = Field(default=None)
    ipo_status: str | None = Field(default=None)
    document_link: str | None = Field(default=None)
    listing_date: str | None = Field(default=None)


class IssuerOfferDocumentQueryParams(QueryParams):
    symbol: str | None = Field(default=None)


# ── Integrated Filings ─────────────────────────────────────────────────────────

class IntegratedFilingData(Data):
    symbol: str
    company_name: str | None = Field(default=None)
    filing_type: str | None = Field(default=None) # Financials or Governance
    period: str | None = Field(default=None)
    submission_date: dateType | None = Field(default=None)
    xbrl_link: str | None = Field(default=None)
    pdf_link: str | None = Field(default=None)


class IntegratedFilingQueryParams(NSEDateRangeQueryParams):
    symbol: str | None = Field(default=None)


# ── Scheme of Arrangement ──────────────────────────────────────────────────────

class SchemeOfArrangementData(Data):
    symbol: str
    company_name: str | None = Field(default=None)
    subject: str | None = Field(default=None)
    filing_date: dateType | None = Field(default=None)
    document_link: str | None = Field(default=None)


class SchemeOfArrangementQueryParams(NSEDateRangeQueryParams):
    symbol: str | None = Field(default=None)


# ── Insider Trading ────────────────────────────────────────────────────────────

class InsiderTradingData(Data):
    symbol: str
    company_name: str | None = Field(default=None)
    acquirer_name: str | None = Field(default=None)
    category_of_person: str | None = Field(default=None)
    transaction_type: str | None = Field(default=None)
    shares_quantity: float | None = Field(default=None)
    value_of_shares: float | None = Field(default=None)
    transaction_date: dateType | None = Field(default=None)
    broadcast_date: dateType | None = Field(default=None)


class InsiderTradingQueryParams(NSEDateRangeQueryParams):
    symbol: str | None = Field(default=None)


# ── Postal Ballot ──────────────────────────────────────────────────────────────

class PostalBallotData(Data):
    symbol: str
    company_name: str | None = Field(default=None)
    purpose: str | None = Field(default=None)
    broadcast_date: dateType | None = Field(default=None)
    attachment_link: str | None = Field(default=None)


class PostalBallotQueryParams(NSEDateRangeQueryParams):
    symbol: str | None = Field(default=None)
