"""FolioPP FastAPI backend - Institutional 4-Phase Architecture."""

from fastapi import FastAPI, HTTPException, Query
from datetime import datetime
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

# Client & Config Imports
from backend.config import settings
from backend.clients.redis import redis_client
from backend.agents.market_agent import market_agent
from backend.clients.postgres import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from fastapi import Depends
from backend.core.foliopp_core.database.models import PortfolioEntry, NSETicker, User, BulkDeal, IngestedBatch, AuditLog
from sqlalchemy import func

# Provider Imports
from foliopp_yfinance.models.equity_quote import YFinanceEquityQuoteFetcher
from foliopp_yfinance.models.equity_profile import YFinanceEquityProfileFetcher
from foliopp_yfinance.models.equity_historical import YFinanceEquityHistoricalFetcher
from foliopp_yfinance.models.company_news import YFinanceCompanyNewsFetcher
from foliopp_yfinance.models.income_statement import YFinanceIncomeStatementFetcher
from foliopp_yfinance.models.balance_sheet import YFinanceBalanceSheetFetcher
from foliopp_yfinance.models.cash_flow import YFinanceCashFlowFetcher
from foliopp_yfinance.models.key_metrics import YFinanceKeyMetricsFetcher
from foliopp_nse.models.deliverable import NSEDeliverableFetcher
from foliopp_nse.models.bulk_block_deals import NSEBulkBlockDealFetcher
from foliopp_nse.models.fii_dii import NSEFiiDiiFetcher
from foliopp_nse.models.india_vix import NSEIndiaVixFetcher
from foliopp_nse.models.corporate_actions import NSECorporateActionFetcher
from foliopp_nse.models.event_calendar import NSEEventCalendarFetcher
from foliopp_nse.models.market_movers import NSEMarketMoverFetcher, NSEIndexSnapshotFetcher
from foliopp_nse.models.short_selling import NSEShortSellingFetcher
from foliopp_nse.models.price_volume import NSEPriceVolumeFetcher
from foliopp_nse.models.financial_results import NSEFinancialResultFetcher
from foliopp_nse.models.most_active import NSEMostActiveFetcher
from foliopp_nse.models.total_traded import NSETotalTradedFetcher
from foliopp_nse.models.fno_equity_list import NSEFnoEquityListFetcher
from foliopp_indmoney.models.equity_historical import INDmoneyEquityHistoricalFetcher
from foliopp_nse.models.index_equity_list import NSEIndexEquityListFetcher
from foliopp_core.provider.utils.errors import EmptyDataError

app = FastAPI(
    title=settings.APP_NAME, 
    version=settings.APP_VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    """Phase 4: Serving Initialization."""
    redis = await redis_client.connect()
    FastAPICache.init(RedisBackend(redis), prefix="foliopp-cache")
    
    # Ensure PostgreSQL tables exist (Institutional Persistence)
    try:
        from backend.clients.postgres import engine, Base
        from backend.core.foliopp_core.database import models # Ensure registration
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"Postgres Sync Warning: {e}")

    try:
        from backend.clients.minio import minio_client
        await minio_client.ensure_bucket(settings.MINIO_BUCKET_RAW)
    except Exception as e:
        print(f"MinIO Startup Warning: {e}. Dashboard will still run.")

    # Trigger Automatic DRL Experience Evaluation & Update (Phase 4: Optimization)
    # This runs a background loop to retrain the neural policy weights
    async def run_drl_cycle():
        from backend.processors.drl_trainer import drl_trainer
        while True:
            await drl_trainer.run_automatic_cycle()
            await asyncio.sleep(3600) # Re-training cycle every hour
            
    asyncio.create_task(run_drl_cycle())

# Endpoints are decentralized but maintained at the end of the file or in dedicated routers.

# ── Equity Provider Endpoints ────────────────────────────────────────────────

# ── Equity Provider Endpoints ────────────────────────────────────────────────

@app.get("/equity/quote")
@cache(expire=300)
async def equity_quote(symbol: str = Query(...), exchange: str = Query("NSE")):
    try:
        result = await YFinanceEquityQuoteFetcher.fetch_data(
            {"symbol": symbol, "exchange": exchange}, {}
        )
        return result.model_dump()
    except EmptyDataError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/equity/profile")
@cache(expire=3600)
async def equity_profile(symbol: str = Query(...), exchange: str = Query("NSE")):
    try:
        result = await YFinanceEquityProfileFetcher.fetch_data(
            {"symbol": symbol, "exchange": exchange}, {}
        )
        return result[0].model_dump()
    except EmptyDataError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/equity/historical")
@cache(expire=600)
async def equity_historical(
    symbol: str = Query(...),
    exchange: str = Query("NSE"),
    start_date: str = Query(None),
    end_date: str = Query(None),
    interval: str = Query("1d"),
):
    try:
        result = await YFinanceEquityHistoricalFetcher.fetch_data(
            {
                "symbol": symbol,
                "exchange": exchange,
                "start_date": start_date,
                "end_date": end_date,
                "interval": interval,
            },
            {},
        )
        return [r.model_dump() for r in result]
    except EmptyDataError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/equity/technical-analysis")
async def equity_technical_analysis(symbol: str = Query(...), exchange: str = Query("NSE")):
    """Generates the manual-indicators Plotly chart using Python-side calculations."""
    print(f"📡 Neural Request V2: Generating Technical Analysis for {symbol} ({exchange})...")
    from backend.processors.technical_analyzer import technical_analyzer
    try:
        # 1. Fetch historical data
        hist_result = await YFinanceEquityHistoricalFetcher.fetch_data(
            {"symbol": symbol, "exchange": exchange, "interval": "1d"}, {}
        )
        data = [r.model_dump() for r in hist_result]
        
        # 2. Generate Plotly JSON
        fig_json = technical_analyzer.generate_technical_plot(data, symbol)
        return fig_json
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/equity/news")
@cache(expire=300)
async def equity_news(symbol: str = Query(...), exchange: str = Query("NSE")):
    try:
        result = await YFinanceCompanyNewsFetcher.fetch_data(
            {"symbol": symbol, "exchange": exchange}, {}
        )
        return [r.model_dump() for r in result]
    except EmptyDataError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/market/news")
@cache(expire=600)
async def market_news():
    """Aggregates latest news for major market indices and drivers."""
    from foliopp_yfinance.models.company_news import YFinanceCompanyNewsFetcher
    import asyncio
    
    # 🌍 High-impact global and local tickers
    major_tickers = ["^NSEI", "^BSESN", "RELIANCE.NS", "AAPL", "BTC-USD"]
    
    async def fetch_item(t):
        try:
            res = await YFinanceCompanyNewsFetcher.fetch_data({"symbol": t, "exchange": "NSE"}, {})
            results = []
            for r in res[:5]: # Top 5 per ticker
                item = r.model_dump()
                item['source_ticker'] = t # Track where it came from
                results.append(item)
            return results
        except: return []

    all_results = await asyncio.gather(*[fetch_item(t) for t in major_tickers])
    all_news = [item for sublist in all_results for item in sublist]
    
    # Simple deduplication based on title
    seen = set()
    unique_news = []
    for n in all_news:
        if n['title'] not in seen:
            seen.add(n['title'])
            unique_news.append(n)
            
    return sorted(unique_news, key=lambda x: x.get('provider_publish_time', 0), reverse=True)

@app.get("/equity/news/analyze-stream")
async def analyze_news_stream(symbol: str = Query(...), exchange: str = Query("NSE"), news_index: int = Query(0)):
    """Streams the deterministic, rule-based NLP analysis for a specific news item."""
    from fastapi.responses import StreamingResponse
    from backend.processors.streaming_classifier import stream_rule_based_analysis
    import json

    async def event_generator():
        # Fetch current news items
        news_items = await YFinanceCompanyNewsFetcher.fetch_data({"symbol": symbol, "exchange": exchange}, {})
        
        if news_index >= len(news_items):
            yield f"data: {json.dumps({'error': 'News index out of range'})}\n\n"
            return

        news = news_items[news_index]
        headline = f"{news.title}. {news.summary}"
        
        # Stream the rule-based logic (fast, deterministic, explainable)
        async for part in stream_rule_based_analysis(headline, symbol):
            yield f"data: {json.dumps(part)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/equity/financials")
@cache(expire=3600)
async def equity_financials(
    symbol: str = Query(...),
    exchange: str = Query("NSE"),
    period: str = Query("annual"),
    limit: int = Query(4),
):
    try:
        result = await YFinanceIncomeStatementFetcher.fetch_data(
            {"symbol": symbol, "exchange": exchange, "period": period, "limit": limit},
            {},
        )
        return [r.model_dump() for r in result]
    except EmptyDataError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/equity/balance-sheet")
@cache(expire=3600)
async def equity_balance_sheet(
    symbol: str = Query(...),
    exchange: str = Query("NSE"),
    period: str = Query("annual"),
    limit: int = Query(4),
):
    try:
        result = await YFinanceBalanceSheetFetcher.fetch_data(
            {"symbol": symbol, "exchange": exchange, "period": period, "limit": limit},
            {},
        )
        return [r.model_dump() for r in result]
    except EmptyDataError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/equity/cash-flow")
@cache(expire=3600)
async def equity_cash_flow(
    symbol: str = Query(...),
    exchange: str = Query("NSE"),
    period: str = Query("annual"),
    limit: int = Query(4),
):
    try:
        result = await YFinanceCashFlowFetcher.fetch_data(
            {"symbol": symbol, "exchange": exchange, "period": period, "limit": limit},
            {},
        )
        return [r.model_dump() for r in result]
    except EmptyDataError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/equity/key-metrics")
@cache(expire=3600)
async def equity_key_metrics(
    symbol: str = Query(...),
    exchange: str = Query("NSE"),
):
    try:
        result = await YFinanceKeyMetricsFetcher.fetch_data(
            {"symbol": symbol, "exchange": exchange},
            {},
        )
        return result[0].model_dump()
    except EmptyDataError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── NSE Provider Endpoints ────────────────────────────────────────────────────

@app.get("/nse/deliverable")
@cache(expire=300)
async def nse_deliverable(
    symbol: str = Query(...),
    from_date: str = Query(None),
    to_date: str = Query(None),
    period: str = Query("1M"),
):
    try:
        result = await NSEDeliverableFetcher.fetch_data(
            {"symbol": symbol, "from_date": from_date, "to_date": to_date, "period": period}, {}
        )
        return [r.model_dump() for r in result]
    except EmptyDataError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/nse/deals")
@cache(expire=600)
async def nse_deals(
    deal_type: str = Query("bulk"),
    from_date: str = Query(None),
    to_date: str = Query(None),
    period: str = Query("1M"),
):
    """
    Returns enriched Bulk/Block deals with Signal Priority (Phase 1 & 2).
    """
    try:
        from backend.core.foliopp_core.pipeline.nse_bulk_ingestion import bulk_ingestor
        
        # This will fetch, enrich (Promoter & % Equity), and save to Postgres
        result = await bulk_ingestor.run({
            "deal_type": deal_type, 
            "from_date": from_date, 
            "to_date": to_date, 
            "period": period
        })
        return [r.model_dump() for r in result]

    except EmptyDataError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/institutional/latest-bulk-deals")
@cache(expire=3600)
async def latest_market_bulk_deals(limit: int = Query(20)):
    """
    Returns market-wide institutional bulk deals for the streaming frontend panel.
    Uses aggressive caching to prevent redundancy.
    """
    try:
        from backend.core.foliopp_core.pipeline.nse_bulk_ingestion import bulk_ingestor
        
        # Pull 1 month of global deals (no symbol)
        result = await bulk_ingestor.run({"period": "1M"})
        
        # Convert to list and sort by date desc
        deals = [r.model_dump() for r in result]
        sorted_deals = sorted(deals, key=lambda x: x.get('date', ''), reverse=True)
        
        return sorted_deals[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/nse/fii-dii")
@cache(expire=3600)
async def nse_fii_dii():
    try:
        result = await NSEFiiDiiFetcher.fetch_data({}, {})
        return [r.model_dump() for r in result]
    except EmptyDataError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/nse/india-vix")
@cache(expire=300)
async def nse_india_vix(
    from_date: str = Query(None),
    to_date: str = Query(None),
    period: str = Query("1M"),
):
    try:
        result = await NSEIndiaVixFetcher.fetch_data(
            {"from_date": from_date, "to_date": to_date, "period": period}, {}
        )
        return [r.model_dump() for r in result]
    except EmptyDataError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/nse/corporate-actions")
@cache(expire=3600)
async def nse_corporate_actions(
    symbol: str = Query(None),
    from_date: str = Query(None),
    to_date: str = Query(None),
    period: str = Query("3M"),
    fno_only: bool = Query(False),
):
    try:
        result = await NSECorporateActionFetcher.fetch_data(
            {"symbol": symbol, "from_date": from_date, "to_date": to_date,
             "period": period, "fno_only": fno_only}, {}
        )
        return [r.model_dump() for r in result]
    except EmptyDataError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/nse/events")
@cache(expire=3600)
async def nse_events(
    symbol: str = Query(None),
    from_date: str = Query(None),
    to_date: str = Query(None),
    period: str = Query("1M"),
    fno_only: bool = Query(False),
):
    try:
        result = await NSEEventCalendarFetcher.fetch_data(
            {"symbol": symbol, "from_date": from_date, "to_date": to_date,
             "period": period, "fno_only": fno_only}, {}
        )
        return [r.model_dump() for r in result]
    except EmptyDataError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/nse/market-movers")
@cache(expire=60)
async def nse_market_movers(mover_type: str = Query("gainer")):
    try:
        result = await NSEMarketMoverFetcher.fetch_data({"mover_type": mover_type}, {})
        return [r.model_dump() for r in result]
    except EmptyDataError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/nse/indices")
@cache(expire=60)
async def nse_indices():
    try:
        result = await NSEIndexSnapshotFetcher.fetch_data({}, {})
        return [r.model_dump() for r in result]
    except EmptyDataError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@app.get("/nse/short-selling")
@cache(expire=3600)
async def nse_short_selling(
    from_date: str = Query(None),
    to_date: str = Query(None),
    period: str = Query("1M"),
):
    try:
        result = await NSEShortSellingFetcher.fetch_data(
            {"from_date": from_date, "to_date": to_date, "period": period}, {}
        )
        return [r.model_dump() for r in result]
    except EmptyDataError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@app.get("/nse/price-volume")
@cache(expire=300)
async def nse_price_volume(
    symbol: str = Query(...),
    from_date: str = Query(None),
    to_date: str = Query(None),
    period: str = Query("1M"),
):
    try:
        result = await NSEPriceVolumeFetcher.fetch_data(
            {"symbol": symbol, "from_date": from_date, "to_date": to_date, "period": period}, {}
        )
        return [r.model_dump() for r in result]
    except EmptyDataError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/nse/financial-results")
@cache(expire=3600)
async def nse_financial_results(
    from_date: str = Query(None),
    to_date: str = Query(None),
    period: str = Query("1M"),
    fno_only: bool = Query(False),
    fin_period: str = Query("Quarterly"),
):
    try:
        result = await NSEFinancialResultFetcher.fetch_data(
            {"from_date": from_date, "to_date": to_date, "period": period,
             "fno_only": fno_only, "fin_period": fin_period}, {}
        )
        return [r.model_dump() for r in result]
    except EmptyDataError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/nse/most-active")
@cache(expire=300)
async def nse_most_active(fetch_by: str = Query("volume")):
    try:
        result = await NSEMostActiveFetcher.fetch_data({"fetch_by": fetch_by}, {})
        return [r.model_dump() for r in result]
    except EmptyDataError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/nse/total-traded")
@cache(expire=300)
async def nse_total_traded():
    try:
        result = await NSETotalTradedFetcher.fetch_data({}, {})
        return [r.model_dump() for r in result]
    except EmptyDataError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/nse/fno-list")
@cache(expire=86400)
async def nse_fno_list():
    try:
        result = await NSEFnoEquityListFetcher.fetch_data({}, {})
        return [r.model_dump() for r in result]
    except EmptyDataError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/nse/index-constituents")
@cache(expire=86400)
async def nse_index_constituents(index_name: str = Query(...)):
    try:
        result = await NSEIndexEquityListFetcher.fetch_data({"index_name": index_name}, {})
        return [r.model_dump() for r in result]
    except EmptyDataError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── INDmoney Provider Endpoints ───────────────────────────────────────────────

# ── Portfolio Management (Institutional Persistence) ───────────────────

@app.get("/api/portfolio")
async def get_portfolio(db: AsyncSession = Depends(get_db)):
    """Retrieve all holdings with real-time P&L calculation."""
    stmt = select(PortfolioEntry)
    result = await db.execute(stmt)
    holdings = result.scalars().all()
    
    enriched = []
    for h in holdings:
        try:
            quote = await YFinanceEquityQuoteFetcher.fetch_data({"symbol": h.symbol}, {})
            current_price = float(quote.price or 0)
            pnl = (current_price - h.avg_price) * h.units
            enriched.append({
                "symbol": h.symbol,
                "units": h.units,
                "avg_price": h.avg_price,
                "current_price": current_price,
                "pnl": pnl,
                "pnl_pct": (pnl / (h.avg_price * h.units)) * 100 if h.avg_price > 0 else 0,
                "sector": h.sector
            })
        except:
            enriched.append({
                "symbol": h.symbol, "units": h.units, "avg_price": h.avg_price,
                "current_price": h.avg_price, "pnl": 0, "pnl_pct": 0, "sector": h.sector
            })
    return enriched

@app.post("/api/portfolio")
async def add_holding(data: dict, db: AsyncSession = Depends(get_db)):
    """Add a new institutional investment to the DB."""
    symbol = data["symbol"]
    avg_price = data.get("avg_price")
    
    # 📡 Fallback: If no price given, use LTP
    if not avg_price:
        try:
            quote = await YFinanceEquityQuoteFetcher.fetch_data({"symbol": symbol}, {})
            avg_price = float(quote.price or 0)
        except:
            avg_price = 0
            
    entry = PortfolioEntry(
        symbol=symbol,
        units=data["units"],
        avg_price=avg_price,
        sector=data.get("sector", "Various")
    )
    db.add(entry)
    await db.commit()
    return {"status": "success", "id": entry.id}

@app.delete("/api/portfolio/{symbol}")
async def delete_holding(symbol: str, db: AsyncSession = Depends(get_db)):
    """Remove a counter from the institutional tracker."""
    await db.execute(delete(PortfolioEntry).where(PortfolioEntry.symbol == symbol))
    await db.commit()
    return {"status": "success"}

@app.get("/api/tickers/search")
async def search_tickers(q: str = Query(...), db: AsyncSession = Depends(get_db)):
    """Institutional Autocomplete for valid NSE/NASDAQ tickers."""
    stmt = select(NSETicker).where(NSETicker.symbol.ilike(f"%{q}%")).limit(10)
    result = await db.execute(stmt)
    return [{"symbol": t.symbol, "name": t.name} for t in result.scalars().all()]

@app.get("/api/admin/stats")
async def get_admin_stats(db: AsyncSession = Depends(get_db)):
    """Institutional System Status & DB Overview."""
    stats = {}
    models = {
        "users": User,
        "portfolio": PortfolioEntry,
        "tickers": NSETicker,
        "bulk_deals": BulkDeal,
        "raw_batches": IngestedBatch,
        "audit_logs": AuditLog
    }
    for key, model in models.items():
        res = await db.execute(select(func.count()).select_from(model))
        stats[key] = res.scalar()
    
    # Add system health mock (would be real in production)
    stats["latency"] = "14ms"
    stats["api_status"] = "HEALTHY"
    stats["last_sync"] = datetime.utcnow().isoformat()
    return stats

@app.get("/api/admin/raw/tickers")
async def get_raw_tickers(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Retrieve raw ticker metadata for technical audit."""
    stmt = select(NSETicker).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

@app.get("/api/admin/raw/deals")
async def get_raw_deals(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Retrieve raw Bulk/Block deals for technical audit."""
    stmt = select(BulkDeal).order_by(BulkDeal.trade_date.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

@app.get("/api/admin/raw/tickers/all")
async def get_all_tickers(db: AsyncSession = Depends(get_db)):
    """Retrieve all ticker metadata for raw dump."""
    stmt = select(NSETicker)
    result = await db.execute(stmt)
    return result.scalars().all()
@app.get("/indmoney/historical")
@cache(expire=600)
async def indmoney_historical(
    symbol: str = Query(...),
    exchange: str = Query("NSE"),
    start_date: str = Query(None),
    end_date: str = Query(None),
    interval: str = Query("1d"),
):
    try:
        result = await INDmoneyEquityHistoricalFetcher.fetch_data(
            {
                "symbol": symbol,
                "exchange": exchange,
                "start_date": start_date,
                "end_date": end_date,
                "interval": interval,
            },
            {},
        )
        return [r.model_dump() for r in result]
    except EmptyDataError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Serving initialization is handled at the end of the file.
@app.get("/")
async def root():
    return {"status": "Institutional Terminal Backend - 4 Phase Architecture Active"}

@app.post("/intelligence/run")
async def run_analysis(payload: dict):
    """Executes AI-generated Python code and returns the plot/output (Phase 3)."""
    from backend.api.executor import execute_python_plot
    code = payload.get("code", "")
    if not code:
        raise HTTPException(status_code=400, detail="No code provided")
    result = execute_python_plot(code)
    return result

# ── Intelligence Persistent History ──────────────────────────────────────────

@app.get("/intelligence/sessions")
async def get_sessions(db: AsyncSession = Depends(get_db)):
    """Return all unique research sessions with metadata."""
    from backend.core.foliopp_core.database.models import ChatMessage
    from sqlalchemy import func
    stmt = (
        select(
            ChatMessage.session_id,
            func.max(ChatMessage.timestamp).label("last_active"),
            func.min(ChatMessage.content).label("title")
        )
        .group_by(ChatMessage.session_id)
        .order_by(func.max(ChatMessage.timestamp).desc())
    )
    result = await db.execute(stmt)
    sessions = result.all()
    return [{"session_id": s[0], "last_active": s[1], "title": s[2][:40] + "..." if s[2] else "Untitled Research"} for s in sessions]

@app.get("/intelligence/history")
async def get_chat_history(session_id: str = Query("default"), db: AsyncSession = Depends(get_db)):
    """Retrieve institutional chat history for a research session."""
    from backend.core.foliopp_core.database.models import ChatMessage
    stmt = (
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.timestamp.asc())
    )
    result = await db.execute(stmt)
    messages = result.scalars().all()
    return [{"role": m.role, "content": m.content, "thoughts": m.thoughts, "timestamp": m.timestamp} for m in messages]

@app.get("/intelligence/chat")
async def chat(query: str, session_id: str = Query("default"), active_symbol: str = Query(None)):
    """Orchestrates AI reasoning with persistent session context."""
    from fastapi.responses import StreamingResponse
    try:
        return StreamingResponse(
            market_agent.chat_stream(query, active_symbol=active_symbol, session_id=session_id), 
            media_type="text/plain"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
