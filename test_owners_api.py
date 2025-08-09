#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from scraper.fetcher import MyHomeFetcher
from scraper.parser import MyHomeParser
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

def test_owners_api():
    """Test the owners API scraping with sample URLs"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Sample property URLs from user
    test_urls = [
        "https://www.myhome.ge/pr/22013265/qiravdeba-2-otaxiani-bina-did-dighomshi/",
        "https://www.myhome.ge/pr/22015430/qiravdeba-2-otaxiani-bina-nadzaladevshi/",
        "https://www.myhome.ge/pr/22015386/qiravdeba-2-otaxiani-bina-vakeshi/",
        "https://www.myhome.ge/pr/22015437/qiravdeba-2-otaxiani-bina-saburtaloze/"
    ]
    
    fetcher = MyHomeFetcher()
    parser = MyHomeParser()
    data_storage = DataStorage()
    
    logger.info("Testing owners API scraping...")
    
    for url in test_urls:
        try:
            logger.info(f"Testing URL: {url}")
            
            # Extract statement UUID from property URL
            statement_uuid = parser.extract_statement_uuid_from_url(url, fetcher)
            logger.info(f"Extracted UUID: {statement_uuid}")
            
            if statement_uuid:
                # Fetch phone number using API
                api_data = fetcher.fetch_property_phone_api(statement_uuid)
                
                if api_data:
                    logger.info(f"API Response: {api_data}")
                    phone = parser.parse_property_phone_api_response(api_data)
                    
                    if phone:
                        data_storage.add_owner_phone(phone)
                        logger.info(f"✅ Successfully added phone: {phone}")
                    else:
                        logger.warning(f"❌ No valid phone number found")
                else:
                    logger.error(f"❌ Failed to fetch phone API")
            else:
                logger.error(f"❌ Could not extract statement UUID")
                
        except Exception as e:
            logger.error(f"❌ Error processing {url}: {e}")
    
    # Export results
    data_storage.export_to_csv()
    stats = data_storage.get_stats()
    logger.info(f"Test completed! Owners found: {stats['owners_count']}")

if __name__ == "__main__":
    test_owners_api()
