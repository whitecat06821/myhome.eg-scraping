#!/usr/bin/env python3
"""
MyHome.ge Property Owners Phone Number Scraper
Dedicated script for scraping property owner phone numbers only.
"""

import sys
import os
import logging
import time
import csv
from typing import Optional, Dict, Any, Set

# Add the scraper module to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.fetcher import MyHomeFetcher
from scraper.parser import MyHomeParser
from scraper.selenium_handler import SeleniumHandler

class OwnersPhoneScraper:
    """Dedicated scraper for property owner phone numbers"""
    
    def __init__(self, use_selenium=True):
        """Initialize the owners scraper"""
        # Setup logging first
        self.setup_logging()
        
        self.fetcher = MyHomeFetcher()
        self.parser = MyHomeParser()
        self.use_selenium = use_selenium
        self.selenium_handler = None
        
        if self.use_selenium:
            try:
                self.selenium_handler = SeleniumHandler()
                self.logger.info("Selenium initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize Selenium: {e}")
                self.use_selenium = False
        
        # Set to store unique phone numbers
        self.owner_phones = set()
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('owners_scraper.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def scrape_owners(self, max_pages=50, target_count=1000):
        """Scrape property owner phone numbers"""
        self.logger.info(f"Starting property owners scraping (target: {target_count})")
        
        total_owners_found = 0
        page = 1
        
        while page <= max_pages and total_owners_found < target_count:
            self.logger.info(f"Scraping property listings page {page}")
            
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
            
            # Scrape each property detail page
            for property_info in properties:
                if total_owners_found >= target_count:
                    self.logger.info(f"Reached target count of {target_count} owners! Stopping...")
                    break
                
                try:
                    property_url = property_info['url']
                    self.logger.info(f"Scraping property: {property_url}")
                    
                    phone = self.get_property_phone(property_info, property_url)
                    
                    if phone and phone not in self.owner_phones:
                        self.owner_phones.add(phone)
                        total_owners_found += 1
                        self.logger.info(f"Added owner phone #{total_owners_found}: {phone}")
                    elif phone:
                        self.logger.debug(f"Duplicate phone number: {phone}")
                    else:
                        self.logger.debug(f"No valid phone number found for {property_url}")
                    
                    # Rate limiting
                    time.sleep(1)
                    
                except Exception as e:
                    self.logger.error(f"Error scraping property {property_url}: {e}")
            
            page += 1
        
        self.logger.info(f"Property owners scraping completed. Total unique owners: {len(self.owner_phones)}")
        return len(self.owner_phones)
    
    def get_property_phone(self, property_info: Dict[str, str], property_url: str) -> Optional[str]:
        """Get phone number for a property using multiple methods"""
        phone = None
        
        # Method 1: Try Selenium approach (most reliable for "Show Number" button)
        if self.use_selenium and self.selenium_handler:
            try:
                self.logger.debug(f"Using Selenium for {property_url}")
                phone = self.selenium_handler.get_property_phone_with_selenium(property_url)
                if phone:
                    return phone
            except Exception as e:
                self.logger.error(f"Selenium error for {property_url}: {e}")
        
        # Method 2: Try API approach using property UUID
        try:
            # Use UUID from property info if available
            statement_uuid = property_info.get('uuid')
            
            # Fallback to extracting UUID from page
            if not statement_uuid:
                statement_uuid = self.parser.extract_statement_uuid_from_url(property_url, self.fetcher)
            
            if statement_uuid:
                api_data = self.fetcher.fetch_property_phone_api(statement_uuid)
                if api_data:
                    phone = self.parser.parse_property_phone_api_response(api_data)
                    if phone:
                        return phone
        except Exception as e:
            self.logger.error(f"API error for {property_url}: {e}")
        
        return None
    
    def export_to_csv(self, filename="owners.csv"):
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
        if self.fetcher:
            self.fetcher.close()
        if self.selenium_handler:
            self.selenium_handler.close()

def main():
    """Main function to run the owners scraper"""
    scraper = None
    try:
        print("🏠 MyHome.ge Property Owners Phone Scraper")
        print("=" * 50)
        
        # Initialize scraper with Selenium enabled
        scraper = OwnersPhoneScraper(use_selenium=True)
        
        # Start scraping (target: 700-1000 owners)
        owners_count = scraper.scrape_owners(max_pages=50, target_count=900)
        
        # Export results
        scraper.export_to_csv("owners.csv")
        
        # Print final statistics
        stats = scraper.get_stats()
        print(f"\n✅ Scraping completed!")
        print(f"📱 Total unique owner phone numbers: {stats['owners_count']}")
        print(f"📄 Results saved to: owners.csv")
        
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
