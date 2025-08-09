#!/usr/bin/env python3
"""
Direct MyHome.ge Property Owners Phone Number Scraper
Uses direct HTTP requests to extract phone numbers from property pages
"""

import sys
import os
import logging
import time
import csv
import re
import requests
from typing import Set, List, Dict, Any

# Add the scraper module to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.fetcher import MyHomeFetcher
from scraper.parser import MyHomeParser

class DirectOwnersPhoneScraper:
    """Direct scraper for property owner phone numbers"""
    
    def __init__(self):
        """Initialize the direct owners scraper"""
        self.setup_logging()
        
        self.fetcher = MyHomeFetcher()
        self.parser = MyHomeParser()
        
        # Set to store unique phone numbers
        self.owner_phones = set()
        
        # Setup session for direct requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('owners_direct_scraper.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
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
                clean_phone = re.sub(r'[^\d]', '', match)
                # Check if it's a valid Georgian mobile number
                if len(clean_phone) >= 9 and clean_phone.startswith('5'):
                    if len(clean_phone) == 9:
                        phones.add(clean_phone)
                    elif len(clean_phone) > 9 and clean_phone.startswith('9955'):
                        # Remove country code
                        phones.add(clean_phone[3:])
        
        return phones
    
    def scrape_property_phone(self, property_url: str) -> Set[str]:
        """Scrape phone numbers from a single property page"""
        phones = set()
        
        try:
            self.logger.debug(f"Fetching property page: {property_url}")
            
            response = self.session.get(property_url, timeout=10)
            response.raise_for_status()
            
            html_content = response.text
            
            # Extract phone numbers from HTML
            found_phones = self.extract_phone_from_html(html_content)
            
            if found_phones:
                self.logger.info(f"Found {len(found_phones)} phone numbers in {property_url}: {list(found_phones)}")
                phones.update(found_phones)
            else:
                self.logger.debug(f"No phone numbers found in {property_url}")
            
        except Exception as e:
            self.logger.error(f"Error scraping property {property_url}: {e}")
        
        return phones
    
    def scrape_owners(self, max_pages=200, target_count=700, min_target=700):
        """Scrape property owner phone numbers"""
        self.logger.info(f"Starting property owners scraping (target: {target_count}, minimum: {min_target})")
        
        # Get property URLs (get more properties to account for low extraction rate)
        property_urls = self.get_property_urls(max_pages=max_pages, max_properties=5000)
        
        if not property_urls:
            self.logger.error("No property URLs found")
            return 0
        
        # Scrape phone numbers from each property
        for i, property_url in enumerate(property_urls, 1):
            if len(self.owner_phones) >= min_target:
                self.logger.info(f"✅ SUCCESS! Reached minimum target of {min_target} unique phone numbers!")
                self.logger.info(f"📊 Final count: {len(self.owner_phones)} phone numbers from {i} properties")
                break
                
            self.logger.info(f"Scraping property {i}/{len(property_urls)}: {property_url}")
            
            # Get phone numbers from this property
            property_phones = self.scrape_property_phone(property_url)
            
            # Add unique phone numbers
            new_phones = property_phones - self.owner_phones
            if new_phones:
                self.owner_phones.update(new_phones)
                self.logger.info(f"Added {len(new_phones)} new phone numbers. Total: {len(self.owner_phones)}")
                # Real-time CSV save every 5 new phones
                if len(self.owner_phones) % 5 == 0:
                    self.export_to_csv("owners_direct.csv")
            
            # Rate limiting
            time.sleep(2)
        
        self.logger.info(f"Scraping completed. Total unique phone numbers: {len(self.owner_phones)}")
        return len(self.owner_phones)
    
    def export_to_csv(self, filename="owners_direct.csv"):
        """Export owner phone numbers to CSV in proper format"""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Phone'])  # Header
                
                for phone in sorted(self.owner_phones):
                    # Format as +995XXXXXXXXX to prevent Excel scientific notation
                    formatted_phone = f"+995{phone}"
                    writer.writerow([formatted_phone])
            
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
        if self.session:
            self.session.close()

def main():
    """Main function to run the direct owners scraper"""
    scraper = None
    try:
        print("🏠 Direct MyHome.ge Property Owners Phone Scraper")
        print("=" * 55)
        
        # Initialize scraper
        scraper = DirectOwnersPhoneScraper()
        
        # Start scraping (minimum: 700 phone numbers, will stop once reached)
        owners_count = scraper.scrape_owners(max_pages=200, target_count=700, min_target=700)
        
        # Export results
        if owners_count > 0:
            scraper.export_to_csv("owners_direct.csv")
        
        # Print final statistics
        stats = scraper.get_stats()
        print(f"\n✅ Scraping completed!")
        print(f"📱 Total unique owner phone numbers: {stats['owners_count']}")
        
        if stats['owners_count'] > 0:
            print(f"📄 Results saved to: owners_direct.csv")
        else:
            print("❌ No phone numbers found. The website might require user interaction to show phone numbers.")
        
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
