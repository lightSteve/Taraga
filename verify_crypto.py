import yfinance as yf
import pandas as pd
from datetime import datetime

tickers = "BTC-USD ETH-USD"
print(f"Fetching data for {tickers} at {datetime.now()}...")

data = yf.download(
    tickers,
    period="5d",  # 5 days to be sure to get history
    group_by="ticker",
    progress=False,
    threads=False,
)

for ticker in ["BTC-USD", "ETH-USD"]:
    print(f"\n--- {ticker} ---")
    if isinstance(data.columns, pd.MultiIndex):
        try:
            df = data.xs(ticker, axis=1, level=1)  # Try level 1 first
        except KeyError:
            df = data[ticker]  # Fallback
    else:
        df = data

    print(df.tail(3)[["Close", "Open", "High", "Low"]])

    if len(df) >= 2:
        current = df["Close"].iloc[-1]
        prev = df["Close"].iloc[-2]
        change = ((current - prev) / prev) * 100
        print(
            f"Calculated Change: {change:.2f}% (Current: {current:.2f}, Prev Close: {prev:.2f})"
        )
    else:
        print("Not enough data")
