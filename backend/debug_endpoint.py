import asyncio
import traceback
from backend.core.foliopp_core.pipeline.nse_bulk_ingestion import bulk_ingestor

async def debug():
    try:
        print("Starting test run of bulk_ingestor...")
        result = await bulk_ingestor.run({"period": "1M"})
        print(f"Success! Result: {result}")
    except Exception:
        print("Encountered error in bulk_ingestor:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug())
