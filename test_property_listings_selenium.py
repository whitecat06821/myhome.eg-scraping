#!/usr/bin/env python3
"""
Test script for property listings using Selenium
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.selenium_handler import SeleniumHandler
from scraper.parser import MyHomeParser
import time

def test_property_listings_selenium():
    """Test property listings with Selenium"""
    selenium = SeleniumHandler()
    parser = MyHomeParser()
    
    try:
        print("Loading property listings page with Selenium...")
        
        # Load the property listings page
        url = "https://www.myhome.ge/pr/rent/?page=1"
        selenium.driver.get(url)
        
        # Wait for the page to load
        print("Waiting for page to load...")
        time.sleep(5)
        
        # Get the page source
        page_source = selenium.driver.page_source
        
        # Save the page source for inspection
        with open("property_listings_selenium.html", "w", encoding="utf-8") as f:
            f.write(page_source)
        
        print("✅ Page loaded and saved to property_listings_selenium.html")
        
        # Try to extract property links
        property_links = parser.extract_property_links_from_list(page_source)
        
        print(f"Found {len(property_links)} property links")
        for i, link in enumerate(property_links[:5]):  # Show first 5
            print(f"  {i+1}. {link}")
        
        if len(property_links) == 0:
            print("❌ No property links found. Let me check the HTML structure...")
            
            # Look for any links that might be property links
            import re
            all_links = re.findall(r'href="([^"]*)"', page_source)
            pr_links = [link for link in all_links if '/pr/' in link]
            print(f"Found {len(pr_links)} links with /pr/ pattern:")
            for i, link in enumerate(pr_links[:10]):
                print(f"  {i+1}. {link}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        selenium.close()

if __name__ == "__main__":
    test_property_listings_selenium()
