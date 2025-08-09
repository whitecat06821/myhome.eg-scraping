#!/usr/bin/env python3
"""
Simple MyHome.ge Property Owners Phone Number Scraper
Focused on getting property data and extracting phone numbers via manual inspection
"""

import sys
import os
import logging
import time
import csv
import json
from typing import Optional, Dict, Any, Set, List

# Add the scraper module to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.fetcher import MyHomeFetcher
from scraper.parser import MyHomeParser

class SimpleOwnersPhoneScraper:
    """Simple scraper for property owner phone numbers"""
    
    def __init__(self):
        """Initialize the simple owners scraper"""
        # Setup logging first
        self.setup_logging()
        
        self.fetcher = MyHomeFetcher()
        self.parser = MyHomeParser()
        
        # List to store property information
        self.properties = []
        self.owner_phones = set()
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('owners_simple_scraper.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def collect_property_data(self, max_pages=10, max_properties=100):
        """Collect property data from API"""
        self.logger.info(f"Collecting property data (max: {max_properties})")
        
        page = 1
        total_collected = 0
        
        while page <= max_pages and total_collected < max_properties:
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
            
            # Add properties to our collection
            for property_info in properties:
                if total_collected >= max_properties:
                    break
                
                self.properties.append(property_info)
                total_collected += 1
                self.logger.info(f"Collected property #{total_collected}: {property_info['url']}")
            
            page += 1
            time.sleep(1)  # Rate limiting
        
        self.logger.info(f"Property data collection completed. Total properties: {len(self.properties)}")
        return len(self.properties)
    
    def extract_sample_phone_numbers(self, sample_size=5):
        """Extract phone numbers from a sample of properties for testing"""
        self.logger.info(f"Testing phone extraction on {sample_size} properties")
        
        for i, property_info in enumerate(self.properties[:sample_size]):
            try:
                property_url = property_info['url']
                self.logger.info(f"Testing property {i+1}: {property_url}")
                
                # Try to get the property page content
                html_content = self.fetcher.fetch_page(property_url)
                
                if html_content:
                    # Save the HTML for manual inspection
                    filename = f"property_sample_{i+1}.html"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    
                    self.logger.info(f"Saved property HTML to {filename}")
                    
                    # Try to extract phone numbers from the HTML
                    import re
                    
                    # Look for Georgian phone numbers (5XXXXXXXX)
                    phone_patterns = [
                        r'\b5\d{8}\b',  # 5XXXXXXXX format
                        r'\b\+995\s*5\d{8}\b',  # +995 5XXXXXXXX format
                        r'\b995\s*5\d{8}\b',  # 995 5XXXXXXXX format
                        r'\b5\d{2}[\s-]?\d{3}[\s-]?\d{3}\b'  # 5XX XXX XXX format
                    ]
                    
                    found_phones = set()
                    for pattern in phone_patterns:
                        matches = re.findall(pattern, html_content)
                        for match in matches:
                            # Clean the phone number
                            clean_phone = re.sub(r'[^\d]', '', match)
                            if len(clean_phone) >= 9 and clean_phone.startswith('5'):
                                found_phones.add(clean_phone)
                    
                    if found_phones:
                        self.logger.info(f"Found {len(found_phones)} phone numbers: {list(found_phones)}")
                        self.owner_phones.update(found_phones)
                    else:
                        self.logger.info(f"No phone numbers found in HTML")
                
                time.sleep(2)  # Rate limiting
                
            except Exception as e:
                self.logger.error(f"Error processing property {property_url}: {e}")
        
        self.logger.info(f"Phone extraction test completed. Total unique phones: {len(self.owner_phones)}")
    
    def save_property_data(self, filename="properties_data.json"):
        """Save collected property data to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.properties, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved {len(self.properties)} properties to {filename}")
            
        except Exception as e:
            self.logger.error(f"Error saving property data: {e}")
    
    def export_phones_to_csv(self, filename="owners_simple.csv"):
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
            'properties_collected': len(self.properties),
            'phones_found': len(self.owner_phones)
        }
    
    def close(self):
        """Close all connections"""
        if self.fetcher:
            self.fetcher.close()

def main():
    """Main function to run the simple owners scraper"""
    scraper = None
    try:
        print("🏠 Simple MyHome.ge Property Data Collector")
        print("=" * 50)
        
        # Initialize scraper
        scraper = SimpleOwnersPhoneScraper()
        
        # Collect property data
        property_count = scraper.collect_property_data(max_pages=5, max_properties=50)
        
        # Save property data
        scraper.save_property_data("properties_data.json")
        
        # Test phone extraction on a sample
        scraper.extract_sample_phone_numbers(sample_size=5)
        
        # Export any found phones
        if len(scraper.owner_phones) > 0:
            scraper.export_phones_to_csv("owners_simple.csv")
        
        # Print final statistics
        stats = scraper.get_stats()
        print(f"\n✅ Data collection completed!")
        print(f"🏢 Total properties collected: {stats['properties_collected']}")
        print(f"📱 Total phone numbers found: {stats['phones_found']}")
        print(f"📄 Property data saved to: properties_data.json")
        
        if stats['phones_found'] > 0:
            print(f"📄 Phone numbers saved to: owners_simple.csv")
        
    except KeyboardInterrupt:
        print("\n⚠️ Data collection interrupted by user")
    except Exception as e:
        print(f"❌ Error during data collection: {e}")
        logging.error(f"Fatal error: {e}")
    finally:
        if scraper:
            scraper.close()

if __name__ == "__main__":
    main()
