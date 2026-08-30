import asyncio
import httpx
import traceback

ENDPOINTS = [
    "http://localhost:8000/api/institutional/latest-bulk-deals",
    "http://localhost:8000/equity/news?symbol=RELIANCE&exchange=NSE",
    "http://localhost:8000/market/news",
    "http://localhost:8000/equity/technical-analysis?symbol=RELIANCE&exchange=NSE",
    "http://localhost:8000/api/portfolio",
]

async def test_endpoint(client, url):
    try:
        print(f"Testing {url}...")
        resp = await client.get(url, timeout=30.0)
        if resp.status_code == 200:
            print(f"✅ SUCCESS: {url}")
        else:
            print(f"❌ FAILED ({resp.status_code}): {url}")
            print(f"   Response: {resp.text[:200]}...")
    except Exception as e:
        print(f"💥 ERROR: {url}")
        print(f"   Exception: {e}")

async def main():
    async with httpx.AsyncClient() as client:
        tasks = [test_endpoint(client, url) for url in ENDPOINTS]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
