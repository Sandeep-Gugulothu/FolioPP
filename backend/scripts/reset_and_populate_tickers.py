import asyncio
import sys
import os
from sqlalchemy import text, select, delete

# Set root to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.clients.postgres import AsyncSessionLocal
from backend.core.foliopp_core.database.models import NSETicker

async def reset_and_populate():
    print("--- Resetting and Repopulating Tickers from Clean Slate ---")
    
    raw_symbols = "HDFCBANK, RELIANCE, BHARTIARTL, ICICIBANK, LT, SBIN, SAMMAANCAP, KOTAKBANK, ETERNAL, BAJFINANCE, TCS, INFY, SHRIRAMFIN, BSE, AXISBANK, LODHA, KAYNES, M&M, INDIGO, VEDL, MCX, ITC, TECHM, MARUTI, TATASTEEL, BEL, DIXON, HCLTECH, SWIGGY, WAAREEENER, TITAN, BPCL, DMART, COFORGE, ULTRACEMCO, POWERGRID, ADANIENT, HINDPETRO, HINDUNILVR, HINDZINC, GRASIM, PGEL, UNITDSPR, BAJAJ-AUTO, IDEA, HINDALCO, HAL, PERSISTENT, COALINDIA, TRENT, TVSMOTOR, PFC, CHOLAFIN, JIOFIN, BANKBARODA, VBL, ONGC, MUTHOOTFIN, POLYCAB, NTPC, SAIL, EICHERMOT, APOLLOHOSP, SUNPHARMA, BAJAJFINSV, SUZLON, DLF, IOC, INDUSTOWER, UNIONBANK, CUMMINSIND, NATIONALUM, POLICYBZR, BHARATFORG, CDSL, CANBK, KEI, ASIANPAINT, POWERINDIA, KALYANKJIL, HEROMOTOCO, MAZDOCK, LUPIN, TATAPOWER, AMBER, MAXHEALTH, PAYTM, FEDERALBNK, WIPRO, RVNL, SOLARINDS, ADANIPORTS, INDUSINDBK, TMPV, PREMIERENE, AUROPHARMA, MOTHERSON, GAIL, INDIANB, OIL"
    
    symbols = [f"{s.strip()}.NS" if not s.strip().endswith(".NS") else s.strip() for s in raw_symbols.split(",")]

    async with AsyncSessionLocal() as db:
        # 1. Clear everything
        try:
            print("Clearing nse_tickers table...")
            await db.execute(text("TRUNCATE TABLE nse_tickers CASCADE;"))
            await db.commit()
            
            # 2. Re-populate with yfinance metadata
            import yfinance as yf
            for symbol in symbols:
                print(f"Processing {symbol}...", end=" ", flush=True)
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    
                    name = info.get("shortName") or info.get("longName") or symbol
                    sector = info.get("sector") or info.get("industry") or "Misc"
                    market_cap = info.get("marketCap") or 0.0
                    
                    cap_in_cr = market_cap / 10000000
                    cap_bucket = "Small Cap"
                    if cap_in_cr > 20000: # > 20,000 Cr
                        cap_bucket = "Large Cap"
                    elif cap_in_cr > 5000: # > 5,000 Cr
                        cap_bucket = "Mid Cap"
                    
                    new_ticker = NSETicker(
                        symbol=symbol,
                        name=name,
                        sector=sector,
                        market_cap=market_cap,
                        market_cap_bucket=cap_bucket
                    )
                    db.add(new_ticker)
                    print(f"DONE: {sector} | {cap_bucket}")
                except Exception as e:
                    print(f"FAILED: {str(e)}")
                
                # Commit every 10 for safety
                if len(db.new) >= 10:
                    await db.commit()
            
            await db.commit()
            print("Successfully reset and populated tickers.")
        except Exception as e:
            await db.rollback()
            print(f"Global Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(reset_and_populate())
