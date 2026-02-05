import yfinance as yf

SP500_MAJOR_TICKERS = ["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA"]
tickers_str = " ".join(SP500_MAJOR_TICKERS)
print(f"Downloading: {tickers_str}")

data = yf.download(tickers_str, period="2d", group_by="ticker", progress=False)
print("\nData Shape:", data.shape)
print("\nColumns:", data.columns)
print("\nData Head:\n", data.head())

if not data.empty:
    print("\nAttempting to access AAPL:")
    try:
        aapl_df = data["AAPL"]
        print(aapl_df.head())
        print("Close:", aapl_df["Close"].iloc[-1])
    except Exception as e:
        print(f"Error accessing AAPL: {e}")
