import logging
import time
from selenium_handler import SeleniumHandler
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_myhome_with_wait():
    """Test if Selenium can load myhome.ge agents page with longer wait"""
    handler = SeleniumHandler()
    
    try:
        logger.info("Starting Selenium...")
        success = handler.start_driver()
        
        if not success:
            logger.error("Failed to start Selenium driver")
            return False
            
        logger.info("Selenium started successfully!")
        
        # Test loading myhome.ge agents page
        logger.info("Loading myhome.ge agents page...")
        html = handler.get_page_with_phone("https://www.myhome.ge/maklers/")
        
        if html:
            logger.info(f"Successfully loaded page, HTML length: {len(html)}")
            
            # Wait longer for dynamic content to load
            logger.info("Waiting for dynamic content to load...")
            time.sleep(10)  # Wait 10 seconds
            
            # Try to find agent links using Selenium
            try:
                # Look for agent links with various selectors
                selectors = [
                    "a[href*='/maklers/']",
                    ".group a[href*='/maklers/']",
                    "[href*='/maklers/']",
                    "a[href*='maklers']"
                ]
                
                for selector in selectors:
                    try:
                        elements = handler.driver.find_elements(By.CSS_SELECTOR, selector)
                        logger.info(f"Found {len(elements)} elements with selector: {selector}")
                        
                        if elements:
                            logger.info("Sample agent links found:")
                            for i, element in enumerate(elements[:5]):
                                href = element.get_attribute('href')
                                text = element.text
                                logger.info(f"  {i+1}. {text} -> {href}")
                            
                            # Save the updated HTML
                            updated_html = handler.driver.page_source
                            with open("myhome_agents_updated.html", "w", encoding="utf-8") as f:
                                f.write(updated_html)
                            logger.info("Saved updated HTML to myhome_agents_updated.html")
                            
                            return True
                            
                    except Exception as e:
                        logger.debug(f"Selector {selector} failed: {e}")
                
                logger.warning("No agent links found with any selector")
                return False
                
            except Exception as e:
                logger.error(f"Error finding agent links: {e}")
                return False
        else:
            logger.error("Failed to load page")
            return False
            
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        return False
    finally:
        handler.close()

if __name__ == "__main__":
    test_myhome_with_wait()
