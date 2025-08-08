import logging
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)

class SeleniumHandler:
    def __init__(self):
        self.driver = None
        
    def start_driver(self):
        """Start Chrome WebDriver with proper configuration"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Use the correct ChromeDriver path
            driver_path = r"C:\Users\Success\.wdm\drivers\chromedriver\win64\139.0.7258.66\chromedriver-win32\chromedriver.exe"
            
            if os.path.exists(driver_path):
                logger.info(f"Using ChromeDriver: {driver_path}")
                service = Service(driver_path)
            else:
                logger.warning(f"ChromeDriver not found at {driver_path}, trying webdriver-manager")
                try:
                    driver_path = ChromeDriverManager().install()
                    # Fix the path if it points to wrong file
                    if "THIRD_PARTY_NOTICES" in driver_path:
                        driver_dir = os.path.dirname(driver_path)
                        actual_driver = os.path.join(driver_dir, "chromedriver.exe")
                        if os.path.exists(actual_driver):
                            driver_path = actual_driver
                    service = Service(driver_path)
                except Exception as e:
                    logger.error(f"Failed to get ChromeDriver: {e}")
                    return False
            
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(10)
            logger.info("Chrome WebDriver started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Chrome WebDriver: {e}")
            return False
    
    def get_page_with_phone(self, url):
        """Get page content and click show number buttons if needed"""
        if not self.driver:
            logger.error("WebDriver not started")
            return None
            
        try:
            logger.info(f"Loading page: {url}")
            self.driver.get(url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Try to click "Show Number" buttons
            self._click_show_number_buttons()
            
            # Get the final HTML
            html_content = self.driver.page_source
            logger.info(f"Page loaded successfully, HTML length: {len(html_content)}")
            return html_content
            
        except Exception as e:
            logger.error(f"Error loading page {url}: {e}")
            return None
    
    def _click_show_number_buttons(self):
        """Click all 'Show Number' buttons on the page"""
        try:
            # Common selectors for show number buttons
            button_selectors = [
                "button:contains('Show Number')",
                "button:contains('Show Phone')", 
                "span:contains('Show Number')",
                ".show-number-btn",
                "[data-action='show-phone']"
            ]
            
            for selector in button_selectors:
                try:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for button in buttons:
                        if button.is_displayed() and button.is_enabled():
                            self.driver.execute_script("arguments[0].click();", button)
                            time.sleep(0.5)
                            logger.debug(f"Clicked show number button: {selector}")
                except Exception as e:
                    logger.debug(f"Could not find buttons with selector {selector}: {e}")
                    
        except Exception as e:
            logger.warning(f"Error clicking show number buttons: {e}")
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver closed successfully")
            except Exception as e:
                logger.error(f"Error closing WebDriver: {e}")
            finally:
                self.driver = None
