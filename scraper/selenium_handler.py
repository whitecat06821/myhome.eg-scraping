import time
import logging
import os
from typing import Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)

class SeleniumHandler:
    def __init__(self, headless=True):
        self.driver = None
        self.headless = headless
        self.wait_timeout = 10
    
    def start_driver(self):
        try:
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument("--headless")
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
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
                    raise
            
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            logger.info("Selenium WebDriver started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start WebDriver: {e}")
            raise
    
    def get_page_with_phone(self, url: str) -> Optional[str]:
        if not self.driver:
            self.start_driver()
        
        try:
            logger.info(f"Fetching page with Selenium: {url}")
            self.driver.get(url)
            
            time.sleep(2)
            self._click_show_number_buttons()
            time.sleep(1)
            
            page_source = self.driver.page_source
            logger.debug(f"Successfully fetched page: {url}")
            return page_source
            
        except Exception as e:
            logger.error(f"Failed to fetch page with Selenium: {url} - {e}")
            return None
    
    def _click_show_number_buttons(self):
        try:
            buttons = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Show') and contains(text(), 'Number')]")
            buttons.extend(self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Show') and contains(text(), 'Phone')]"))
            buttons.extend(self.driver.find_elements(By.CSS_SELECTOR, ".show-number, .show-phone"))
            
            for button in buttons:
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView();", button)
                    time.sleep(0.5)
                    button.click()
                    logger.debug("Clicked 'Show Number' button")
                    time.sleep(0.5)
                except Exception as e:
                    logger.debug(f"Failed to click button: {e}")
                    continue
                    
        except Exception as e:
            logger.warning(f"Error clicking show number buttons: {e}")
    
    def close(self):
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Selenium WebDriver closed")
            except Exception as e:
                logger.error(f"Error closing WebDriver: {e}")
            finally:
                self.driver = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def get_property_phone_with_selenium(self, property_url: str) -> Optional[str]:
        """Get property phone number using Selenium by clicking show number button"""
        try:
            logger.info(f"Getting property phone with Selenium: {property_url}")
            
            # Navigate to property page
            self.driver.get(property_url)
            time.sleep(3)  # Wait for page to load
            
            # Look for the "Show number" button
            show_number_selectors = [
                'button[class*="show"]',
                'button[class*="phone"]',
                'button[class*="number"]',
                '[class*="show-number"]',
                '[class*="phone-button"]',
                'button:contains("Show")',
                'button:contains("Phone")',
                'button:contains("Number")'
            ]
            
            show_button = None
            for selector in show_number_selectors:
                try:
                    show_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if show_button and show_button.is_displayed():
                        logger.info(f"Found show number button with selector: {selector}")
                        break
                except:
                    continue
            
            if not show_button:
                logger.warning("Could not find show number button")
                return None
            
            # Click the show number button
            show_button.click()
            logger.info("Clicked show number button")
            time.sleep(2)  # Wait for phone to appear
            
            # Try to get phone from localStorage
            try:
                phone_numbers = self.driver.execute_script("return localStorage.getItem('phoneNumbers');")
                if phone_numbers:
                    import json
                    phones = json.loads(phone_numbers)
                    if phones and len(phones) > 0:
                        phone = phones[0]  # Get first phone number
                        logger.info(f"Found phone in localStorage: {phone}")
                        return phone
            except Exception as e:
                logger.warning(f"Could not get phone from localStorage: {e}")
            
            # Fallback: look for phone number in the page content
            page_source = self.driver.page_source
            phone_patterns = [
                r'\+995\s*\d{3}\s*\d{3}\s*\d{3}',
                r'995\s*\d{3}\s*\d{3}\s*\d{3}',
                r'\d{3}\s*\d{3}\s*\d{3}',
                r'\d{9}',
            ]
            
            for pattern in phone_patterns:
                import re
                matches = re.findall(pattern, page_source)
                for match in matches:
                    # Clean and validate phone number
                    digits = re.sub(r'\D', '', match)
                    if len(digits) == 9 and digits.startswith('5'):
                        phone = f"+995{digits}"
                        logger.info(f"Found phone in page content: {phone}")
                        return phone
                    elif len(digits) == 12 and digits.startswith('995'):
                        phone = f"+{digits}"
                        logger.info(f"Found phone in page content: {phone}")
                        return phone
            
            logger.warning("No phone number found after clicking show number button")
            return None
            
        except Exception as e:
            logger.error(f"Error getting property phone with Selenium: {e}")
            return None
