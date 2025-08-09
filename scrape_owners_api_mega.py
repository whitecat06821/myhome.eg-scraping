#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API-Based Mega Owner Phone Scraper for MyHome.ge
Uses the website's internal APIs to discover maximum property URLs
"""

import csv
import logging
import time
import re
from typing import Set, List, Dict, Optional
from urllib.parse import urljoin, urlparse
import requests
from scraper.fetcher import MyHomeFetcher
from scraper.parser import MyHomeParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper_api_mega.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ApiMegaOwnerScraper:
    """API-based scraper that discovers properties through agents API for maximum coverage"""
    
    def __init__(self):
        self.fetcher = MyHomeFetcher()
        self.parser = MyHomeParser()
        self.discovered_broker_ids = set()
        self.discovered_property_urls = set()
        self.owner_phones = set()
        
    def discover_all_brokers_from_api(self, max_pages: int = 100) -> Set[str]:
        """
        Discover all broker IDs using the agents API
        Returns set of broker IDs
        """
        logger.info(f"🔍 Discovering broker IDs from agents API (max {max_pages} pages)")
        broker_ids = set()
        
        for page in range(1, max_pages + 1):
            try:
                logger.info(f"Fetching agents API page {page}")
                
                # Use the agents API
                api_data = self.fetcher.fetch_agents_api(page)
                if not api_data or not api_data.get('result'):
                    logger.warning(f"No data from agents API page {page}")
                    break
                
                # Parse agents from API response
                agents = self.parser.parse_agents_api_response(api_data)
                
                page_broker_count = 0
                for agent in agents:
                    if 'id' in agent:
                        broker_ids.add(str(agent['id']))
                        page_broker_count += 1
                    
                    # Also get sub-agents for this agent
                    if 'id' in agent:
                        try:
                            sub_agents_data = self.fetcher.fetch_agent_sub_agents_api(str(agent['id']))
                            if sub_agents_data and sub_agents_data.get('result'):
                                sub_agents = self.parser.parse_sub_agents_api_response(sub_agents_data)
                                for sub_agent in sub_agents:
                                    if 'id' in sub_agent:
                                        broker_ids.add(str(sub_agent['id']))
                                        page_broker_count += 1
                        except Exception as e:
                            logger.debug(f"Failed to get sub-agents for {agent['id']}: {e}")
                
                logger.info(f"Found {page_broker_count} brokers on page {page}. Total: {len(broker_ids)}")
                
                # If no agents found on this page, we might have reached the end
                if len(agents) == 0:
                    logger.info(f"No agents found on page {page}. Stopping discovery.")
                    break
                    
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error fetching agents API page {page}: {e}")
                continue
        
        logger.info(f"✅ Discovered {len(broker_ids)} unique broker IDs")
        return broker_ids
    
    def discover_properties_from_multiple_apis(self, max_pages_per_api: int = 200) -> Set[str]:
        """
        Discover property URLs from multiple API endpoints
        """
        logger.info(f"🔍 Discovering properties from multiple API sources")
        property_urls = set()
        
        # API endpoints to try
        api_endpoints = [
            "/statements",  # All statements
            "/statements?operation_type_id=1",  # Sale
            "/statements?operation_type_id=3",  # Rent
        ]
        
        for endpoint in api_endpoints:
            logger.info(f"📡 Fetching from API endpoint: {endpoint}")
            
            for page in range(1, max_pages_per_api + 1):
                try:
                    api_data = self.fetcher.fetch_property_listings_api(page, endpoint)
                    if not api_data or not api_data.get('result'):
                        logger.debug(f"No data from {endpoint} page {page}")
                        break
                    
                    properties = self.parser.parse_property_listings_api_response(api_data)
                    
                    page_properties = 0
                    for prop in properties:
                        if 'statement_id' in prop:
                            # Generate property URL
                            property_url = f"https://www.myhome.ge/pr/{prop['statement_id']}/"
                            property_urls.add(property_url)
                            page_properties += 1
                    
                    logger.info(f"{endpoint} page {page}: {page_properties} properties. Total: {len(property_urls)}")
                    
                    # If no properties found, we've reached the end
                    if page_properties == 0:
                        break
                        
                    time.sleep(0.3)  # Rate limiting
                    
                except Exception as e:
                    logger.error(f"Error fetching {endpoint} page {page}: {e}")
                    break
        
        return property_urls
    
    def discover_properties_from_broker_listings(self, broker_ids: Set[str], max_properties: int = 50000) -> Set[str]:
        """
        Discover property URLs from broker-specific listings
        """
        logger.info(f"🔍 Discovering properties from {len(broker_ids)} broker listings")
        property_urls = set()
        
        for i, broker_id in enumerate(broker_ids, 1):
            try:
                # Use multiple endpoints for each broker
                broker_endpoints = [
                    f"/statements?broker_id={broker_id}",
                    f"/statements?broker_id={broker_id}&operation_type_id=1",  # Sale
                    f"/statements?broker_id={broker_id}&operation_type_id=3",  # Rent
                ]
                
                for endpoint in broker_endpoints:
                    for page in range(1, 10):  # Max 10 pages per broker per endpoint
                        try:
                            api_data = self.fetcher.fetch_property_listings_api(page, endpoint)
                            if not api_data or not api_data.get('result'):
                                break
                            
                            properties = self.parser.parse_property_listings_api_response(api_data)
                            
                            for prop in properties:
                                if 'statement_id' in prop:
                                    property_url = f"https://www.myhome.ge/pr/{prop['statement_id']}/"
                                    property_urls.add(property_url)
                            
                            if len(properties) == 0:
                                break
                                
                        except Exception as e:
                            logger.debug(f"Error fetching broker {broker_id} {endpoint} page {page}: {e}")
                            break
                
                if i % 50 == 0:
                    logger.info(f"📊 Progress: {i}/{len(broker_ids)} brokers processed. {len(property_urls)} URLs discovered")
                
                # Check if we've reached our target
                if len(property_urls) >= max_properties:
                    logger.info(f"✅ Reached target of {max_properties} property URLs!")
                    break
                    
            except Exception as e:
                logger.error(f"Error processing broker {broker_id}: {e}")
                continue
        
        return property_urls
    
    def discover_all_property_urls_mega(self, min_target: int = 50000) -> Set[str]:
        """
        Mega property URL discovery using all available API methods
        """
        logger.info(f"🚀 Starting MEGA API property URL discovery (target: {min_target})")
        
        all_property_urls = set()
        
        # Method 1: Direct property listings APIs
        logger.info("📡 Method 1: Direct property listings APIs")
        direct_properties = self.discover_properties_from_multiple_apis()
        all_property_urls.update(direct_properties)
        logger.info(f"Method 1 result: {len(direct_properties)} URLs. Total: {len(all_property_urls)}")
        
        # Check if we've reached the target
        if len(all_property_urls) >= min_target:
            logger.info(f"✅ Reached target with Method 1!")
            return all_property_urls
        
        # Method 2: Broker-specific listings
        logger.info("👥 Method 2: Broker-specific listings")
        broker_ids = self.discover_all_brokers_from_api()
        broker_properties = self.discover_properties_from_broker_listings(broker_ids, min_target - len(all_property_urls))
        all_property_urls.update(broker_properties)
        logger.info(f"Method 2 result: {len(broker_properties)} URLs. Total: {len(all_property_urls)}")
        
        logger.info(f"✅ MEGA Discovery complete: {len(all_property_urls)} property URLs found")
        return all_property_urls
    
    def scrape_property_phone(self, property_url: str) -> Optional[str]:
        """
        Scrape phone number from a property page using API or HTML
        """
        try:
            # Extract statement UUID/ID from URL
            match = re.search(r'/pr/(\d+)/', property_url)
            if not match:
                return None
            
            statement_id = match.group(1)
            
            # First try to extract UUID from the page for API call
            try:
                uuid = self.parser.extract_statement_uuid_from_url(property_url, self.fetcher)
                if uuid:
                    api_data = self.fetcher.fetch_property_phone_api(uuid)
                    if api_data:
                        phone_data = self.parser.parse_property_phone_api_response(api_data)
                        if phone_data and 'phone' in phone_data:
                            return phone_data['phone']
            except Exception as e:
                logger.debug(f"API method failed for {property_url}: {e}")
            
            # Fallback to HTML scraping
            response = self.fetcher.fetch_page(property_url)
            if not response:
                return None
            
            # Look for phone numbers in the HTML
            phone_patterns = [
                r'\+995\s*\d{3}\s*\d{3}\s*\d{3}',
                r'\+995\d{9}',
                r'995\d{9}',
                r'\b5\d{8}\b',
                r'\b[0-9]{9}\b'
            ]
            
            for pattern in phone_patterns:
                matches = re.findall(pattern, response)
                for match in matches:
                    # Clean and validate phone
                    clean_phone = re.sub(r'[^\d+]', '', match)
                    if len(clean_phone) >= 9:
                        return clean_phone
            
            return None
            
        except Exception as e:
            logger.error(f"Error scraping phone from {property_url}: {e}")
            return None
    
    def export_to_csv(self, filename: str = 'owners_api_mega.csv'):
        """Export phone numbers to CSV with proper Excel formatting"""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Phone'])  # Header
                
                sorted_phones = sorted(self.owner_phones)
                for phone in sorted_phones:
                    # Format with spaces for Excel: +995 571 233 844
                    if not phone.startswith('+995'):
                        formatted_phone = f"+995{phone}"
                    else:
                        formatted_phone = phone
                    
                    # Add spaces
                    if len(formatted_phone) >= 13:
                        spaced_phone = f"{formatted_phone[:4]} {formatted_phone[4:7]} {formatted_phone[7:10]} {formatted_phone[10:]}"
                    else:
                        spaced_phone = formatted_phone
                    
                    writer.writerow([spaced_phone])
            
            logger.info(f"✅ Exported {len(self.owner_phones)} phone numbers to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting to {filename}: {e}")
            return False
    
    def scrape_owners_api_mega(self, min_target: int = 1000):
        """
        Main method to scrape owner phone numbers using mega API discovery
        """
        logger.info(f"🎯 Starting API MEGA owner phone scraping (target: {min_target})")
        
        # Step 1: Discover all property URLs using API
        property_urls = self.discover_all_property_urls_mega(min_target * 20)  # Get more URLs than needed
        logger.info(f"📋 Will scrape phones from {len(property_urls)} properties")
        
        # Step 2: Scrape phones from properties
        scraped_count = 0
        for i, property_url in enumerate(property_urls, 1):
            try:
                phone = self.scrape_property_phone(property_url)
                if phone:
                    self.owner_phones.add(phone)
                    scraped_count += 1
                    logger.info(f"✅ Found phone in property {i}: {phone}. Total: {len(self.owner_phones)}")
                    
                    # Save progress every 50 phones
                    if len(self.owner_phones) % 50 == 0:
                        self.export_to_csv()
                    
                    # Check if we've reached our target
                    if len(self.owner_phones) >= min_target:
                        logger.info(f"🎉 SUCCESS! Reached target of {min_target} owner phones!")
                        break
                
                # Progress update
                if i % 100 == 0:
                    success_rate = (scraped_count / i * 100) if i > 0 else 0
                    logger.info(f"📊 Progress: {i}/{len(property_urls)} properties. {len(self.owner_phones)} phones ({success_rate:.1f}% success rate)")
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error scraping property {i} ({property_url}): {e}")
                continue
        
        # Final export
        self.export_to_csv()
        
        logger.info(f"🏁 API MEGA scraping complete! Found {len(self.owner_phones)} unique owner phone numbers")
        return len(self.owner_phones)

def main():
    """Main execution"""
    scraper = ApiMegaOwnerScraper()
    
    # Target: 1000 owner phone numbers
    result = scraper.scrape_owners_api_mega(min_target=1000)
    
    if result >= 1000:
        print(f"✅ SUCCESS: Found {result} owner phone numbers!")
    else:
        print(f"⚠️  Found {result} owner phone numbers (target was 1000)")

if __name__ == "__main__":
    main()
