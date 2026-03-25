import asyncio
import json
from typing import AsyncGenerator, Dict, Any

async def stream_rule_based_analysis(headline: str, ticker: str, profile: Dict = None) -> AsyncGenerator[str, None]:
    """
    Streams a single-call Neural Reasoning result for institutional-grade transparency.
    """
    # Initialize the Ferrari
    from .nlp_analyzer import NLPAnalyzer
    analyzer = NLPAnalyzer()
    
    # 1. Fetch Company context for the LLM
    company_context = profile or {
        "name": ticker,
        "sector": "Financial Services",
        "industry": "Banks",
        "longBusinessSummary": f"Institutional context for {ticker}."
    }

    # 2. Call the REAL Neural Engine with streaming reasoning
    full_reasoning = ""
    analysis_data = None
    
    async for part in analyzer.stream_analysis(headline, company_context):
        # We catch the 'reasoning' chunks as they come and yield them for the UI
        if part["type"] == "reasoning":
            # We yield it as-is for the typewriter effect
            yield part["content"]
            full_reasoning += part["content"]
        elif part["type"] == "final":
            analysis_data = part["content"]

    # In case of error or no final data
    if not analysis_data:
        yield "\n[INTERNAL ERROR] Institutional thinking interrupted.\n"
        return

    # 3. Yield the structured signal tool call (so the frontend summary boxes work)
    tool_call = {
        "function": {
            "name": "analyze_market_nlp_features",
            "arguments": json.dumps({
                "relevance": analysis_data.get("news_relevance", 0),
                "sentiment": analysis_data.get("sentiment", 0),
                "potential_impact_on_price": analysis_data.get("price_impact", 0),
                "trend_direction": analysis_data.get("trend_direction", 0),
                "earnings_impact": analysis_data.get("earnings_impact", 0),
                "investor_confidence": analysis_data.get("investor_confidence", 0),
                "risk_profile_change": analysis_data.get("risk_profile", 0),
                "reasoning": analysis_data.get("reasoning", "")
            })
        }
    }
    
    yield f"\n[TOOL_CALL]\n{json.dumps(tool_call)}"
