#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from scraper.selenium_handler import SeleniumHandler
from scraper.data_storage import DataStorage

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

def test_owners_selenium():
    """Test the owners Selenium scraping with sample URLs"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Sample property URLs from user
    test_urls = [
        "https://www.myhome.ge/pr/22013265/qiravdeba-2-otaxiani-bina-did-dighomshi/",
        "https://www.myhome.ge/pr/22015430/qiravdeba-2-otaxiani-bina-nadzaladevshi/"
    ]
    
    selenium_handler = SeleniumHandler()
    data_storage = DataStorage()
    
    try:
        selenium_handler.start_driver()
        logger.info("Selenium WebDriver started")
        
        for url in test_urls:
            try:
                logger.info(f"Testing URL: {url}")
                
                phone = selenium_handler.get_property_phone_with_selenium(url)
                
                if phone:
                    data_storage.add_owner_phone(phone)
                    logger.info(f"✅ Successfully added phone: {phone}")
                else:
                    logger.warning(f"❌ No phone number found")
                    
            except Exception as e:
                logger.error(f"❌ Error processing {url}: {e}")
        
        # Export results
        data_storage.export_to_csv()
        stats = data_storage.get_stats()
        logger.info(f"Test completed! Owners found: {stats['owners_count']}")
        
    finally:
        selenium_handler.close()

if __name__ == "__main__":
    test_owners_selenium()
