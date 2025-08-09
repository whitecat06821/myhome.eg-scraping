#!/usr/bin/env python3
"""
MyHome.ge Real Estate Agents Phone Number Scraper
Dedicated script for scraping real estate agent phone numbers using API.
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
from excel_utils import save_phones_to_excel_compatible_csv, save_phones_to_excel_file

class AgentsPhoneScraper:
    """Dedicated scraper for real estate agent phone numbers"""
    
    def __init__(self):
        """Initialize the agents scraper"""
        # Setup logging first
        self.setup_logging()
        
        self.fetcher = MyHomeFetcher()
        self.parser = MyHomeParser()
        
        # Set to store unique phone numbers
        self.agent_phones = set()
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('agents_scraper.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def scrape_agents(self, max_pages=109, target_count=700, min_target=700):
        """Scrape real estate agent phone numbers"""
        self.logger.info(f"Starting agents scraping (target: {target_count}, minimum: {min_target})")
        
        total_agents_found = 0
        page = 1
        
        while page <= max_pages and total_agents_found < min_target:
            self.logger.info(f"Scraping agents page {page}")
            
            # Fetch agents from API
            api_data = self.fetcher.fetch_agents_api(page)
            
            if not api_data:
                self.logger.error(f"Failed to fetch agents API page {page}")
                break
            
            # Parse agents from API response
            agents = self.parser.parse_agents_api_response(api_data)
            
            if not agents:
                self.logger.info(f"No more agents found on page {page}, stopping")
                break
            
            self.logger.info(f"Found {len(agents)} agents on page {page}")
            
            # Process each agent
            for agent in agents:
                if total_agents_found >= min_target:
                    self.logger.info(f"✅ SUCCESS! Reached minimum target of {min_target} agents! Stopping...")
                    break
                
                try:
                    # Add main agent phone
                    if 'phone_number' in agent and agent['phone_number']:
                        phone = self.clean_phone_number(agent['phone_number'])
                        if phone and phone not in self.agent_phones:
                            self.agent_phones.add(phone)
                            total_agents_found += 1
                            self.logger.info(f"Added agent #{total_agents_found}: {phone}")
                            # Real-time CSV save every 10 new phones
                            if total_agents_found % 10 == 0:
                                self.export_to_csv("agents.csv")
                        elif phone:
                            self.logger.debug(f"Duplicate agent phone: {phone}")
                    
                    # Try to get sub-agents for this agent
                    agent_id = agent.get('id')
                    if agent_id:
                        sub_agents_count = self.scrape_agent_sub_agents(agent_id, target_count - total_agents_found)
                        total_agents_found += sub_agents_count
                    
                    if total_agents_found >= min_target:
                        break
                    
                except Exception as e:
                    self.logger.error(f"Error processing agent {agent}: {e}")
            
            page += 1
        
        self.logger.info(f"Agents scraping completed. Total unique agents: {len(self.agent_phones)}")
        return len(self.agent_phones)
    
    def scrape_agent_sub_agents(self, agent_id: str, remaining_count: int):
        """Scrape sub-agents for a given agent"""
        if remaining_count <= 0:
            return 0
        
        sub_agents_found = 0
        page = 1
        max_sub_pages = 5  # Limit sub-agent pages per agent
        
        while page <= max_sub_pages and sub_agents_found < remaining_count:
            try:
                # Fetch sub-agents from API
                api_data = self.fetcher.fetch_agent_sub_agents_api(agent_id, page)
                
                if not api_data:
                    break
                
                # Parse sub-agents from API response
                sub_agents = self.parser.parse_sub_agents_api_response(api_data)
                
                if not sub_agents:
                    break
                
                self.logger.info(f"Found {len(sub_agents)} sub-agents for agent {agent_id}, page {page}")
                
                # Process each sub-agent
                for sub_agent in sub_agents:
                    if sub_agents_found >= remaining_count:
                        break
                    
                    if 'phone_number' in sub_agent and sub_agent['phone_number']:
                        phone = self.clean_phone_number(sub_agent['phone_number'])
                        if phone and phone not in self.agent_phones:
                            self.agent_phones.add(phone)
                            sub_agents_found += 1
                            self.logger.info(f"Added sub-agent phone: {phone}")
                            # Real-time CSV save for sub-agents too
                            if len(self.agent_phones) % 10 == 0:
                                self.export_to_csv("agents.csv")
                
                page += 1
                time.sleep(0.5)  # Rate limiting for sub-agents
                
            except Exception as e:
                self.logger.error(f"Error fetching sub-agents for agent {agent_id}: {e}")
                break
        
        return sub_agents_found
    
    def clean_phone_number(self, phone: str) -> Optional[str]:
        """Clean and validate phone number"""
        if not phone:
            return None
        
        # Remove non-digit characters
        import re
        clean_phone = re.sub(r'[^\d]', '', str(phone))
        
        # Validate Georgian mobile number format
        if len(clean_phone) == 9 and clean_phone.startswith('5'):
            return clean_phone
        elif len(clean_phone) > 9 and clean_phone.startswith('9955'):
            # Remove country code
            return clean_phone[3:]
        
        return None
    
    def export_to_csv(self, filename="agents.csv"):
        """Export agent phone numbers to Excel-compatible CSV format"""
        try:
            # Save as Excel-compatible CSV
            success = save_phones_to_excel_compatible_csv(self.agent_phones, filename)
            
            # Also try to save as Excel file if possible
            excel_filename = filename.replace('.csv', '.xlsx')
            save_phones_to_excel_file(self.agent_phones, excel_filename)
            
            if success:
                self.logger.info(f"Exported {len(self.agent_phones)} agent phone numbers to {filename}")
            
        except Exception as e:
            self.logger.error(f"Error exporting to CSV: {e}")
    
    def get_stats(self):
        """Get scraping statistics"""
        return {
            'agents_count': len(self.agent_phones)
        }
    
    def close(self):
        """Close all connections"""
        if self.fetcher:
            self.fetcher.close()

def main():
    """Main function to run the agents scraper"""
    scraper = None
    try:
        print("👔 MyHome.ge Real Estate Agents Phone Scraper")
        print("=" * 50)
        
        # Initialize scraper
        scraper = AgentsPhoneScraper()
        
        # Start scraping (minimum: 700 agents, will stop once reached)
        agents_count = scraper.scrape_agents(max_pages=109, target_count=700, min_target=700)
        
        # Export results
        scraper.export_to_csv("agents.csv")
        
        # Print final statistics
        stats = scraper.get_stats()
        print(f"\n✅ Scraping completed!")
        print(f"👔 Total unique agent phone numbers: {stats['agents_count']}")
        print(f"📄 Results saved to: agents.csv")
        
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
