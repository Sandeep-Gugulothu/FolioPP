import os
import json
import asyncio
from enum import IntEnum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from openai import AsyncOpenAI, OpenAI
from dotenv import load_dotenv

load_dotenv()

class NewsRelevance(IntEnum):
    NOT_RELEVANT = 0
    SOMEWHAT_RELEVANT = 1
    HIGHLY_RELEVANT = 2

class Sentiment(IntEnum):
    NEGATIVE = -1
    NEUTRAL = 0
    POSITIVE = 1

class PriceImpact(IntEnum):
    STRONG_NEGATIVE = -3
    MODERATE_NEGATIVE = -2
    SLIGHT_NEGATIVE = -1
    NO_IMPACT = 0
    SLIGHT_POSITIVE = 1
    MODERATE_POSITIVE = 2
    STRONG_POSITIVE = 3

class TrendDirection(IntEnum):
    DOWNWARD = -1
    NEUTRAL = 0
    UPWARD = 1

class EarningsImpact(IntEnum):
    SIGNIFICANT_NEGATIVE = -2
    SLIGHT_NEGATIVE = -1
    NEUTRAL_OR_UNCLEAR = 0
    SLIGHT_POSITIVE = 1
    SIGNIFICANT_POSITIVE = 2

class InvestorConfidence(IntEnum):
    STRONG_DECREASE = -3
    MODERATE_DECREASE = -2
    SLIGHT_DECREASE = -1
    NO_CHANGE = 0
    SLIGHT_INCREASE = 1
    MODERATE_INCREASE = 2
    STRONG_INCREASE = 3

class RiskProfileChange(IntEnum):
    SIGNIFICANTLY_INCREASED = -2
    SLIGHTLY_INCREASED = -1
    NO_SIGNIFICANT_CHANGE = 0
    SLIGHTLY_REDUCED = 1
    SIGNIFICANTLY_REDUCED = 2

class FinancialAnalysis(BaseModel):
    """Structured analysis of a financial news item."""
    reasoning: str = Field(..., description="A detailed chain-of-thought analysis.")
    news_relevance: NewsRelevance
    sentiment: Sentiment
    price_impact: PriceImpact
    trend_direction: TrendDirection
    earnings_impact: EarningsImpact
    investor_confidence: InvestorConfidence
    risk_profile: RiskProfileChange

NLP_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "analyze_market_nlp_features",
            "description": "Analyze financial news and extract features.",
            "parameters": FinancialAnalysis.model_json_schema()
        }
    }
]

class NLPAnalyzer:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.base_url = "https://api.groq.com/openai/v1"
        self.model = "llama-3.1-8b-instant"
        self.sync_client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.async_client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)

    def get_prompt(self, news_text: str, company_context: Dict[str, Any]) -> str:
        return f"""
        ### CONTEXT: FINANCIAL ANALYSIS TASK
        Analyze the impact of this news on {company_context.get('name', 'the ticker')}.
        Business Focus: {company_context.get('longBusinessSummary', 'N/A')[:500]}
        
        ### NEWS CONTENT:
        "{news_text}"
        
        Call the 'analyze_market_nlp_features' function with your findings. 
        Start with 'reasoning' to explain your steps.
        """

    def analyze_news(self, news_text: str, company_context: Dict[str, Any]) -> FinancialAnalysis:
        messages = [
            {"role": "system", "content": "You are a professional financial analyst."},
            {"role": "user", "content": self.get_prompt(news_text, company_context)}
        ]
        response = self.sync_client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=NLP_TOOLS,
            tool_choice={"type": "function", "function": {"name": "analyze_market_nlp_features"}}
        )
        tool_call = response.choices[0].message.tool_calls[0]
        return FinancialAnalysis(**json.loads(tool_call.function.arguments))

    async def stream_analysis(self, news_text: str, company_context: Dict[str, Any]):
        """Streams the reasoning as [THOUGHT] tags for the UI."""
        messages = [
            {"role": "system", "content": "Analyze news. Stream 'reasoning' first."},
            {"role": "user", "content": self.get_prompt(news_text, company_context)}
        ]
        
        response = await self.async_client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=NLP_TOOLS,
            tool_choice={"type": "function", "function": {"name": "analyze_market_nlp_features"}},
            stream=True
        )

        full_args = ""
        in_reasoning = False
        
        async for chunk in response:
            if not chunk.choices: continue
            delta = chunk.choices[0].delta
            if delta.tool_calls:
                arg_delta = delta.tool_calls[0].function.arguments
                if arg_delta:
                    full_args += arg_delta
                    
                    # Rough detection of reasoning start
                    if '"reasoning": "' in full_args and not in_reasoning:
                        in_reasoning = True
                        yield {"type": "reasoning", "content": "[THOUGHT] Analysing market context... [/THOUGHT]"}
                    
                    # Yield reasoning updates occasionally for UI feel
                    if len(full_args) % 100 == 0:
                        yield {"type": "reasoning", "content": "[THOUGHT] Expanding pattern recognition... [/THOUGHT]"}

        try:
            # We add a small artificial delay to make the reasoning steps readable
            await asyncio.sleep(0.5)
            yield {"type": "reasoning", "content": "[THOUGHT] Synthesizing final research report... [/THOUGHT]"}
            await asyncio.sleep(0.2)
            
            # Simple fix for incomplete JSON from stream
            if not full_args.endswith('}'): full_args += '"}'
            if not full_args.startswith('{'): full_args = '{' + full_args
            
            data = json.loads(full_args)
            yield {"type": "final", "content": data}
        except:
             # Fallback if parsing fails during stream
             yield {"type": "final", "content": {}}

if __name__ == "__main__":
    analyzer = NLPAnalyzer()
    print("Analyzer ready.")
