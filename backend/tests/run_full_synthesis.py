import asyncio
import sys
import os

# Set root to allow backend imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.agents.market_agent import market_agent

async def run_full_flow():
    query = "Deep dive into RELIANCE after the recent block deal"
    print(f"--- 🚀 Executing Full Neural Synthesis for: '{query}' ---")
    
    # We use chat_stream to get the thoughts + final report
    async for chunk in market_agent.chat_stream(query):
        print(chunk, end="", flush=True)
    
    print("\n\n✅ Investment Intelligence Synthesis Complete.")

if __name__ == "__main__":
    asyncio.run(run_full_flow())
