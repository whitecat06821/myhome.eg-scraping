#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from scraper.fetcher import MyHomeFetcher
import re

def setup_logging():
    logging.basicConfig(level=logging.INFO)

def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    
    fetcher = MyHomeFetcher()
    
    try:
        # Fetch the first page
        html = fetcher.fetch_agents_list(1)
        if html:
            # Save HTML to file for analysis
            with open('debug_agents_page.html', 'w', encoding='utf-8') as f:
                f.write(html)
            logger.info(f"Saved HTML to debug_agents_page.html (length: {len(html)})")
            
            # Print first 2000 characters to see structure
            print("First 2000 characters of HTML:")
            print(html[:2000])
            print("\n" + "="*50 + "\n")
            
            # Look for any links containing 'maklers'
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            makler_links = soup.find_all('a', href=re.compile(r'maklers'))
            print(f"Found {len(makler_links)} links containing 'maklers'")
            for i, link in enumerate(makler_links[:5]):  # Show first 5
                print(f"Link {i+1}: {link.get('href')} - Text: {link.get_text()[:50]}")
                
        else:
            logger.error("Failed to fetch HTML")
            
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        fetcher.close()

if __name__ == "__main__":
    main()
