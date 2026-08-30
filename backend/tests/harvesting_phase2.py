import os
import asyncio
import json
from groq import AsyncGroq
from typing import Dict, Any, List

# Load environment
try:
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    load_dotenv(env_path)
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
except ImportError:
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

class HarvestingPlanAgent:
    """
    Phase 2: Autonomous Harvesting Plan
    Identifies the necessary tool-chest requirements based on intent.
    """
    def __init__(self, api_key: str):
        self.client = AsyncGroq(api_key=api_key)
        self.model = "llama-3.1-8b-instant"
        
        # Available tools based on providers
        self.available_tools = [
            {"id": "price_ohlcv", "name": "OHLCV Historical Data", "description": "1-year price/volume history for technical analysis"},
            {"id": "fundamental_ratios", "name": "Key Metrics & Ratios", "description": "P/E, D/E, ROE, and valuation metrics"},
            {"id": "nse_filings", "name": "Bulk/Block Deals", "description": "NSE filing data for institutional movements"},
            {"id": "market_news", "name": "Company News", "description": "Latest stories and institutional context"},
            {"id": "realtime_quote", "name": "Real-time Quote", "description": "Current LTP and day's range"}
        ]

    async def generate_plan(self, query: str, intent: str) -> Dict[str, Any]:
        """
        If intent is GENERAL, provides a response.
        If RESEARCH or PORTFOLIO, identifies data requirements.
        """
        if intent == "GENERAL":
            prompt = f"""
            You are the FolioPP Terminal. User query: "{query}"
            Provide a professional, concise response. Remind them you are ready for deep Research or Portfolio Impact analysis.
            """
            resp = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return {
                "intent": "GENERAL",
                "response": resp.choices[0].message.content.strip(),
                "plan": None
            }

        # For RESEARCH or PORTFOLIO, generate a harvesting plan
        system_prompt = f"""
        You are a Data Architect for FolioPP. Based on the query, select the necessary data fetchers.
        Available Tools:
        {json.dumps(self.available_tools, indent=2)}

        Return a JSON object:
        {{
            "thought_process": "Why these tools were selected?",
            "symbol": "TICKER.NS" (extracted symbol or SBIN.NS as default),
            "required_tools": ["tool_id1", "tool_id2"],
            "harvesting_status": "Ready to fetch"
        }}
        """
        
        try:
            resp = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            data = json.loads(resp.choices[0].message.content)
            return {
                "intent": intent,
                "plan": data
            }
        except Exception as e:
            return {"error": str(e)}

async def run_phase2_tests():
    agent = HarvestingPlanAgent(api_key=GROQ_API_KEY)
    results_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
    output_file = os.path.join(results_dir, "phase2_harvesting_output.txt")
    
    # Input from Phase 1 (Simulated)
    test_cases = [
        {"query": "Hi, who are you?", "intent": "GENERAL"},
        {"query": "Analyze RELIANCE after today's bulk deal", "intent": "RESEARCH"},
        {"query": "Check my portfolio for risk", "intent": "PORTFOLIO"},
        {"query": "What is the P/E ratio of HDFCBANK?", "intent": "RESEARCH"}
    ]

    print("--- Phase 2: Autonomous Harvesting Plan ---")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("--- Phase 2: Autonomous Harvesting Plan Output ---\n\n")
        
        for case in test_cases:
            print(f"\nQUERY: {case['query']}")
            result = await agent.generate_plan(case['query'], case['intent'])
            
            if result['intent'] == "GENERAL":
                output = f"Intent: GENERAL\nResponse: {result['response']}\n"
            else:
                plan = result['plan']
                output = (
                    f"Intent: {result['intent']}\n"
                    f"Symbol: {plan.get('symbol', 'N/A')}\n"
                    f"Tools Required: {', '.join(plan.get('required_tools', []))}\n"
                    f"Reasoning: {plan.get('thought_process', 'N/A')}\n"
                )
            
            print(output)
            f.write(f"QUERY: {case['query']}\n{output}" + "-"*50 + "\n")
            
    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    if not GROQ_API_KEY:
        print("Error: GROQ_API_KEY not found.")
    else:
        asyncio.run(run_phase2_tests())
