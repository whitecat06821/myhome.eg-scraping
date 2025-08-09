#!/usr/bin/env python3
"""
Enhanced MyHome.ge Property Owners Phone Number Scraper with Fixed Selenium
Handles "Show Number" button clicks and extracts hidden phone numbers
"""

import sys
import os
import logging
import time
import csv
import re
from typing import Set, List, Dict, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Add the scraper module to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.fetcher import MyHomeFetcher
from scraper.parser import MyHomeParser

class SeleniumOwnersPhoneScraper:
    """Enhanced scraper using Selenium to click Show Number buttons"""
    
    def __init__(self):
        """Initialize the selenium owners scraper"""
        self.setup_logging()
        
        self.fetcher = MyHomeFetcher()
        self.parser = MyHomeParser()
        
        # Set to store unique phone numbers
        self.owner_phones = set()
        
        # Initialize Selenium WebDriver
        self.driver = None
        self.init_selenium()
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('owners_selenium_fixed.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def init_selenium(self):
        """Initialize Selenium WebDriver with proper configuration"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Run in background
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36')
            
            # Install and use ChromeDriver
            service = webdriver.ChromeService(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            self.logger.info("Selenium WebDriver initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Selenium: {e}")
            self.driver = None
    
    def get_property_urls(self, max_pages=10, max_properties=100):
        """Get property URLs from the API"""
        self.logger.info(f"Getting property URLs (max: {max_properties})")
        
        property_urls = []
        page = 1
        
        while page <= max_pages and len(property_urls) < max_properties:
            self.logger.info(f"Fetching property listings page {page}")
            
            # Fetch property listings from API
            api_data = self.fetcher.fetch_property_listings_api(page)
            
            if not api_data:
                self.logger.error(f"Failed to fetch property listings API page {page}")
                break
            
            # Parse property URLs from API response
            properties = self.parser.parse_property_listings_api_response(api_data)
            
            if not properties:
                self.logger.info(f"No more properties found on page {page}, stopping")
                break
            
            self.logger.info(f"Found {len(properties)} properties on page {page}")
            
            # Add property URLs to our list
            for property_info in properties:
                if len(property_urls) >= max_properties:
                    break
                property_urls.append(property_info['url'])
            
            page += 1
            time.sleep(1)  # Rate limiting
        
        self.logger.info(f"Collected {len(property_urls)} property URLs")
        return property_urls
    
    def extract_phone_with_selenium(self, property_url: str) -> Set[str]:
        """Extract phone numbers using Selenium to click Show Number button"""
        phones = set()
        
        if not self.driver:
            return phones
        
        try:
            self.logger.debug(f"Loading property page: {property_url}")
            
            # Load the property page
            self.driver.get(property_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Look for Show Number button (various possible selectors)
            show_number_selectors = [
                "button[data-testid*='show']",
                "button[class*='show']",
                "button[class*='phone']",
                "button[onclick*='show']",
                "button:contains('ნომრის ჩვენება')",  # Georgian text
                "button:contains('Show Number')",
                ".show-phone",
                ".show-number",
                "[data-phone]"
            ]
            
            button_clicked = False
            
            for selector in show_number_selectors:
                try:
                    # Find and click the show number button
                    button = WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    button.click()
                    button_clicked = True
                    self.logger.debug(f"Clicked show number button with selector: {selector}")
                    break
                except (TimeoutException, NoSuchElementException):
                    continue
            
            if button_clicked:
                # Wait for phone number to appear
                time.sleep(2)
                
                # Check localStorage for phone number
                try:
                    local_storage = self.driver.execute_script("return localStorage;")
                    for key, value in local_storage.items():
                        if 'phone' in key.lower() and value:
                            phone = self.clean_phone_number(value)
                            if phone:
                                phones.add(phone)
                except Exception as e:
                    self.logger.debug(f"Error reading localStorage: {e}")
            
            # Extract any visible phone numbers from page source
            page_source = self.driver.page_source
            page_phones = self.extract_phone_from_html(page_source)
            phones.update(page_phones)
            
            if phones:
                self.logger.info(f"Found {len(phones)} phone numbers via Selenium: {list(phones)}")
            
        except Exception as e:
            self.logger.error(f"Error extracting phone with Selenium from {property_url}: {e}")
        
        return phones
    
    def extract_phone_from_html(self, html_content: str) -> Set[str]:
        """Extract phone numbers from HTML content"""
        phones = set()
        
        if not html_content:
            return phones
        
        # Georgian phone number patterns
        phone_patterns = [
            r'\b5\d{8}\b',  # 5XXXXXXXX format
            r'\b\+995\s*5\d{8}\b',  # +995 5XXXXXXXX format  
            r'\b995\s*5\d{8}\b',  # 995 5XXXXXXXX format
            r'\b5\d{2}[\s\-]?\d{3}[\s\-]?\d{3}\b',  # 5XX XXX XXX format
            r'\b5\d{2}[\s\-]?\d{2}[\s\-]?\d{2}[\s\-]?\d{2}\b'  # 5XX XX XX XX format
        ]
        
        for pattern in phone_patterns:
            matches = re.findall(pattern, html_content)
            for match in matches:
                # Clean the phone number
                clean_phone = self.clean_phone_number(match)
                if clean_phone:
                    phones.add(clean_phone)
        
        return phones
    
    def clean_phone_number(self, phone: str) -> str:
        """Clean and validate phone number"""
        if not phone:
            return None
        
        # Remove non-digit characters
        clean_phone = re.sub(r'[^\d]', '', str(phone))
        
        # Check if it's a valid Georgian mobile number
        if len(clean_phone) >= 9 and clean_phone.startswith('5'):
            if len(clean_phone) == 9:
                return clean_phone
            elif len(clean_phone) > 9 and clean_phone.startswith('9955'):
                # Remove country code
                return clean_phone[3:]
        
        return None
    
    def scrape_owners(self, max_pages=20, target_count=1000):
        """Scrape property owner phone numbers using Selenium"""
        self.logger.info(f"Starting property owners scraping with Selenium (target: {target_count})")
        
        if not self.driver:
            self.logger.error("Selenium WebDriver not available")
            return 0
        
        # Get property URLs
        property_urls = self.get_property_urls(max_pages=max_pages, max_properties=target_count*3)
        
        if not property_urls:
            self.logger.error("No property URLs found")
            return 0
        
        # Scrape phone numbers from each property
        for i, property_url in enumerate(property_urls, 1):
            if len(self.owner_phones) >= target_count:
                self.logger.info(f"Reached target count of {target_count} unique phone numbers!")
                break
                
            self.logger.info(f"Scraping property {i}/{len(property_urls)}: {property_url}")
            
            # Get phone numbers from this property
            property_phones = self.extract_phone_with_selenium(property_url)
            
            # Add unique phone numbers
            new_phones = property_phones - self.owner_phones
            if new_phones:
                self.owner_phones.update(new_phones)
                self.logger.info(f"Added {len(new_phones)} new phone numbers. Total: {len(self.owner_phones)}")
            
            # Rate limiting
            time.sleep(3)
        
        self.logger.info(f"Selenium scraping completed. Total unique phone numbers: {len(self.owner_phones)}")
        return len(self.owner_phones)
    
    def export_to_csv(self, filename="owners_selenium.csv"):
        """Export owner phone numbers to CSV"""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Phone'])  # Header
                
                for phone in sorted(self.owner_phones):
                    writer.writerow([phone])
            
            self.logger.info(f"Exported {len(self.owner_phones)} owner phone numbers to {filename}")
            
        except Exception as e:
            self.logger.error(f"Error exporting to CSV: {e}")
    
    def get_stats(self):
        """Get scraping statistics"""
        return {
            'owners_count': len(self.owner_phones)
        }
    
    def close(self):
        """Close all connections"""
        if self.driver:
            self.driver.quit()
        if self.fetcher:
            self.fetcher.close()

def main():
    """Main function to run the selenium owners scraper"""
    scraper = None
    try:
        print("🏠 Enhanced MyHome.ge Property Owners Phone Scraper (Selenium)")
        print("=" * 65)
        
        # Initialize scraper
        scraper = SeleniumOwnersPhoneScraper()
        
        # Start scraping (target: 700-1000 phone numbers)
        owners_count = scraper.scrape_owners(max_pages=30, target_count=1000)
        
        # Export results
        if owners_count > 0:
            scraper.export_to_csv("owners_selenium.csv")
        
        # Print final statistics
        stats = scraper.get_stats()
        print(f"\n✅ Scraping completed!")
        print(f"📱 Total unique owner phone numbers: {stats['owners_count']}")
        
        if stats['owners_count'] > 0:
            print(f"📄 Results saved to: owners_selenium.csv")
        else:
            print("❌ No phone numbers found.")
        
    except KeyboardInterrupt:
        print("\n⚠️ Scraping interrupted by user")
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        logging.error(f"Fatal error: {e}")
    finally:
        if scraper:
            scraper.close()

if __name__ == "__main__":
    main()
