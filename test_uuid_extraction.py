#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from scraper.fetcher import MyHomeFetcher
from scraper.parser import MyHomeParser

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

def test_uuid_extraction():
    """Test UUID extraction from property pages"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Test URLs from user's examples
    test_urls = [
        "https://www.myhome.ge/pr/22015430/qiravdeba-2-otaxiani-bina-nadzaladevshi/",
        "https://www.myhome.ge/pr/22015386/qiravdeba-2-otaxiani-bina-vakeshi/",
        "https://www.myhome.ge/pr/22015437/qiravdeba-2-otaxiani-bina-saburtaloze/"
    ]
    
    fetcher = MyHomeFetcher()
    parser = MyHomeParser()
    
    for url in test_urls:
        try:
            logger.info(f"Testing URL: {url}")
            uuid = parser.extract_statement_uuid_from_url(url, fetcher)
            
            if uuid:
                logger.info(f"✅ Found UUID: {uuid}")
                
                # Test the API call with this UUID
                api_data = fetcher.fetch_property_phone_api(uuid)
                if api_data:
                    logger.info(f"✅ API Response: {api_data}")
                    phone = parser.parse_property_phone_api_response(api_data)
                    if phone:
                        logger.info(f"✅ Phone number: {phone}")
                    else:
                        logger.warning(f"❌ No phone number found in API response")
                else:
                    logger.error(f"❌ API call failed for UUID: {uuid}")
            else:
                logger.error(f"❌ No UUID found for URL: {url}")
                
        except Exception as e:
            logger.error(f"❌ Error processing {url}: {e}")
    
    fetcher.close()

if __name__ == "__main__":
    test_uuid_extraction()
