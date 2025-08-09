#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import re
from scraper.fetcher import MyHomeFetcher

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

def debug_uuid_extraction():
    """Debug UUID extraction from property pages"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Test URLs from user's examples
    test_urls = [
        "https://www.myhome.ge/pr/22015430/qiravdeba-2-otaxiani-bina-nadzaladevshi/",
        "https://www.myhome.ge/pr/22015386/qiravdeba-2-otaxiani-bina-vakeshi/",
        "https://www.myhome.ge/pr/22015437/qiravdeba-2-otaxiani-bina-saburtaloze/"
    ]
    
    fetcher = MyHomeFetcher()
    
    for url in test_urls:
        try:
            logger.info(f"\n{'='*50}")
            logger.info(f"Testing URL: {url}")
            
            html_content = fetcher.fetch_page(url)
            if not html_content:
                logger.error(f"Failed to fetch page: {url}")
                continue
            
            logger.info(f"Page content length: {len(html_content)} characters")
            
            # Find all UUIDs in the content
            uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
            matches = re.findall(uuid_pattern, html_content, re.IGNORECASE)
            
            logger.info(f"Found {len(matches)} UUIDs in the page:")
            for i, uuid in enumerate(matches):
                logger.info(f"  {i+1}. {uuid}")
            
            # Look for statement-related content
            statement_lines = [line for line in html_content.split('\n') if 'statement' in line.lower()]
            logger.info(f"\nFound {len(statement_lines)} lines containing 'statement':")
            for i, line in enumerate(statement_lines[:10]):  # Show first 10
                logger.info(f"  {i+1}. {line.strip()}")
            
            # Look for phone-related content
            phone_lines = [line for line in html_content.split('\n') if 'phone' in line.lower()]
            logger.info(f"\nFound {len(phone_lines)} lines containing 'phone':")
            for i, line in enumerate(phone_lines[:10]):  # Show first 10
                logger.info(f"  {i+1}. {line.strip()}")
                
        except Exception as e:
            logger.error(f"Error processing {url}: {e}")
    
    fetcher.close()

if __name__ == "__main__":
    debug_uuid_extraction()
