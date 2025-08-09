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
    
    # Sample property URL
    test_url = "https://www.myhome.ge/pr/22013265/qiravdeba-2-otaxiani-bina-did-dighomshi/"
    
    fetcher = MyHomeFetcher()
    
    logger.info(f"Fetching property page: {test_url}")
    
    html_content = fetcher.fetch_page(test_url)
    if not html_content:
        logger.error("Failed to fetch property page")
        return
    
    logger.info(f"Page content length: {len(html_content)}")
    
    # Look for all UUIDs in the content
    uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
    matches = re.findall(uuid_pattern, html_content, re.IGNORECASE)
    
    logger.info(f"Found {len(matches)} UUIDs in the page:")
    for i, uuid in enumerate(matches):
        logger.info(f"  {i+1}. {uuid}")
    
    # Look for specific patterns that might be statement UUIDs
    logger.info("\nSearching for statement-related content:")
    
    # Look for "statement" context
    statement_lines = [line for line in html_content.split('\n') if 'statement' in line.lower()]
    for line in statement_lines[:5]:  # Show first 5 lines
        logger.info(f"  Statement line: {line.strip()}")
    
    # Look for "uuid" context
    uuid_lines = [line for line in html_content.split('\n') if 'uuid' in line.lower()]
    for line in uuid_lines[:5]:  # Show first 5 lines
        logger.info(f"  UUID line: {line.strip()}")
    
    # Look for "phone" context
    phone_lines = [line for line in html_content.split('\n') if 'phone' in line.lower()]
    for line in phone_lines[:5]:  # Show first 5 lines
        logger.info(f"  Phone line: {line.strip()}")

if __name__ == "__main__":
    debug_uuid_extraction()
