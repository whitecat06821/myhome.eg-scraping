import logging
from scraper.parser import MyHomeParser
from scraper.data_storage import DataStorage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_phone_number_extraction():
    parser = MyHomeParser()
    
    test_cases = [
        "+995 555 123 456",
        "995 555 123 456", 
        "555 123 456",
        "555123456",
        "Contact us at +995 555 123 456 or call 555 789 012"
    ]
    
    for test_case in test_cases:
        phone = parser._find_phone_in_text(test_case)
        if phone:
            logger.info(f"Extracted phone: {phone} from '{test_case}'")
        else:
            logger.warning(f"No phone found in: '{test_case}'")

if __name__ == "__main__":
    logger.info("Starting scraper tests...")
    test_phone_number_extraction()
    logger.info("Test completed successfully!")
