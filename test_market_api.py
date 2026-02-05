import requests
import time

BASE_URL = "http://localhost:8000/api/v1"


def test_endpoint(endpoint):
    print(f"Testing {endpoint}...")
    start = time.time()
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
        elapsed = time.time() - start
        print(f"Status: {response.status_code}, Time: {elapsed:.2f}s")
        if response.status_code == 200:
            data = response.json()
            print(f"Data: {str(data)[:100]}...")  # Print first 100 chars
        else:
            print(f"Error: {response.text}")
    except requests.Timeout:
        print("❌ TIMEOUT (10s)")
    except Exception as e:
        print(f"❌ ERROR: {e}")


if __name__ == "__main__":
    test_endpoint("/market/us/top-gainers")
    test_endpoint("/market/us/top-losers")
