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

def test_property_listings():
    """Test property listings page extraction"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    fetcher = MyHomeFetcher()
    parser = MyHomeParser()
    
    # Test the property listings page
    url = "https://www.myhome.ge/pr/?page=1"
    logger.info(f"Testing property listings page: {url}")
    
    html_content = fetcher.fetch_property_listings(1)
    if not html_content:
        logger.error("Failed to fetch property listings page")
        return
    
    logger.info(f"Page content length: {len(html_content)} characters")
    
    # Extract property links
    property_links = parser.extract_property_links_from_list(html_content)
    logger.info(f"Found {len(property_links)} property links")
    
    # Show first few links
    for i, link in enumerate(property_links[:5]):
        logger.info(f"  {i+1}. {link}")
    
    # Save a sample of the HTML for debugging
    with open("property_listings_sample.html", "w", encoding="utf-8") as f:
        f.write(html_content[:10000])  # First 10k characters
    logger.info("Saved sample HTML to property_listings_sample.html")
    
    fetcher.close()

if __name__ == "__main__":
    test_property_listings()
