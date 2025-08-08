import logging
from selenium_handler import SeleniumHandler

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_selenium():
    """Test if Selenium can start and load a simple page"""
    handler = SeleniumHandler()
    
    try:
        logger.info("Testing Selenium startup...")
        success = handler.start_driver()
        
        if not success:
            logger.error("Failed to start Selenium driver")
            return False
            
        logger.info("Selenium started successfully!")
        
        # Test loading a simple page
        logger.info("Testing page loading...")
        html = handler.get_page_with_phone("https://www.google.com")
        
        if html:
            logger.info(f"Successfully loaded page, HTML length: {len(html)}")
            logger.info("Selenium test PASSED!")
            return True
        else:
            logger.error("Failed to load page")
            return False
            
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        return False
    finally:
        handler.close()

if __name__ == "__main__":
    test_selenium()
