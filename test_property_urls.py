#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
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

def test_property_urls():
    """Test different property listing URLs"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    fetcher = MyHomeFetcher()
    
    # Test different URL variations
    test_urls = [
        "https://www.myhome.ge/pr/",
        "https://www.myhome.ge/pr",
        "https://www.myhome.ge/pr/?page=1",
        "https://www.myhome.ge/pr?page=1",
        "https://www.myhome.ge/pr/rent/",
        "https://www.myhome.ge/pr/sale/",
        "https://www.myhome.ge/pr/rent/?page=1",
        "https://www.myhome.ge/pr/sale/?page=1"
    ]
    
    for url in test_urls:
        try:
            logger.info(f"Testing URL: {url}")
            html_content = fetcher.fetch_page(url)
            
            if html_content:
                logger.info(f"✅ Success! Content length: {len(html_content)}")
                # Check if it contains property links
                if '/pr/' in html_content:
                    logger.info(f"✅ Contains property links")
                else:
                    logger.info(f"❌ No property links found")
            else:
                logger.error(f"❌ Failed to fetch")
                
        except Exception as e:
            logger.error(f"❌ Error: {e}")
    
    fetcher.close()

if __name__ == "__main__":
    test_property_urls()
