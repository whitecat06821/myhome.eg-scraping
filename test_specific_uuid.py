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

def test_specific_uuids():
    """Test the specific UUIDs provided by the user"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Test the specific UUIDs from user's examples
    test_uuids = [
        "8bba42bb-1077-42bc-af89-d242b70a632a",
        "684cd038-c146-4966-907e-34de317d7845", 
        "345528b7-a30c-4e88-a172-3cbda9bf459e"
    ]
    
    fetcher = MyHomeFetcher()
    parser = MyHomeParser()
    
    for uuid in test_uuids:
        try:
            logger.info(f"Testing UUID: {uuid}")
            
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
                
        except Exception as e:
            logger.error(f"❌ Error processing UUID {uuid}: {e}")
    
    fetcher.close()

if __name__ == "__main__":
    test_specific_uuids()
