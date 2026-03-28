import asyncio
import sys
import os

# Set root to allow backend imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.agents.market_agent import market_agent

def test_extract_symbol():
    print("--- 🔍 Testing: _extract_symbol() ---")
    
    test_cases = [
        ("Analyze RELIANCE now", "RELIANCE"),
        ("What is the LTP for SBIN.NS?", "SBIN"),
        ("Compare TCS and INFY", "TCS"), # Should pick the FIRST one based on regex
        ("How is my portfolio?", None),
        ("Buy 100 shares of HDFCBANK", "HDFCBANK"),
        ("Check the price of AAPL", "AAPL"), # Non-NSE might not get .NS if not recognized as default (my current regex adds .NS to 2-10 char strings)
        ("Is MSFT going up?", "MSFT.NS") # My current regex adds .NS to MSFT if it's alphanumeric and length <= 10.
    ]
    
    for query, expected in test_cases:
        result = market_agent._extract_symbol(query)
        status = "✅ PASS" if result == expected else f"❌ FAIL (Got: {result}, Expected: {expected})"
        print(f"Query: '{query}' -> Extracted: {result} | {status}")

if __name__ == "__main__":
    test_extract_symbol()
