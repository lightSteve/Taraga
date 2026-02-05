import pandas as pd
from sqlalchemy.orm import Session
from database import SessionLocal
from models import StockKR


def sync_krx_stocks():
    print("🚀 Starting KRX Stock Sync...")

    # KRX KIND Download URL
    url = "http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13"

    import requests
    from io import StringIO

    try:
        print(f"📥 Downloading data from {url}...")

        # Use requests to get content and decode manually
        response = requests.get(url)
        response.raise_for_status()

        # Convert bytes to string using euc-kr
        html_content = response.content.decode("euc-kr")

        # Parse using StringIO
        dfs = pd.read_html(StringIO(html_content), header=0)
        df = dfs[0]

        print(f"✅ Downloaded {len(df)} companies.")

        # Rename columns (Korean -> English mapping based on response)
        # Expected cols: '회사명', '종목코드', '업종', '주요제품', '상장일', '결산월', '대표자명', '홈페이지', '지역'
        df = df[["회사명", "종목코드", "업종"]]
        df.columns = ["name", "ticker", "sector"]

        # Format Ticker: 1234 -> 001234
        df["ticker"] = df["ticker"].astype(str).str.zfill(6)

        db = SessionLocal()
        count = 0
        updated = 0

        for index, row in df.iterrows():
            ticker = row["ticker"]
            name = row["name"]
            sector = row["sector"]

            # Upsert Logic
            existing = db.query(StockKR).filter(StockKR.ticker == ticker).first()
            if not existing:
                stock = StockKR(ticker=ticker, name=name, sector=sector)
                db.add(stock)
                count += 1
            else:
                if existing.sector != sector:  # Update sector if changed
                    existing.sector = sector
                    updated += 1

        db.commit()
        db.close()

        print(
            f"🎉 Sync Complete! Added: {count}, Updated: {updated}, Total in DB: {len(df)}"
        )

    except Exception as e:
        print(f"❌ Error during sync: {e}")


if __name__ == "__main__":
    sync_krx_stocks()
