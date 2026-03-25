"""Market Agent - Neural Orchestrator for Institutional Research Synthesis."""

import json
from typing import AsyncGenerator
import asyncio
from backend.config import settings
from groq import AsyncGroq

# 🔹 Standardized Intelligence Registry
from foliopp_yfinance.models.equity_quote import YFinanceEquityQuoteFetcher
from foliopp_yfinance.models.equity_profile import YFinanceEquityProfileFetcher
from foliopp_yfinance.models.equity_historical import YFinanceEquityHistoricalFetcher
from foliopp_yfinance.models.company_news import YFinanceCompanyNewsFetcher
from foliopp_yfinance.models.key_metrics import YFinanceKeyMetricsFetcher

class MarketAgent:
    """Orchestrates Phase 3 (Intelligence) using Llama 3.1 for structured institutional reporting."""
    
    def __init__(self):
        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.1-8b-instant"

    async def chat_stream(self, query: str) -> AsyncGenerator[str, None]:
        """Streams structured institutional research following the 7-Dimension format."""
        
        # 1. 🔍 Context Harvesting (Extract Symbol)
        # In a real scenario, we'd use a regex or NLP to find the symbol. 
        # For our terminal, we assume the user is asking about the focused ticker.
        symbol = "SBIN" # Default for now, ideally extracted from query
        if "AAPL" in query.upper(): symbol = "AAPL"
        elif "RELIANCE" in query.upper(): symbol = "RELIANCE.NS"
        
        # 2. 📡 Real-Time Data Fetching (Parallel)
        try:
            tasks = [
                YFinanceEquityQuoteFetcher.fetch_data({"symbol": symbol, "exchange": "NSE"}, {}),
                YFinanceEquityProfileFetcher.fetch_data({"symbol": symbol, "exchange": "NSE"}, {}),
                YFinanceCompanyNewsFetcher.fetch_data({"symbol": symbol, "exchange": "NSE"}, {}),
                YFinanceKeyMetricsFetcher.fetch_data({"symbol": symbol, "exchange": "NSE"}, {})
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            quote = results[0] if not isinstance(results[0], Exception) else {}
            profile = results[1] if not isinstance(results[1], Exception) else {}
            news = results[2] if not isinstance(results[2], Exception) else []
            metrics = results[3] if not isinstance(results[3], Exception) else {}

            context = {
                "symbol": symbol,
                "price": getattr(quote, 'price', 'N/A'),
                "change": getattr(quote, 'change_percent', 'N/A'),
                "market_cap": getattr(quote, 'market_cap', 'N/A'),
                "news": [n.model_dump() for n in news[:5]] if news else [],
                "sector": profile[0].sector if profile else "Equity",
                "description": profile[0].long_business_summary[:500] if profile else ""
            }
        except Exception as e:
            context = {"error": str(e), "symbol": symbol}

        # 3. 🧠 Neural Synthesis (Llama 3.1)
        system_prompt = """
        You are an Institutional Research AI. Generate a formal "Investment Report" exactly in this format:
        
        # Investment Report: [Symbol] ([Company Name])
        **Date: [Current Date]**

        ### Technical Analysis
        * **Price Action**: [Analyze recent move, volatility]
        * **Volume**: [Analyze participation levels]
        * **Indicators**: [Synthesize SMA20, RSI(14) logic]
        
        ### Fundamental Analysis
        * **Market Cap**: [Size and leadership]
        * **Valuation**: [P/E, Forward P/E analysis]
        * **Leverage**: [Debt-to-equity and cash flow resilience]

        ### News Overview
        1. [Major Event 1]: [Sentiment & Impact]
        2. [Major Event 2]: [Policy/Macro context]
        3. [Major Event 3]: [Strategy/Risk context]

        ### Summary
        [Synthesize technical support zones and macro catalysts in 3-4 lines]

        ### Risks
        * **Policy Uncertainty**: [Geopolitical/Regulatory risks]
        * **Technical Risk**: [Support breakdown levels]
        * **Competitive Pressure**: [Sector competition]

        ### Investment Conclusion
        [One line verdict]
        **Recommended Action: [BUY/SELL/HOLD] (Price range: [Range])**
        
        STRICT RULES:
        1. Use EXACT headings.
        2. Be quantitative (use numbers).
        3. Professional matte tone.
        4. No fluff.
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context: {json.dumps(context)}\n\nUser Query: {query}"}
        ]

        # 4. 🌊 Neural Streaming
        completion = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True,
            temperature=0.2
        )

        async for chunk in completion:
            content = chunk.choices[0].delta.content or ""
            if content:
                yield content

market_agent = MarketAgent()
