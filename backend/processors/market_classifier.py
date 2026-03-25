from typing import Dict, List, Any
import json
import asyncio
from .nlp_analyzer import NLPAnalyzer

class MarketClassifier:
    """
    Consolidated Neural Orchestrator for FolioPP Financial Analysis.
    Replaced 7+ rule-based scripts with a single, high-fidelity LLM Intelligence call.
    """
    
    def __init__(self):
        self.analyzer = NLPAnalyzer()
        # Institutional baseline for context if fetch fails
        self.fallback_profiles = {
            "SBIN": {
                "name": "State Bank of India",
                "sector": "Financial Services",
                "industry": "Banks",
                "longBusinessSummary": "State Bank of India is a fortune 500 company and the largest public sector bank in India."
            }
        }

    async def analyze_complete_async(self, headline: str, ticker: str, profile: Dict = None) -> Dict[str, Any]:
        """
        Executes a single, unified LLM call via NLPAnalyzer.
        """
        company_context = profile or self.fallback_profiles.get(ticker, {
            "name": ticker,
            "sector": "General",
            "industry": "General",
            "longBusinessSummary": f"No detailed profile for {ticker}."
        })

        # One call to rule them all
        analysis = self.analyzer.analyze_news(headline, company_context)
        
        return {
            "headline": headline,
            "ticker": ticker,
            "company": company_context.get("name"),
            "features": {
                "relevance": int(analysis.news_relevance),
                "sentiment": int(analysis.sentiment),
                "potential_impact_on_price": int(analysis.price_impact),
                "trend_direction": int(analysis.trend_direction),
                "earnings_impact": int(analysis.earnings_impact),
                "investor_confidence": int(analysis.investor_confidence),
                "risk_profile_change": int(analysis.risk_profile)
            },
            "reasoning": analysis.reasoning
        }

# Global Singleton
market_classifier = MarketClassifier()
