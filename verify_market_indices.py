import logging
import yfinance as yf
from services.yahoo_finance_service import YahooFinanceService

# Configure logging
logging.basicConfig(level=logging.INFO)


def verify_indices():
    service = YahooFinanceService()
    print("Fetching market indices...")
    indices = service.get_market_indices()
    print("\nResult:")
    print(indices)

    # Manual check for S&P 500 (^GSPC)
    print("\nManual check for ^GSPC:")
    data = yf.download("^GSPC", period="5d", progress=False)
    print(data.tail())


if __name__ == "__main__":
    verify_indices()
