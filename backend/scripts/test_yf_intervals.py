import yfinance as yf

intervals = ['1m','2m','5m','15m','30m','60m','90m','1h','1d','5d','1wk','1mo','3mo']

print("Testing intervals with period='1mo'")
print("-" * 60)
for interval in intervals:
    try:
        data = yf.download('RELIANCE.NS', interval=interval, period='1mo', progress=False, auto_adjust=False)
        if hasattr(data.columns, 'levels'):
            data.columns = [col[0] for col in data.columns]
        print(f"{interval:>5} -> rows: {len(data):>5}")
    except Exception as e:
        print(f"{interval:>5} -> ERROR: {e}")

print()
print("Testing max history per interval (how far back can we go?)")
print("-" * 60)
for interval in ['1m', '5m', '1h', '1d', '1wk', '1mo', '3mo']:
    try:
        data = yf.download('RELIANCE.NS', interval=interval, period='max', progress=False, auto_adjust=False)
        if hasattr(data.columns, 'levels'):
            data.columns = [col[0] for col in data.columns]
        if not data.empty:
            data = data.reset_index()
            date_col = 'Datetime' if 'Datetime' in data.columns else 'Date'
            print(f"{interval:>5} -> rows: {len(data):>6}  from: {data[date_col].iloc[0]}  to: {data[date_col].iloc[-1]}")
        else:
            print(f"{interval:>5} -> empty")
    except Exception as e:
        print(f"{interval:>5} -> ERROR: {e}")
