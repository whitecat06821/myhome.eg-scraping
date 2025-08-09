#!/usr/bin/env python3
"""
Enhanced MyHome.ge Property Owners Phone Number Scraper
Uses multiple sources and strategies to get 700+ phone numbers
"""

import sys
import os
import logging
import time
import csv
import re
import requests
from typing import Set, List, Dict, Any
from urllib.parse import urljoin, urlparse

# Add the scraper module to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.fetcher import MyHomeFetcher
from scraper.parser import MyHomeParser

class EnhancedOwnersPhoneScraper:
    """Enhanced scraper for property owner phone numbers using multiple sources"""
    
    def __init__(self):
        """Initialize the enhanced owners scraper"""
        self.setup_logging()
        
        self.fetcher = MyHomeFetcher()
        self.parser = MyHomeParser()
        
        # Set to store unique phone numbers
        self.owner_phones = set()
        
        # Multiple listing endpoints
        self.listing_endpoints = [
            "/statements?page={page}&operation_type_id=1",  # Sale
            "/statements?page={page}&operation_type_id=2",  # Rent
            "/statements?page={page}&operation_type_id=3",  # Daily rent
        ]
        
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
                logging.FileHandler('owners_enhanced_scraper.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def get_property_urls_from_multiple_sources(self, max_pages_per_endpoint=100, max_total_properties=10000):
        """Get property URLs from multiple endpoints and sources"""
        self.logger.info(f"Getting property URLs from multiple sources (max: {max_total_properties})")
        
        all_property_urls = set()  # Use set to avoid duplicates
        
        # Method 1: Use API endpoints for different operation types
        for endpoint in self.listing_endpoints:
            self.logger.info(f"Fetching from endpoint: {endpoint}")
            
            page = 1
            while page <= max_pages_per_endpoint and len(all_property_urls) < max_total_properties:
                try:
                    # Construct API URL
                    api_url = f"{self.fetcher.base_url}{endpoint.format(page=page)}"
                    
                    response = self.fetcher.session.get(api_url, headers=self.fetcher.headers, timeout=10)
                    
                    if response.status_code == 200:
                        api_data = response.json()
                        properties = self.parser.parse_property_listings_api_response(api_data)
                        
                        if not properties:
                            self.logger.info(f"No more properties found on {endpoint} page {page}")
                            break
                        
                        self.logger.info(f"Found {len(properties)} properties on {endpoint} page {page}")
                        
                        # Add property URLs
                        for property_info in properties:
                            if len(all_property_urls) >= max_total_properties:
                                break
                            all_property_urls.add(property_info['url'])
                        
                        page += 1
                        time.sleep(0.5)  # Rate limiting
                    else:
                        self.logger.error(f"Failed to fetch {endpoint} page {page}: {response.status_code}")
                        break
                        
                except Exception as e:
                    self.logger.error(f"Error fetching {endpoint} page {page}: {e}")
                    break
        
        # Method 2: Also try scraping HTML listing pages directly
        html_listing_urls = [
            "https://www.myhome.ge/pr/rent/?page={page}",
            "https://www.myhome.ge/pr/sale/?page={page}",
        ]
        
        for listing_url_template in html_listing_urls:
            self.logger.info(f"Scraping HTML listings from: {listing_url_template}")
            
            page = 1
            while page <= 50 and len(all_property_urls) < max_total_properties:  # More pages for HTML
                try:
                    listing_url = listing_url_template.format(page=page)
                    
                    response = self.session.get(listing_url, timeout=10)
                    response.raise_for_status()
                    
                    # Extract property links from HTML
                    property_links = self.extract_property_links_from_html(response.text)
                    
                    if not property_links:
                        self.logger.info(f"No property links found on {listing_url}")
                        break
                    
                    self.logger.info(f"Found {len(property_links)} property links on {listing_url}")
                    
                    # Add to our set
                    for link in property_links:
                        if len(all_property_urls) >= max_total_properties:
                            break
                        # Convert relative URLs to absolute
                        full_url = urljoin("https://www.myhome.ge", link)
                        all_property_urls.add(full_url)
                    
                    page += 1
                    time.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    self.logger.error(f"Error scraping HTML listing {listing_url}: {e}")
                    break
        
        property_urls_list = list(all_property_urls)
        self.logger.info(f"Collected {len(property_urls_list)} unique property URLs from all sources")
        return property_urls_list
    
    def extract_property_links_from_html(self, html_content: str) -> List[str]:
        """Extract property links from HTML listing page"""
        from bs4 import BeautifulSoup
        
        property_links = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find property links (adjust selector based on actual HTML structure)
            link_selectors = [
                'a[href*="/pr/"]',  # Links containing /pr/
                'a[href^="/pr/"]',  # Links starting with /pr/
                '.statement-item a',  # Common class names
                '.property-card a',
                '.listing-item a'
            ]
            
            for selector in link_selectors:
                links = soup.select(selector)
                for link in links:
                    href = link.get('href')
                    if href and '/pr/' in href and href not in property_links:
                        property_links.append(href)
            
        except Exception as e:
            self.logger.error(f"Error extracting property links from HTML: {e}")
        
        return property_links
    
    def extract_phone_from_html(self, html_content: str) -> Set[str]:
        """Extract phone numbers from HTML content with improved patterns"""
        phones = set()
        
        if not html_content:
            return phones
        
        # Enhanced Georgian phone number patterns
        phone_patterns = [
            r'\b5\d{8}\b',  # 5XXXXXXXX format
            r'\b\+995\s*5\d{8}\b',  # +995 5XXXXXXXX format  
            r'\b995\s*5\d{8}\b',  # 995 5XXXXXXXX format
            r'\b5\d{2}[\s\-]?\d{3}[\s\-]?\d{3}\b',  # 5XX XXX XXX format
            r'\b5\d{2}[\s\-]?\d{2}[\s\-]?\d{2}[\s\-]?\d{2}\b',  # 5XX XX XX XX format
            r'phone[\"\'\\s]*[:=][\"\'\\s]*[\"\'\\s]*5\d{8}[\"\'\\s]*',  # JSON-like phone fields
            r'[\"\'\\s]5\d{8}[\"\'\\s]',  # Quoted phone numbers
        ]
        
        for pattern in phone_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
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
            
            response = self.session.get(property_url, timeout=15)
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
    
    def scrape_owners(self, max_pages_per_endpoint=100, target_count=700, min_target=700):
        """Scrape property owner phone numbers from multiple sources"""
        self.logger.info(f"Starting enhanced property owners scraping (target: {target_count}, minimum: {min_target})")
        
        # Get property URLs from multiple sources (collect many URLs but stop scraping at target)
        property_urls = self.get_property_urls_from_multiple_sources(
            max_pages_per_endpoint=max_pages_per_endpoint, 
            max_total_properties=10000  # Collect up to 10k URLs to ensure we have enough sources
        )
        
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
                # Real-time CSV save every 10 new phones
                if len(self.owner_phones) % 10 == 0:
                    self.export_to_csv("owners_enhanced.csv")
            
            # Rate limiting - slower to be more respectful
            time.sleep(1.5)
        
        self.logger.info(f"Enhanced scraping completed. Total unique phone numbers: {len(self.owner_phones)}")
        return len(self.owner_phones)
    
    def export_to_csv(self, filename="owners_enhanced.csv"):
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
    """Main function to run the enhanced owners scraper"""
    scraper = None
    try:
        print("🏠 Enhanced MyHome.ge Property Owners Phone Scraper")
        print("=" * 60)
        
        # Initialize scraper
        scraper = EnhancedOwnersPhoneScraper()
        
        # Start scraping (minimum: 700 phone numbers, will stop once reached)
        owners_count = scraper.scrape_owners(max_pages_per_endpoint=100, target_count=700, min_target=700)
        
        # Final export
        if owners_count > 0:
            scraper.export_to_csv("owners_enhanced.csv")
        
        # Print final statistics
        stats = scraper.get_stats()
        print(f"\n✅ Enhanced scraping completed!")
        print(f"📱 Total unique owner phone numbers: {stats['owners_count']}")
        
        if stats['owners_count'] > 0:
            print(f"📄 Results saved to: owners_enhanced.csv")
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
