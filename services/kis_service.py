import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

KIS_APP_KEY = os.getenv("KIS_APP_KEY")
KIS_APP_SECRET = os.getenv("KIS_APP_SECRET")
KIS_ACCOUNT_NO = os.getenv("KIS_ACCOUNT_NO")

# KIS API URLs
BASE_URL = "https://openapi.koreainvestment.com:9443"
TOKEN_URL = f"{BASE_URL}/oauth2/tokenP"
PRICE_URL = f"{BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price"


class KISService:
    """Service to fetch Korean stock market data from Korea Investment & Securities API"""

    def __init__(self, app_key: str = None, app_secret: str = None):
        self.app_key = app_key or KIS_APP_KEY
        self.app_secret = app_secret or KIS_APP_SECRET
        self.access_token = None

        if not self.app_key or not self.app_secret:
            raise ValueError("KIS API credentials are required")

    def get_access_token(self):
        """Get OAuth2 access token from KIS"""
        headers = {"content-type": "application/json"}
        body = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
        }

        response = requests.post(TOKEN_URL, headers=headers, data=json.dumps(body))
        response.raise_for_status()

        data = response.json()
        self.access_token = data.get("access_token")
        return self.access_token

    def get_stock_price(self, ticker: str):
        """Get current price for a Korean stock ticker"""
        if not self.access_token:
            self.get_access_token()

        headers = {
            "content-type": "application/json",
            "authorization": f"Bearer {self.access_token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "tr_id": "FHKST01010100",  # Transaction ID for price inquiry
        }

        params = {
            "FID_COND_MRKT_DIV_CODE": "J",  # Market division (J = KOSPI/KOSDAQ)
            "FID_INPUT_ISCD": ticker,  # Stock code
        }

        response = requests.get(PRICE_URL, headers=headers, params=params)
        response.raise_for_status()

        data = response.json()
        output = data.get("output", {})

        return {
            "ticker": ticker,
            "name": output.get("hts_kor_isnm"),  # Korean name
            "current_price": int(output.get("stck_prpr", 0)),  # Current price
            "change_percent": float(output.get("prdy_ctrt", 0)),  # Change %
            "volume": int(output.get("acml_vol", 0)),  # Accumulated volume
        }

    def get_multiple_prices(self, tickers: list):
        """Get prices for multiple Korean stocks"""
        results = []
        for ticker in tickers:
            try:
                price_data = self.get_stock_price(ticker)
                results.append(price_data)
            except Exception as e:
                print(f"Error fetching {ticker}: {e}")

        return results


if __name__ == "__main__":
    # Test the service
    service = KISService()

    # Test with Samsung Electronics (005930)
    print("📈 Samsung Electronics Price:")
    print(service.get_stock_price("005930"))
