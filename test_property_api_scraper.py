#!/usr/bin/env python3
"""
Test script for property API scraper
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.fetcher import MyHomeFetcher
from scraper.parser import MyHomeParser

def test_property_api_scraper():
    """Test the property API scraper"""
    fetcher = MyHomeFetcher()
    parser = MyHomeParser()
    
    print("Testing property API scraper...")
    
    # Test fetching property listings from API
    api_data = fetcher.fetch_property_listings_api(page=1)
    
    if api_data:
        print("✅ API call successful!")
        
        # Parse the properties
        properties = parser.parse_property_listings_api_response(api_data)
        
        print(f"Found {len(properties)} properties")
        
        for i, property_info in enumerate(properties[:5]):  # Show first 5
            print(f"  {i+1}. {property_info}")
        
        if len(properties) > 0:
            print("✅ Property API scraper is working!")
        else:
            print("❌ No properties found in API response")
    else:
        print("❌ API call failed")
    
    fetcher.close()

if __name__ == "__main__":
    test_property_api_scraper()
