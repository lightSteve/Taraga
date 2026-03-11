from services.service_factory import ServiceFactory
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_service():
    print("Testing YahooFinanceService.get_market_indices()...")
    service = ServiceFactory.get_market_data_service()
    try:
        indices = service.get_market_indices()
        print(f"Result: {indices}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_service()
