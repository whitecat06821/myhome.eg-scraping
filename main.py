#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import time
import threading
from scraper.fetcher import MyHomeFetcher
from scraper.parser import MyHomeParser
from scraper.selenium_handler import SeleniumHandler
from scraper.data_storage import DataStorage

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('scraper.log'),
            logging.StreamHandler()
        ]
    )

class MyHomeScraper:
    def __init__(self, use_api=True, use_selenium=True):
        self.logger = logging.getLogger(__name__)
        self.fetcher = MyHomeFetcher()
        self.parser = MyHomeParser()
        self.data_storage = DataStorage()
        self.use_api = use_api
        self.use_selenium = use_selenium
        
        if self.use_selenium:
            self.selenium_handler = SeleniumHandler()
            self.selenium_handler.start_driver()
            self.logger.info("Selenium WebDriver started")
    
    def scrape_agents(self, max_pages=109, target_count=900):
        """Scrape agent data from multiple pages using API until target count is reached"""
        self.logger.info(f"Starting agent scraping... Target: {target_count} agents")
        
        page = 1
        total_agents_found = 0
        
        while page <= max_pages and total_agents_found < target_count:
            self.logger.info(f"Scraping agents page {page}")
            
            if self.use_api:
                # Use API to fetch agent data
                api_data = self.fetcher.fetch_agents_api(page=page)
                
                if not api_data:
                    self.logger.error(f"Failed to fetch API data for page {page}")
                    break
                
                # Parse agents from API response
                agents = self.parser.parse_agents_api_response(api_data)
                self.logger.info(f"Found {len(agents)} agents on page {page}")
                
                if not agents:
                    self.logger.info(f"No more agents found on page {page}, stopping")
                    break
                
                # Add main agents to storage and fetch their sub-agents
                for agent in agents:
                    try:
                        # Add main agent
                        self.data_storage.add_agent(agent)
                        total_agents_found += 1
                        self.logger.info(f"Added main agent: {agent['name']} - {agent['phone']}")
                        
                        # Fetch sub-agents for this main agent
                        sub_agents_count = self._scrape_agent_sub_agents(agent['id'])
                        if sub_agents_count > 0:
                            self.logger.info(f"Found {sub_agents_count} sub-agents for {agent['name']}")
                            total_agents_found += sub_agents_count
                        
                        # Rate limiting between agents
                        time.sleep(1)
                        
                        # Check if we've reached the target
                        if total_agents_found >= target_count:
                            self.logger.info(f"Reached target count of {target_count} agents! Stopping...")
                            break
                        
                    except Exception as e:
                        self.logger.error(f"Error processing agent {agent.get('name', 'Unknown')}: {e}")
                
                page += 1
                
            else:
                # Legacy Selenium approach (not recommended)
                if self.use_selenium:
                    url = f"https://www.myhome.ge/maklers/?page={page}" if page > 1 else "https://www.myhome.ge/maklers/"
                    html_content = self.selenium_handler.get_page_with_phone(url)
                    
                    if not html_content:
                        self.logger.error(f"Failed to load page {page}")
                        break
                    
                    # Wait for content to load
                    time.sleep(5)
                    
                    # Get updated HTML after dynamic loading
                    html_content = self.selenium_handler.driver.page_source
                    
                else:
                    # Use regular fetcher (won't work for dynamic content)
                    html_content = self.fetcher.fetch_agents_list(page)
                
                if html_content:
                    # Parse agent links from the page
                    agent_links = self.parser.extract_agent_links_from_list(html_content)
                    self.logger.info(f"Found {len(agent_links)} agent links on page {page}")
                    
                    if not agent_links:
                        self.logger.info(f"No more agents found on page {page}, stopping")
                        break
                    
                    # Scrape each agent detail page
                    for agent_link in agent_links:
                        try:
                            self._scrape_agent_detail(agent_link)
                            total_agents_found += 1
                            
                            # Rate limiting
                            time.sleep(2)
                            
                        except Exception as e:
                            self.logger.error(f"Error scraping agent {agent_link}: {e}")
                    
                    page += 1
                else:
                    self.logger.error(f"Failed to get content for page {page}")
                    break
        
        self.logger.info(f"Agent scraping completed. Total agents processed: {total_agents_found}")
        return total_agents_found
    
    def _scrape_agent_sub_agents(self, agent_id: str) -> int:
        """Scrape sub-agents for a specific main agent"""
        sub_agents_count = 0
        
        try:
            # Fetch sub-agents from API
            api_data = self.fetcher.fetch_agent_sub_agents_api(agent_id, page=1)
            
            if api_data:
                # Parse sub-agents from API response
                sub_agents = self.parser.parse_sub_agents_api_response(api_data)
                
                # Add sub-agents to storage
                for sub_agent in sub_agents:
                    try:
                        self.data_storage.add_agent(sub_agent)
                        sub_agents_count += 1
                        self.logger.info(f"Added sub-agent: {sub_agent['name']} - {sub_agent['phone']}")
                        
                    except Exception as e:
                        self.logger.error(f"Error adding sub-agent {sub_agent.get('name', 'Unknown')}: {e}")
            
        except Exception as e:
            self.logger.error(f"Error scraping sub-agents for agent {agent_id}: {e}")
        
        return sub_agents_count
    
    def _scrape_agent_detail(self, agent_url):
        """Scrape individual agent detail page (legacy method)"""
        self.logger.info(f"Scraping agent detail: {agent_url}")
        
        if self.use_selenium:
            html_content = self.selenium_handler.get_page_with_phone(agent_url)
        else:
            html_content = self.fetcher.fetch_agent_detail(agent_url)
        
        if html_content:
            # Parse agent data
            agent_data = self.parser.parse_agent_detail(html_content, agent_url)
            
            if agent_data and agent_data.get('name') and agent_data.get('phone'):
                self.data_storage.add_agent(
                    name=agent_data['name'],
                    phone=agent_data['phone'],
                    url=agent_url
                )
                self.logger.info(f"Added agent: {agent_data['name']} - {agent_data['phone']}")
            else:
                self.logger.warning(f"No valid agent data found for {agent_url}")
        else:
            self.logger.error(f"Failed to load agent detail page: {agent_url}")
    
    def scrape_properties(self, max_pages=50, target_count=900):
        """Scrape property owner phone numbers using API approach"""
        self.logger.info(f"Starting property owner scraping... Target: {target_count} owners")
        
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
                    
                    phone = None
                    
                    # Try Selenium approach first since API is not working
                    if self.use_selenium:
                        self.logger.info(f"Using Selenium for {property_url}")
                        phone = self.selenium_handler.get_property_phone_with_selenium(property_url)
                    
                    # Fallback to API approach (currently not working)
                    if not phone:
                        statement_uuid = self.parser.extract_statement_uuid_from_url(property_url, self.fetcher)
                        if statement_uuid:
                            api_data = self.fetcher.fetch_property_phone_api(statement_uuid)
                            if api_data:
                                phone = self.parser.parse_property_phone_api_response(api_data)
                    
                    if phone:
                        self.data_storage.add_owner_phone(phone)
                        total_owners_found += 1
                        self.logger.info(f"Added owner phone: {phone}")
                    else:
                        self.logger.debug(f"No valid phone number found for {property_url}")
                    
                    # Rate limiting
                    time.sleep(1)
                    
                except Exception as e:
                    self.logger.error(f"Error scraping property {property_url}: {e}")
            
            page += 1
        
        self.logger.info(f"Property owner scraping completed. Total owners processed: {total_owners_found}")
        return total_owners_found
    
    def run_agents_scraping(self):
        """Run agents scraping in a separate thread"""
        try:
            agents_count = self.scrape_agents(max_pages=109, target_count=900)
            self.logger.info(f"Agents scraping completed: {agents_count} agents found")
        except Exception as e:
            self.logger.error(f"Error in agents scraping: {e}")
    
    def run_owners_scraping(self):
        """Run owners scraping in a separate thread"""
        try:
            owners_count = self.scrape_properties(max_pages=50, target_count=900)
            self.logger.info(f"Owners scraping completed: {owners_count} owners found")
        except Exception as e:
            self.logger.error(f"Error in owners scraping: {e}")
    
    def run(self):
        """Run both agents and owners scraping simultaneously"""
        try:
            self.logger.info("Starting MyHome.ge scraper (agents + owners)...")
            
            # Create threads for simultaneous scraping
            agents_thread = threading.Thread(target=self.run_agents_scraping)
            owners_thread = threading.Thread(target=self.run_owners_scraping)
            
            # Start both threads
            agents_thread.start()
            owners_thread.start()
            
            # Wait for both threads to complete
            agents_thread.join()
            owners_thread.join()
            
            # Export data
            self.data_storage.export_to_csv()
            
            # Print statistics
            stats = self.data_storage.get_stats()
            self.logger.info(f"Scraping completed!")
            self.logger.info(f"Agents found: {stats['agents_count']}")
            self.logger.info(f"Owners found: {stats['owners_count']}")
            
        except Exception as e:
            self.logger.error(f"Error during scraping: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        if self.use_selenium and self.selenium_handler:
            self.selenium_handler.close()
        if self.fetcher:
            self.fetcher.close()
        self.logger.info("Cleanup completed")

def main():
    """Main entry point"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Create scraper with API enabled for agents, Selenium for owners
        scraper = MyHomeScraper(use_api=True, use_selenium=True)
        
        # Run the scraper (both agents and owners simultaneously)
        scraper.run()
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")

if __name__ == "__main__":
    main()
