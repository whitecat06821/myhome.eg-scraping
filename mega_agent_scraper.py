#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEGA Agent Phone Scraper
Target: 8,000 unique agent phone numbers
"""

import csv
import logging
import time
import re
from typing import Set, List, Dict, Optional
from scraper.fetcher import MyHomeFetcher
from scraper.parser import MyHomeParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mega_agent_scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MegaAgentScraper:
    """Mega agent scraper targeting 8,000 unique agent phones"""
    
    def __init__(self):
        self.fetcher = MyHomeFetcher()
        self.parser = MyHomeParser()
        self.agent_phones = set()
        self.processed_agents = set()
        self.target_phones = 8000
        
    def load_existing_agent_phones(self):
        """Load existing agent phones to avoid duplicates"""
        try:
            with open('agents.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    phone = row.get('Phone', '').strip()
                    if phone:
                        normalized = self.normalize_phone(phone)
                        if normalized:
                            self.agent_phones.add(normalized)
            logger.info(f"Loaded {len(self.agent_phones)} existing agent phones")
        except Exception as e:
            logger.debug(f"Could not load existing agents: {e}")
    
    def normalize_phone(self, phone: str) -> str:
        """Normalize phone for deduplication"""
        if not phone:
            return ""
        
        digits = re.sub(r'\D', '', phone)
        
        if len(digits) == 9 and digits.startswith('5'):
            return f"+995{digits}"
        elif len(digits) == 12 and digits.startswith('995'):
            return f"+{digits}"
        elif len(digits) >= 9:
            return f"+995{digits[-9:]}"
        
        return ""
    
    def discover_all_agents_mega(self, max_pages: int = 500) -> Set[str]:
        """Discover all agent IDs using the agents API extensively"""
        logger.info(f"🔍 MEGA agent discovery (max {max_pages} pages)")
        agent_ids = set()
        
        for page in range(1, max_pages + 1):
            try:
                logger.info(f"Fetching agents API page {page}")
                
                api_data = self.fetcher.fetch_agents_api(page)
                if not api_data or not api_data.get('result'):
                    logger.warning(f"No data from agents API page {page}")
                    break
                
                agents = self.parser.parse_agents_api_response(api_data)
                
                page_agent_count = 0
                for agent in agents:
                    if 'id' in agent:
                        agent_ids.add(str(agent['id']))
                        page_agent_count += 1
                
                logger.info(f"Page {page}: {page_agent_count} agents. Total: {len(agent_ids)}")
                
                # If no agents found, we've reached the end
                if len(agents) == 0:
                    logger.info(f"No agents found on page {page}. Stopping discovery.")
                    break
                    
                time.sleep(0.3)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error fetching agents API page {page}: {e}")
                continue
        
        logger.info(f"✅ Discovered {len(agent_ids)} unique agent IDs")
        return agent_ids
    
    def scrape_agent_and_sub_agents(self, agent_id: str) -> List[Dict]:
        """Scrape main agent and all sub-agents"""
        all_agents = []
        
        try:
            # Get main agent data
            main_agent_data = self.fetcher.fetch_agents_api(1, f"id:{agent_id}")
            if main_agent_data and main_agent_data.get('result'):
                main_agents = self.parser.parse_agents_api_response(main_agent_data)
                all_agents.extend(main_agents)
            
            # Get sub-agents
            sub_agents_data = self.fetcher.fetch_agent_sub_agents_api(agent_id)
            if sub_agents_data and sub_agents_data.get('result'):
                sub_agents = self.parser.parse_sub_agents_api_response(sub_agents_data)
                all_agents.extend(sub_agents)
                
                logger.debug(f"Agent {agent_id}: {len(sub_agents)} sub-agents")
            
            return all_agents
            
        except Exception as e:
            logger.error(f"Error scraping agent {agent_id}: {e}")
            return []
    
    def extract_phone_from_agent(self, agent: Dict) -> Optional[str]:
        """Extract and normalize phone from agent data"""
        try:
            # Try different phone field names
            phone_fields = ['phone', 'mobile', 'telephone', 'contact', 'phoneNumber']
            
            for field in phone_fields:
                if field in agent and agent[field]:
                    phone = str(agent[field]).strip()
                    normalized = self.normalize_phone(phone)
                    if normalized and normalized not in self.agent_phones:
                        return normalized
            
            return None
            
        except Exception as e:
            logger.debug(f"Error extracting phone from agent: {e}")
            return None
    
    def export_mega_agents_csv(self, filename: str = 'mega_agents.csv'):
        """Export unique agent phones to CSV"""
        try:
            sorted_phones = sorted(self.agent_phones)
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Phone'])
                
                for phone in sorted_phones:
                    # Format for Excel: +995 571 233 844
                    digits = re.sub(r'[^\d]', '', phone)
                    if len(digits) >= 12:
                        formatted = f"+995 {digits[3:6]} {digits[6:9]} {digits[9:12]}"
                    else:
                        formatted = phone
                    writer.writerow([formatted])
            
            logger.info(f"✅ Exported {len(sorted_phones)} agent phones to {filename}")
            return len(sorted_phones)
            
        except Exception as e:
            logger.error(f"Error exporting agent CSV: {e}")
            return 0
    
    def mega_agent_scrape(self):
        """Main mega agent scraping method"""
        logger.info(f"🚀 MEGA AGENT SCRAPER STARTING (target: {self.target_phones})")
        
        # Load existing phones
        self.load_existing_agent_phones()
        
        if len(self.agent_phones) >= self.target_phones:
            logger.info(f"🎉 Target already reached! {len(self.agent_phones)} agent phones")
            return len(self.agent_phones)
        
        # Discover all agent IDs
        agent_ids = self.discover_all_agents_mega()
        logger.info(f"📋 Will process {len(agent_ids)} agents for phones")
        
        # Process each agent and their sub-agents
        processed_count = 0
        new_phones_found = 0
        
        for i, agent_id in enumerate(agent_ids, 1):
            try:
                if agent_id in self.processed_agents:
                    continue
                
                # Get all agents (main + sub-agents)
                all_agents = self.scrape_agent_and_sub_agents(agent_id)
                
                for agent in all_agents:
                    phone = self.extract_phone_from_agent(agent)
                    if phone:
                        old_count = len(self.agent_phones)
                        self.agent_phones.add(phone)
                        if len(self.agent_phones) > old_count:
                            new_phones_found += 1
                            logger.info(f"✅ NEW agent phone {new_phones_found}: {phone}. Total: {len(self.agent_phones)}")
                            
                            # Save progress every 200 new phones
                            if new_phones_found % 200 == 0:
                                self.export_mega_agents_csv()
                
                self.processed_agents.add(agent_id)
                processed_count += 1
                
                # Progress update
                if i % 100 == 0:
                    logger.info(f"📊 Progress: {i}/{len(agent_ids)} agents. {len(self.agent_phones)} unique phones")
                
                # Check if target reached
                if len(self.agent_phones) >= self.target_phones:
                    logger.info(f"🎉 AGENT TARGET REACHED! {len(self.agent_phones)} unique phones!")
                    break
                
                time.sleep(0.2)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error processing agent {agent_id}: {e}")
                continue
        
        # Final export
        final_count = self.export_mega_agents_csv()
        
        logger.info(f"🏁 MEGA AGENT SCRAPING COMPLETE!")
        logger.info(f"   Final unique agent phones: {final_count}")
        logger.info(f"   Target: {self.target_phones}")
        logger.info(f"   Success: {'YES' if final_count >= self.target_phones else 'PARTIAL'}")
        
        return final_count

def main():
    """Main execution"""
    scraper = MegaAgentScraper()
    result = scraper.mega_agent_scrape()
    
    if result >= 8000:
        print(f"🎉 SUCCESS: {result} unique agent phones collected!")
    else:
        print(f"📊 Collected {result} unique agent phones (target was 8000)")

if __name__ == "__main__":
    main()
