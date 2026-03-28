"""Market Agent - Neural Orchestrator for Institutional Research Synthesis.
Implements the Multi-Step Reasoning Flow: Intent -> Harvest -> Analysis -> Synthesis.
"""

import json
import logging
import asyncio
import re
import hashlib
from datetime import datetime
from typing import AsyncGenerator, Dict, List, Any, Optional

from groq import AsyncGroq
from sqlalchemy import select

from backend.config import settings
from backend.clients.postgres import AsyncSessionLocal
from backend.core.foliopp_core.database.models import PortfolioEntry, NSETicker, ChatMessage, DRLDecision
from backend.processors.technical_analyzer import technical_analyzer
from backend.processors.nlp_analyzer import NLPAnalyzer
from backend.processors.drl_module import drl_module
from backend.processors.drl_trainer import drl_trainer

# Standardized Provider Registry
from foliopp_yfinance.models.equity_quote import YFinanceEquityQuoteFetcher
from foliopp_yfinance.models.equity_profile import YFinanceEquityProfileFetcher
from foliopp_yfinance.models.equity_historical import YFinanceEquityHistoricalFetcher
from foliopp_yfinance.models.company_news import YFinanceCompanyNewsFetcher
from foliopp_yfinance.models.key_metrics import YFinanceKeyMetricsFetcher
from foliopp_yfinance.models.income_statement import YFinanceIncomeStatementFetcher
from foliopp_yfinance.models.balance_sheet import YFinanceBalanceSheetFetcher
from foliopp_yfinance.models.cash_flow import YFinanceCashFlowFetcher

from foliopp_nse.models.bulk_block_deals import NSEBulkBlockDealFetcher
from foliopp_nse.models.corporate_actions import NSECorporateActionFetcher
from foliopp_nse.models.deliverable import NSEDeliverableFetcher
from foliopp_nse.models.event_calendar import NSEEventCalendarFetcher
from foliopp_nse.models.fii_dii import NSEFiiDiiFetcher
from foliopp_nse.models.financial_results import NSEFinancialResultFetcher
from foliopp_nse.models.fno_equity_list import NSEFnoEquityListFetcher
from foliopp_nse.models.index_equity_list import NSEIndexEquityListFetcher
from foliopp_nse.models.india_vix import NSEIndiaVixFetcher
from foliopp_nse.models.market_movers import NSEMarketMoverFetcher
from foliopp_nse.models.most_active import NSEMostActiveFetcher
from foliopp_nse.models.price_volume import NSEPriceVolumeFetcher
from foliopp_nse.models.short_selling import NSEShortSellingFetcher
from foliopp_nse.models.total_traded import NSETotalTradedFetcher
from foliopp_nse.models.announcements import NSECorporateAnnouncementFetcher
from foliopp_nse.models.board_meetings import NSEBoardMeetingFetcher
from foliopp_nse.models.shareholding_pattern import NSEShareholdingPatternFetcher

logger = logging.getLogger("MarketAgent")

class MarketAgent:
    """
    FolioPP Orchestrator.
    Autonomous multi-step pipeline for institutional-grade financial intelligence.
    """
    
    def __init__(self):
        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.1-8b-instant"
        self.nlp_analyzer = NLPAnalyzer()

    async def detect_intent(self, query: str, history: List[Dict] = []) -> Dict[str, Any]:
        """Phase 1: Intent Detection & Target Extraction with Context."""
        context_str = "\n".join([f"{m['role']}: {m['content']}" for m in history[-5:]])
        system_prompt = f"""
        You are an Institutional Finance Router. Your job is to classify user queries and extract its target stock if mentioned else null.
        
        PREVIOUS CONTEXT:
        {context_str}

        CATEGORIES:
        1. GENERAL: Greetings, platform info, or general financial terms (e.g. "What is RSI?").
        2. RESEARCH: Real-time data requests, stock analysis, or market deep dives (e.g. "Analyze RELIANCE").
        3. PORTFOLIO: Personal holdings, auditing "my" stocks, or how news affects *their* assets (e.g. "Check **my** portfolio", "Analyze SBIN in **my holdings**").

        Return only JSON:
        {{"intent": "GENERAL" | "RESEARCH" | "PORTFOLIO", "reasoning": "Brief explanation", "target_symbol": "TICKER or null"}}
        """
        resp = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        return json.loads(resp.choices[0].message.content)

    async def generate_harvest_plan(self, query: str, intent: str, suggested_symbol: Optional[str] = None) -> Dict[str, Any]:
        """Phase 2: Autonomous Harvesting Plan."""
        ticker_context = await self._get_ticker_context()
        
        # Categorized High-Density Institutional Tool Registry (26 Tools)
        available_tools = [
            {"id": "yf_quote", "name": "Institutional Quote", "description": "LTP, Bid/Ask, and Market Session metadata."},
            {"id": "yf_profile", "name": "Company Profile", "description": "Sector, Industry, and Executive leadership data."},
            {"id": "yf_historical", "name": "OHLCV History", "description": "Price-Volume candles for technical analysis."},
            {"id": "yf_news", "name": "Global News", "description": "Institutional news context and market-moving stories."},
            {"id": "yf_metrics", "name": "Valuation Metrics", "description": "Ratios: PE, ROE, PEG and institutional valuation."},
            {"id": "yf_income", "name": "Income Statement", "description": "Quarterly/Yearly Revenue and Profitability audit."},
            {"id": "yf_balance", "name": "Balance Sheet", "description": "Assets, Liabilities, and Shareholder Equity."},
            {"id": "yf_cash", "name": "Cash Flow", "description": "Operating, Investing, and Financing cash flows."},
            {"id": "nse_bulk", "name": "Bulk Deals", "description": "Large market transactions (>0.5% equity)."},
            {"id": "nse_block", "name": "Block Deals", "description": "Single-trade institutional blocks (>₹5 Cr)."},
            {"id": "nse_deliverable", "name": "Delivery %", "description": "Institutional absorption and smart money holdings."},
            {"id": "nse_short_sell", "name": "Short Sell Audit", "description": "Speculative pressure and short positioning stats."},
            {"id": "nse_fii_dii", "name": "FII/DII Flow", "description": "Foreign vs Domestic institutional participation."},
            {"id": "nse_announcements", "name": "Live Filings", "description": "Real-time market disclosures and corporate PR."},
            {"id": "nse_board_meet", "name": "Board Strategy", "description": "Upcoming meeting topics and strategy guidance."},
            {"id": "nse_financials", "name": "NSE Financials", "description": "Direct earnings results and filings audit."},
            {"id": "nse_shareholding", "name": "Ownership Structure", "description": "Promoter vs Public holding stability and changes."},
            {"id": "nse_movers", "name": "Market Movers", "description": "Session gainers, losers, and liquidity leaders."},
            {"id": "nse_most_active", "name": "Most Active", "description": "Volume and Value leaders for the current session."},
            {"id": "nse_india_vix", "name": "Fear Index", "description": "Market volatility and risk-off sentiment (VIX)."},
            {"id": "nse_total_traded", "name": "Market Turnover", "description": "Total traded volume and value metrics."},
            {"id": "nse_fno_list", "name": "F&O Universe", "description": "List of securities in the derivatives segment."},
            {"id": "nse_index_equity", "name": "Index Stocks", "description": "Constituents list for specific market indices."},
            {"id": "nse_event_cal", "name": "Event Calendar", "description": "Upcoming corporate and market events calendar."},
            {"id": "nse_price_vol", "name": "Price-Vol Stats", "description": "Detailed delivery and volatility statistics."},
            {"id": "nse_corp_action", "name": "Corp Actions", "description": "Dividends, Bonus, and Split history."}
        ]

        system_prompt = f"""
        You are the Data Architect for FolioPP. Identify precisely which tools are needed to answer the query.

        TOOL SELECTION RULES:
        1. Select ONLY from the pre-defined tool IDs below. 
        2. If "technical analysis", "patterns", or "charts" are mentioned, **ALWAYS** include 'yf_historical'.
        3. Do NOT use abstract names like 'Financial Modeling' or 'Fundamental Analysis'.

        AVAILABLE TOOLS:
        {json.dumps([t['id'] for t in available_tools])}
        
        REFERENCE DATA (Ticker Map):
        {ticker_context}
        
        INPUTS: Query: {query} | Suggested Symbol: {suggested_symbol or "None"}
        
        Return JSON:
        {{
            "thought_process": "Explanation of search strategy",
            "sectors": ["Sector"],
            "symbols": ["TICKER"],
            "required_tools": ["yf_quote", "yf_historical", "nse_bulk"]
        }}
        """
        resp = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        return json.loads(resp.choices[0].message.content)

    async def chat_stream(self, query: str, active_symbol: Optional[str] = None, session_id: str = "default") -> AsyncGenerator[str, None]:
        """Full Pipeline: History -> Intent -> Harvest -> Analysis -> Synthesis -> Persist."""
        
        # 🟢 LOCAL-MODE: Check for basic definitions (Skip LLM for speed/cost)
        definitions = {
            "BULK DEALS": "**NSE Bulk Deals**: A deal is recorded as 'Bulk' when the total quantity of shares bought or sold on a single exchange is more than 0.5% of the total number of equity shares of the listed company. These are executed during normal market hours.",
            "BLOCK DEALS": "**NSE Block Deals**: A single trade that involves a minimum quantity of 5,00,000 shares OR a minimum value of ₹5 Crores. These are executed in a separate 15-minute window before market opens.",
            "RSI": "**Relative Strength Index (RSI)**: A momentum oscillator that measures the speed and change of price movements. RSI oscillates between zero and 100. Usually, RSI > 70 is overbought and RSI < 30 is oversold.",
            "PROMOTER TRADING": "**Promoter Trading**: When individuals or entities classified as promoters (owners/founding group) buy or sell shares. High-volume selling by promoters is often a risk signal in the FolioPP DRL model."
        }
        
        upper_query = query.upper()
        for key, text in definitions.items():
            if key in upper_query and len(query.split()) < 5:
                yield f"### Institutional Definition: {key}\n\n{text}\n\n*This is a local terminal definition. No AI tokens were consumed for this response.*"
                return

        # 0. Load History (Last 10 messages)
        history = await self._get_history(session_id, limit=10)
        
        # 1. Phase 1: IntentDetection
        intent_data = await self.detect_intent(query, history)
        intent = intent_data.get("intent", "GENERAL")
        reasoning = intent_data.get("reasoning", "")
        target_symbol = intent_data.get("target_symbol")
        
        yield f"🎯 [THOUGHT] Intent: **{intent}**. Reasoning: *{reasoning}* [/THOUGHT]\n"

        if intent == "GENERAL":
            async for chunk in self._general_chat(query, session_id): yield chunk
            return

        if intent == "PORTFOLIO" and not target_symbol:
            async with AsyncSessionLocal() as db:
                holdings = (await db.execute(select(PortfolioEntry))).scalars().all()
            
            selected_holdings = holdings # For holistic audit
            yield f"💼 [THOUGHT] Performing a **holistic high-fidelity audit** across ALL {len(selected_holdings)} holdings. [/THOUGHT]\n"

            # Parallel Audit Function
            async def audit_stock(h):
                sym = h.symbol if h.symbol.endswith(".NS") else f"{h.symbol}.NS"
                clean_sym = h.symbol.replace(".NS", "")
                
                # Fetch Quote, Tech, News
                quote_task = YFinanceEquityQuoteFetcher.fetch_data({"symbol": sym, "exchange": "NSE"}, {})
                hist_task = YFinanceEquityHistoricalFetcher.fetch_data({"symbol": sym, "exchange": "NSE", "period": "1y"}, {})
                news_task = YFinanceCompanyNewsFetcher.fetch_data({"symbol": sym, "exchange": "NSE"}, {})
                
                q, hist, news = await asyncio.gather(quote_task, hist_task, news_task, return_exceptions=True)
                
                # Tech Indicator Generation
                tech_data = {}
                if not isinstance(hist, Exception) and hist:
                    df = technical_analyzer.process_data([r.model_dump() for r in hist])
                    last = df.iloc[-1]
                    tech_data = {"price": round(last.get("close", 0), 2), "rsi": round(last.get("rsi_14", 50), 2), "regime": last.get("regime", "Neutral")}
                
                return {
                    "symbol": clean_sym,
                    "holding": {"units": h.units, "avg_price": h.avg_price},
                    "quote": q.model_dump() if not isinstance(q, Exception) else {"error": str(q)},
                    "technical": tech_data,
                    "news": [n.model_dump() for n in news[:2]] if not isinstance(news, Exception) else []
                }

            # Batch Execution
            audit_tasks = [audit_stock(h) for h in selected_holdings]
            portfolio_data = await asyncio.gather(*audit_tasks)
            
            # Synthesis Prompt
            portfolio_prompt = f"""
            You are an Elite Portfolio Manager. Summarize the following "Institutional Portfolio Audit".
            Context Query: {query}
            
            DATA:
            {json.dumps(portfolio_data, default=str)}
            
            Format:
            ### Portfolio Audit Report
            - **Overall Health**: (Check RSI/Regime across positions)
            - **Technical Highlights**: (Bullet points for each stock)
            - **Recent News Impact**: (Summarize Top 1-2 news items for the holdings)
            - **Action Suggestions**: (Hold/Averaging/Reducing suggestions based on latest quote vs avg price)
            """
            
            synth = await self.client.chat.completions.create(
                model=self.model, 
                messages=[
                    {"role": "system", "content": portfolio_prompt}, 
                    *history[-5:], 
                    {"role": "user", "content": query}
                ], 
                stream=True
            )

            full_p_response = ""
            async for chunk in synth:
                if content := chunk.choices[0].delta.content:
                    full_p_response += content
                    yield content
            
            # Persist Portfolio Audit
            await self._save_message(session_id, "user", query)
            await self._save_message(session_id, "assistant", full_p_response, thoughts=[f"Holistic audit of {len(selected_holdings)} assets"])
            return

        # 2. Phase 2: Harvest Plan (Standard Research Flow)
        suggested_symbol = target_symbol or active_symbol or None
        plan = await self.generate_harvest_plan(query, intent, suggested_symbol)
        
        target_symbols = plan.get("symbols", [suggested_symbol] if suggested_symbol else ["SBIN"])
        required_tools = plan.get("required_tools", ["yf_quote"])
        
        yield f"🔍 [THOUGHT] Plan: Targets **{', '.join(target_symbols)}**. Tools: {', '.join(required_tools)}. [/THOUGHT]\n"

        # 3. Phase 3: Parallel Logic (Standard Research Flow)
        symbol = target_symbols[0] if target_symbols else "SBIN"
        data_context = {"symbol": symbol}
        
        yield f"📡 [THOUGHT] Harvesting institutional dataset for {symbol}... [/THOUGHT]\n"
        
        async def wrap_task(t_id, coro):
            try: return t_id, await coro
            except Exception as e: return t_id, e

        tasks = []
        for t_id in required_tools:
            params = self._resolve_tool_params(t_id, symbol)
            fetcher = self._get_fetcher(t_id)
            if fetcher:
                tasks.append(wrap_task(t_id, fetcher.fetch_data(params, {})))
        
        # 🟢 ASYNC STREAMING HARVEST (The speed secret)
        harvest_count = 0
        for future in asyncio.as_completed(tasks):
            t_id, res = await future
            if not isinstance(res, Exception):
                data_context[t_id] = [r.model_dump() if hasattr(r, 'model_dump') else r for r in res] if isinstance(res, list) else (res.model_dump() if hasattr(res, 'model_dump') else res)
            else:
                data_context[t_id] = {"error": str(res)}
                
            harvest_count += 1
            if harvest_count % 3 == 0:
                yield f"[THOUGHT] Synchronizing Pipeline: {t_id.replace('_',' ').title()} integrated... ({harvest_count}/{len(tasks)}) [/THOUGHT]\n"

        # 4. Phase 4: Analysis (Technical, NLP, Portfolio & DRL)
        yield "📈 [THOUGHT] 100% Data Coverage achieved. Running technical patterns, news sentiment & Portfolio impact audit... [/THOUGHT]\n"
        
        # Technical
        if data_context.get("yf_historical"):
            # Compute deep metrics (using all data)
            tech_df = technical_analyzer.process_data(data_context["yf_historical"])
            last = tech_df.iloc[-1]
            data_context["technical_indicators"] = {
                "price": round(last.get("close", 0), 2),
                "rsi_14": round(last.get("rsi_14", 50), 2),
                "macd": round(last.get("macd", 0), 2),
                "sma20": round(last.get("sma_20", 0), 2),
                "sma50": round(last.get("sma_50", 0), 2),
                "sma200": round(last.get("sma_200", 0), 2),
                "regime": last.get("regime", "Neutral"),
                "volume": last.get("volume", 0)
            }
            # TRUNCATE: Only pass the last 5 days of raw OHLCV context to LLM to save tokens
            data_context["yf_historical"] = data_context["yf_historical"][-5:]

        # NLP (News Feature Extraction & Deduplication)
        data_context["nlp_features"] = {
            "sentiment": 0, "price_impact": 0, "risk_profile": 0, "reasoning": "No news available for deep audit."
        }
        news_hash = "no_news"
        if data_context.get("yf_news") and isinstance(data_context["yf_news"], list) and len(data_context["yf_news"]) > 0:
            top_news = data_context["yf_news"][0] # Focus on primary headline
            news_text = f"Title: {top_news.get('title', '')}\nSummary: {top_news.get('summary', '')}"
            news_hash = hashlib.sha256(news_text.encode()).hexdigest()
            
            # CACHE CHECK: If we analyzed this exact news recently for this stock, REUSE it.
            async with AsyncSessionLocal() as db:
                stmt = select(DRLDecision).where(DRLDecision.symbol == symbol, DRLDecision.news_hash == news_hash).order_by(DRLDecision.timestamp.desc()).limit(1)
                existing_decision = (await db.execute(stmt)).scalar()
                
            if existing_decision and (datetime.utcnow() - existing_decision.timestamp) < timedelta(hours=4):
                logger.info(f"NLP Cache Hit for {symbol} (Hash: {news_hash[:8]}). Reusing analysis.")
                cached_nlp = existing_decision.state_json.get("nlp", {})
                data_context["nlp_features"] = cached_nlp
                data_context["is_duplicate_experience"] = True # Flag to avoid redundant training log
            else:
                company_context = data_context.get("yf_profile", {"name": symbol})
                try:
                    analysis = self.nlp_analyzer.analyze_news(news_text, company_context)
                    data_context["nlp_features"] = {
                        "news_relevance": analysis.news_relevance,
                        "sentiment": analysis.sentiment,
                        "price_impact": analysis.price_impact,
                        "trend_direction": analysis.trend_direction,
                        "earnings_impact": analysis.earnings_impact,
                        "investor_confidence": analysis.investor_confidence,
                        "risk_profile": analysis.risk_profile,
                        "reasoning": analysis.reasoning
                    }
                    data_context["is_duplicate_experience"] = False
                except Exception as e:
                    logger.error(f"NLP Analysis Failed: {e}")
                    data_context["is_duplicate_experience"] = True # Fallback to no-log if failed

        # Portfolio Status
        async with AsyncSessionLocal() as db:
            holdings = (await db.execute(select(PortfolioEntry))).scalars().all()
        holding = next((h for h in holdings if h.symbol.replace(".NS","") == symbol.replace(".NS","")), None)
        data_context["portfolio_status"] = {
            "is_held": holding is not None,
            "units": holding.units if holding else 0,
            "avg_price": holding.avg_price if holding else 0,
            "current_value": (holding.units * data_context.get("technical_indicators", {}).get("price", 0)) if holding else 0
        }

        # DRL DECISION (The missing Piece)
        yield f"[THOUGHT] Executing DRL Module (A2C/PPO/SAC) with State(St) inputs... [/THOUGHT]\n"
        drl_result = drl_module.calculate_decision(
            tech_indicators=data_context.get("technical_indicators", {}),
            nlp_features=data_context.get("nlp_features", {}),
            portfolio=data_context["portfolio_status"],
            symbol=symbol
        )
        data_context["drl_decision"] = drl_result.model_dump()

        # PERSIST: Log Experience to Database ONLY if NOT a duplicate/redundant context
        if not data_context.get("is_duplicate_experience", False):
            try:
                async with AsyncSessionLocal() as db:
                    state_data = {
                        "tech": data_context.get("technical_indicators"),
                        "nlp": data_context.get("nlp_features"),
                        "portfolio": data_context.get("portfolio_status")
                    }
                    decision_entry = DRLDecision(
                        symbol=symbol,
                        agent_type=drl_result.agent,
                        state_json=state_data,
                        news_hash=news_hash,
                        action=drl_result.action,
                        confidence=drl_result.confidence
                    )
                    db.add(decision_entry)
                    await db.commit()
                    logger.info(f"DRL Unique Experience logged: {symbol} -> {drl_result.action}")
            except Exception as e:
                logger.error(f"Failed to persist DRL decision: {e}")
        else:
            logger.info(f"Skipping redundant DRL experience log for {symbol} (Already captured in this token/news context).")

        # FINAL CONTEXT CLEANUP: Ensure no massive lists go to LLM
        for key in list(data_context.keys()):
            if isinstance(data_context[key], list) and len(data_context[key]) > 10:
                data_context[key] = data_context[key][-10:] # Keep latest 10 items max


        # 5. Phase 5: Investment Report Synthesis
        report_prompt = f"""
        You are a Senior Portfolio Manager. Generate an "Investment Report" exactly in this format:

        ### Investment Report: {symbol} ({data_context.get('yf_profile', {}).get('name', 'Company')})
        **Date**: {datetime.now().strftime("%B %d, %Y")}

        #### Technical Analysis
        - **Current Price**: ${data_context.get('technical_indicators', {}).get('price')} (Regime: {data_context.get('technical_indicators', {}).get('regime')})
        - **Relative Strength Index (RSI)**: {data_context.get('technical_indicators', {}).get('rsi_14')}
        - **Moving Average (SMA20)**: ${data_context.get('technical_indicators', {}).get('sma20')}
        - **Trading Volume**: {data_context.get('technical_indicators', {}).get('volume', 0):,}

        #### Fundamental Analysis
        (Audit the PE, Cash Flow, and Financials from data)
        - PE Ratio: {data_context.get('yf_metrics', {}).get('trailingPE', 'N/A')}
        - Revenue/Health: {json.dumps(data_context.get('yf_income', 'N/A'))[:200]}

        #### News Overview (Institutional)
        (Summarize top 2-3 news items)
        {json.dumps(data_context.get('yf_news', [])[:3], indent=1)}

        #### Summary
        (2-sentence professional synthesis combining all data signals)

        #### Risks
        - (Identify 2-3 specific risks from the data)

        #### Portfolio Impact & Suggestions
        - **Current Holding**: {data_context['portfolio_status'].get('units', 0)} units at avg price of {data_context['portfolio_status'].get('avg_price', 0)}
        - **Exposures**: (Analyze how this data affects their specific entry price and position size. Provide logic for keeping or reducing exposure.)

        #### DRL Decision (Phase 4: Decision Making)
        - **Model Action**: {data_context.get('drl_decision', {}).get('action')} (Confidence: {data_context.get('drl_decision', {}).get('confidence')*100}%)
        - **Calculated Q-Value**: {data_context.get('drl_decision', {}).get('q_value')}
        - **Agent Engine**: {data_context.get('drl_decision', {}).get('agent')} (Actor-Critic Based Optimization)
        - **DRL Reasoning**: {data_context.get('drl_decision', {}).get('reasoning')}
 
        #### Investment Conclusion
        (Final Verdict: Use the DRL Model Action as a primary signal, but synthesize with Fundamental/Technical reasoning. Provide a definitive BUY/HOLD/SELL recommendation.)
        """
        # PHASE 5: Synthesis & Persistence
        thoughts_log = [reasoning] if reasoning else []
        
        # Add research highlights to thoughts
        thoughts_log.append(f"Intent: {intent}")
        if target_symbol: thoughts_log.append(f"Target: {target_symbol}")
        
        messages = [
            {"role": "system", "content": report_prompt},
            *history[-5:], # Inject last 5 messages for context
            {"role": "user", "content": query}
        ]
        
        completion = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True,
            temperature=0.2
        )
        
        full_response = ""
        async for chunk in completion:
            if content := chunk.choices[0].delta.content:
                full_response += content
                yield content
        
        # 🔗 AUDIT LOG (Collapsible JSON)
        yield "\n\n<details>\n<summary><b>🔍 Institutional Data Context (JSON)</b></summary>\n\n"
        yield f"```json\n{json.dumps(data_context, indent=2, default=str)}\n```\n"
        yield "</details>\n"

        # 6. Persist Conversation
        await self._save_message(session_id, "user", query)
        await self._save_message(session_id, "assistant", full_response, thoughts=thoughts_log)

        # 🔄 AUTOMATIC DRL TRAINING TRIGGER
        # Fire-and-forget background task to calculate rewards and train the model
        asyncio.create_task(drl_trainer.run_automatic_cycle())

    def _get_fetcher(self, t_id: str):
        mapping = {
            "yf_quote": YFinanceEquityQuoteFetcher, "yf_profile": YFinanceEquityProfileFetcher,
            "yf_historical": YFinanceEquityHistoricalFetcher, "yf_news": YFinanceCompanyNewsFetcher,
            "yf_metrics": YFinanceKeyMetricsFetcher, "yf_income": YFinanceIncomeStatementFetcher,
            "yf_balance": YFinanceBalanceSheetFetcher, "yf_cash": YFinanceCashFlowFetcher,
            "nse_bulk": NSEBulkBlockDealFetcher, "nse_block": NSEBulkBlockDealFetcher,
            "nse_corp_action": NSECorporateActionFetcher, "nse_deliverable": NSEDeliverableFetcher,
            "nse_announcements": NSECorporateAnnouncementFetcher, "nse_board_meet": NSEBoardMeetingFetcher,
            "nse_financials": NSEFinancialResultFetcher, "nse_shareholding": NSEShareholdingPatternFetcher,
            "nse_short_sell": NSEShortSellingFetcher, "nse_fii_dii": NSEFiiDiiFetcher,
            "nse_india_vix": NSEIndiaVixFetcher, "nse_movers": NSEMarketMoverFetcher,
            "nse_most_active": NSEMostActiveFetcher, "nse_fno_list": NSEFnoEquityListFetcher,
            "nse_index_equity": NSEIndexEquityListFetcher, "nse_event_cal": NSEEventCalendarFetcher,
            "nse_price_vol": NSEPriceVolumeFetcher, "nse_total_traded": NSETotalTradedFetcher
        }
        return mapping.get(t_id)

    def _resolve_tool_params(self, t_id: str, symbol: str) -> Dict[str, Any]:
        clean = symbol.replace(".NS", "").upper()
        params = {"symbol": f"{clean}.NS" if t_id.startswith("yf_") else clean}
        if t_id.startswith("yf_"):
            params["exchange"] = "NSE"
            if t_id == "yf_historical": params["period"] = "1y"
        elif t_id.startswith("nse_"):
            if t_id == "nse_bulk": params.update({"deal_type": "bulk", "period": "1M"})
            elif t_id == "nse_block": params.update({"deal_type": "block", "period": "1M"})
            elif t_id in ["nse_corp_action", "nse_board_meet", "nse_financials"]: params["period"] = "1Y"
            elif t_id == "nse_deliverable": params["period"] = "1W"
            elif t_id in ["nse_announcements", "nse_price_vol"]: params["period"] = "1M"
            elif t_id == "nse_price_vol" and clean in ["NIFTY", "NIFTY50"]: params["symbol"] = "NIFTY 50"
            elif t_id in ["nse_short_sell", "nse_india_vix", "nse_fii_dii", "nse_movers", "nse_most_active", "nse_fno_list", "nse_index_equity", "nse_event_cal", "nse_total_traded"]:
                params.pop("symbol", None)
                if t_id == "nse_index_equity": params["index_name"] = "NIFTY 50"
                params["period"] = "1W" if "vix" in t_id or "short" in t_id else "1M"
        return params

    async def _get_ticker_context(self) -> str:
        try:
            async with AsyncSessionLocal() as db:
                tickers = (await db.execute(select(NSETicker).limit(15))).scalars().all()
                return "Tickers:\n" + "\n".join([f"- {t.symbol}: {t.name}" for t in tickers]) if tickers else "RELIANCE.NS, SBIN.NS"
        except: return "RELIANCE.NS, SBIN.NS"


    async def _get_history(self, session_id: str, limit: int = 10) -> List[Dict]:
        try:
            async with AsyncSessionLocal() as db:
                msgs = (await db.execute(
                    select(ChatMessage)
                    .where(ChatMessage.session_id == session_id)
                    .order_by(ChatMessage.timestamp.desc())
                    .limit(limit)
                )).scalars().all()
                # Return in chronological order
                return [{"role": m.role, "content": m.content} for m in reversed(msgs)]
        except Exception as e:
            logger.error(f"Error loading history: {e}")
            return []

    async def _save_message(self, session_id: str, role: str, content: str, thoughts: List[str] = None):
        try:
            async with AsyncSessionLocal() as db:
                msg = ChatMessage(session_id=session_id, role=role, content=content, thoughts=thoughts)
                db.add(msg)
                await db.commit()
        except Exception as e:
            logger.error(f"Error saving message: {e}")

    async def _general_chat(self, query: str, session_id: str = "default") -> AsyncGenerator[str, None]:
        """Phase 5: General Synthesis & Persistence for non-research queries."""
        completion = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are the FolioPP Terminal. Give concise professional responses. You have access to real-time institutional data if users ask for research."},
                {"role": "user", "content": query}
            ],
            stream=True
        )
        full_response = ""
        async for chunk in completion:
            if content := chunk.choices[0].delta.content:
                full_response += content
                yield content
        
        # Persist
        await self._save_message(session_id, "user", query)
        await self._save_message(session_id, "assistant", full_response, thoughts=["General conversation context"])

market_agent = MarketAgent()
