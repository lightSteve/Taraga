import yfinance as yf


def verify_global_indices():
    # US, KR, Coin
    tickers = {
        "🇺🇸 S&P 500": "^GSPC",
        "🇰🇷 KOSPI": "^KS11",
        "🇰🇷 KOSDAQ": "^KQ11",
        "🪙 BTC": "BTC-USD",
        "🪙 ETH": "ETH-USD",
    }

    ticker_str = " ".join(tickers.values())
    print(f"Downloading: {ticker_str}")

    data = yf.download(ticker_str, period="5d", progress=False)

    print("\nResults:")
    for name, symbol in tickers.items():
        try:
            if len(tickers) > 1:
                df = (
                    data.xs(symbol, axis=1, level=1)
                    if isinstance(data.columns, pd.MultiIndex)
                    else data
                )
                # yfinance format varies; recent versions use MultiIndex (Price, Ticker)
                # Let's check columns first
                pass

            # Simple check via Ticker object for safety if batch fails structure
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")
            if not hist.empty:
                current = hist["Close"].iloc[-1]
                prev = hist["Close"].iloc[0]
                change = ((current - prev) / prev) * 100
                print(f"{name} ({symbol}): {current:.2f} ({change:+.2f}%)")
            else:
                print(f"{name} ({symbol}): No Data")
        except Exception as e:
            print(f"{name} ({symbol}): Error {e}")

    # Fallback batch check logic
    print("\nBatch Data Columns:")
    print(data.columns)


if __name__ == "__main__":
    import pandas as pd

    verify_global_indices()
