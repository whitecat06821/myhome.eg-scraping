#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Owner Phone Scraper for MyHome.ge
Discovers property URLs through the complete agent hierarchy for maximum coverage
"""

import csv
import logging
import time
import re
from typing import Set, List, Dict, Optional
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from scraper.fetcher import MyHomeFetcher
from scraper.parser import MyHomeParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper_mega.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MegaOwnerScraper:
    """Enhanced scraper that discovers properties through the complete agent hierarchy"""
    
    def __init__(self):
        self.fetcher = MyHomeFetcher()
        self.parser = MyHomeParser()
        self.discovered_agent_ids = set()
        self.discovered_property_urls = set()
        self.owner_phones = set()
        
    def discover_all_agent_ids(self, max_pages: int = 200) -> Set[str]:
        """
        Discover all agent IDs by scraping the agent list pages
        Returns set of agent IDs
        """
        logger.info(f"🔍 Discovering agent IDs from /maklers/ pages (max {max_pages} pages)")
        agent_ids = set()
        
        for page in range(1, max_pages + 1):
            try:
                url = f"https://www.myhome.ge/maklers/?page={page}"
                logger.info(f"Scraping agent list page {page}: {url}")
                
                response = self.fetcher.fetch_page(url)
                if not response:
                    logger.warning(f"Failed to fetch page {page}")
                    continue
                
                soup = BeautifulSoup(response, 'html.parser')
                
                # Find agent links: href="/maklers/XXXX/" (with or without trailing slash)
                agent_links = soup.find_all('a', href=re.compile(r'/maklers/\d+/?'))
                
                page_agent_count = 0
                for link in agent_links:
                    href = link.get('href')
                    # Extract agent ID from /maklers/4756/
                    match = re.search(r'/maklers/(\d+)/?$', href)
                    if match:
                        agent_id = match.group(1)
                        agent_ids.add(agent_id)
                        page_agent_count += 1
                
                logger.info(f"Found {page_agent_count} agents on page {page}. Total: {len(agent_ids)}")
                
                # If no agents found on this page, we might have reached the end
                if page_agent_count == 0:
                    logger.info(f"No agents found on page {page}. Stopping discovery.")
                    break
                    
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error scraping agent list page {page}: {e}")
                continue
        
        logger.info(f"✅ Discovered {len(agent_ids)} unique agent IDs")
        return agent_ids
    
    def get_agent_sub_agents(self, agent_id: str) -> List[str]:
        """
        Get all sub-agent IDs for a given agent
        Returns list of broker IDs that can be used in /s/?brokers=X
        """
        try:
            # First try the API
            api_data = self.fetcher.fetch_agent_sub_agents_api(agent_id)
            if api_data and api_data.get('result'):
                sub_agents = self.parser.parse_sub_agents_api_response(api_data)
                return [agent['id'] for agent in sub_agents if 'id' in agent]
        except Exception as e:
            logger.debug(f"API failed for agent {agent_id}: {e}")
        
        # Fallback to HTML scraping
        try:
            url = f"https://www.myhome.ge/maklers/{agent_id}/"
            response = self.fetcher.fetch_page(url)
            if not response:
                return []
            
            soup = BeautifulSoup(response, 'html.parser')
            
            # Look for broker links in agent detail page
            broker_ids = []
            
            # Find links to broker listings: /s/?brokers=XXXXXX
            broker_links = soup.find_all('a', href=re.compile(r'/s/\?brokers=\d+'))
            for link in broker_links:
                href = link.get('href')
                match = re.search(r'brokers=(\d+)', href)
                if match:
                    broker_id = match.group(1)
                    broker_ids.append(broker_id)
            
            # Also look for tel: links to get direct broker IDs
            tel_links = soup.find_all('a', href=re.compile(r'tel:'))
            for tel_link in tel_links:
                # Look for nearby broker ID patterns
                parent = tel_link.find_parent()
                if parent:
                    text = parent.get_text()
                    broker_matches = re.findall(r'\b\d{7,}\b', text)
                    broker_ids.extend(broker_matches)
            
            return list(set(broker_ids))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error getting sub-agents for agent {agent_id}: {e}")
            return []
    
    def get_property_urls_from_broker(self, broker_id: str, max_pages: int = 50) -> Set[str]:
        """
        Get all property URLs from a broker's listings
        """
        property_urls = set()
        
        for page in range(1, max_pages + 1):
            try:
                url = f"https://www.myhome.ge/s/?brokers={broker_id}&page={page}"
                response = self.fetcher.fetch_page(url)
                if not response:
                    break
                
                soup = BeautifulSoup(response, 'html.parser')
                
                # Find property links: href="/pr/XXXXXXXX/..."
                property_links = soup.find_all('a', href=re.compile(r'/pr/\d+/'))
                
                page_properties = 0
                for link in property_links:
                    href = link.get('href')
                    if href.startswith('/pr/'):
                        full_url = urljoin('https://www.myhome.ge', href)
                        property_urls.add(full_url)
                        page_properties += 1
                
                logger.debug(f"Broker {broker_id} page {page}: {page_properties} properties")
                
                # If no properties found, we've reached the end
                if page_properties == 0:
                    break
                    
                time.sleep(0.3)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error scraping broker {broker_id} page {page}: {e}")
                break
        
        return property_urls
    
    def discover_all_property_urls(self, min_target: int = 50000) -> Set[str]:
        """
        Discover property URLs through the complete agent hierarchy
        """
        logger.info(f"🚀 Starting mega property URL discovery (target: {min_target})")
        
        # Step 1: Discover all agent IDs
        agent_ids = self.discover_all_agent_ids()
        
        # Step 2: For each agent, get their sub-agents and property URLs
        property_urls = set()
        
        for i, agent_id in enumerate(agent_ids, 1):
            try:
                logger.info(f"Processing agent {i}/{len(agent_ids)}: {agent_id}")
                
                # Get broker IDs for this agent (main + sub-agents)
                broker_ids = self.get_agent_sub_agents(agent_id)
                broker_ids.append(agent_id)  # Include the main agent
                broker_ids = list(set(broker_ids))  # Remove duplicates
                
                logger.info(f"Agent {agent_id} has {len(broker_ids)} brokers: {broker_ids}")
                
                # Get property URLs from each broker
                for broker_id in broker_ids:
                    broker_properties = self.get_property_urls_from_broker(broker_id)
                    property_urls.update(broker_properties)
                    
                    logger.info(f"Broker {broker_id}: {len(broker_properties)} properties. Total: {len(property_urls)}")
                    
                    # Check if we've reached our target
                    if len(property_urls) >= min_target:
                        logger.info(f"✅ Reached target of {min_target} property URLs!")
                        return property_urls
                
                # Progress update
                if i % 10 == 0:
                    logger.info(f"📊 Progress: {i}/{len(agent_ids)} agents processed. {len(property_urls)} URLs discovered")
                    
            except Exception as e:
                logger.error(f"Error processing agent {agent_id}: {e}")
                continue
        
        logger.info(f"✅ Discovery complete: {len(property_urls)} property URLs found")
        return property_urls
    
    def scrape_property_phone(self, property_url: str) -> Optional[str]:
        """
        Scrape phone number from a property page
        """
        try:
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
    
    def export_to_csv(self, filename: str = 'owners_mega.csv'):
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
    
    def scrape_owners_mega(self, min_target: int = 1000):
        """
        Main method to scrape owner phone numbers using mega discovery
        """
        logger.info(f"🎯 Starting MEGA owner phone scraping (target: {min_target})")
        
        # Step 1: Discover all property URLs
        property_urls = self.discover_all_property_urls(min_target * 10)  # Get more URLs than needed
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
        
        logger.info(f"🏁 MEGA scraping complete! Found {len(self.owner_phones)} unique owner phone numbers")
        return len(self.owner_phones)

def main():
    """Main execution"""
    scraper = MegaOwnerScraper()
    
    # Target: 1000 owner phone numbers
    result = scraper.scrape_owners_mega(min_target=1000)
    
    if result >= 1000:
        print(f"✅ SUCCESS: Found {result} owner phone numbers!")
    else:
        print(f"⚠️  Found {result} owner phone numbers (target was 1000)")

if __name__ == "__main__":
    main()
