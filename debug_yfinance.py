import yfinance as yf
import pandas as pd


def test_yfinance():
    indices_map = {"^GSPC": "S&P 500", "^DJI": "Dow Jones", "^IXIC": "Nasdaq"}
    tickers_str = " ".join(indices_map.keys())
    print(f"Downloading: {tickers_str}")

    try:
        data = yf.download(tickers_str, period="5d", group_by="ticker", progress=False)
        print("\nDownload complete.")
        print(f"Data type: {type(data)}")
        if isinstance(data, pd.DataFrame):
            print(f"Columns: {data.columns}")
            print("\nHead:\n", data.head())

            for symbol in indices_map.keys():
                print(f"\nProcessing {symbol}...")
                try:
                    if len(indices_map) == 1:
                        df = data
                    else:
                        # existing logic
                        if symbol in data.columns.get_level_values(0):
                            df = data[symbol]
                        else:
                            print(f"Symbol {symbol} not in columns level 0")
                            continue

                    print(f"DF for {symbol}:\n{df.head()}")
                    df = df.dropna(subset=["Close"])
                    print(f"Last 2 rows:\n{df.tail(2)}")
                except Exception as e:
                    print(f"Error processing {symbol}: {e}")

    except Exception as e:
        print(f"Download failed: {e}")


if __name__ == "__main__":
    test_yfinance()
