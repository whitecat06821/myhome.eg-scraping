#!/usr/bin/env python3
"""
Test script for property listings API
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.fetcher import MyHomeFetcher
import json

def test_property_listings_api():
    """Test the property listings API"""
    fetcher = MyHomeFetcher()
    
    print("Testing property listings API...")
    
    # Test the API endpoint
    api_data = fetcher.fetch_property_listings_api(page=1)
    
    if api_data:
        print("✅ API call successful!")
        print(f"Response keys: {list(api_data.keys())}")
        print(f"Response data: {json.dumps(api_data, indent=2)}")
    else:
        print("❌ API call failed")
    
    fetcher.close()

if __name__ == "__main__":
    test_property_listings_api()
