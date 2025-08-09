#!/usr/bin/env python3
"""
Test script for property listings API endpoints
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.fetcher import MyHomeFetcher
import json

def test_property_api_endpoints():
    """Test different API endpoints for property listings"""
    fetcher = MyHomeFetcher()
    
    # Test different API endpoints
    endpoints = [
        "/statements",
        "/statements/rent",
        "/statements/sale", 
        "/statements/list",
        "/properties",
        "/properties/rent",
        "/properties/sale"
    ]
    
    for endpoint in endpoints:
        print(f"\nTesting endpoint: {endpoint}")
        try:
            url = f"{fetcher.base_url}{endpoint}"
            params = {'page': 1, 'limit': 10}
            
            response = fetcher.session.get(url, params=params, headers=fetcher.headers, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ Success! Response keys: {list(data.keys())}")
                    print(f"Data preview: {json.dumps(data, indent=2)[:500]}...")
                except Exception as e:
                    print(f"❌ JSON parse error: {e}")
                    print(f"Response text: {response.text[:200]}...")
            else:
                print(f"❌ Failed with status {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    fetcher.close()

if __name__ == "__main__":
    test_property_api_endpoints()
